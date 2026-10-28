package ru.itmo.movie.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.*;
import java.util.logging.*;
import ru.itmo.movie.domain.*;
import ru.itmo.movie.persistence.Database;

@ApplicationScoped
public class ImportService {
    private static final Logger LOG = Logger.getLogger(ImportService.class.getName());
    @Inject Database db;
    @Inject MovieService movies;
    public ImportService() {}
    public ImportService(Database db, MovieService movies) { this.db=db; this.movies=movies; }

    public Map<String,Object> upload(String user, String filename, byte[] bytes) {
        if (bytes.length == 0) throw new Problem(400,"MISSING_FILE","Выберите непустой JSON-файл");
        if (bytes.length > ImportParser.maxBytes()) throw new Problem(413,"FILE_TOO_LARGE","Файл превышает допустимый размер");
        String safeName = filename.replace('\\','/');
        safeName = safeName.substring(safeName.lastIndexOf('/')+1).replaceAll("[\\p{Cntrl}]", "");
        final String name = safeName.substring(0,Math.min(safeName.length(),255));
        long operation = db.metadata(em -> {
            ImportOperation op = new ImportOperation();
            op.user = ImportHistoryService.account(em,user); op.filename=name;
            em.persist(op); em.flush(); return op.id;
        });
        try {
            new ImportParser().parse(bytes);
            return db.write(em -> {
                // Reparse on each confirmed serialization rollback: no managed entities/IDs survive retries.
                List<Movie> rows = new ImportParser().parse(bytes).movies();
                Map<String,Person> people = new HashMap<>();
                for (int i=0;i<rows.size();i++) {
                    Movie m=rows.get(i);
                    try {
                        m.director=personAt(em,m.director,people,i,"director");
                        m.screenwriter=personAt(em,m.screenwriter,people,i,"screenwriter");
                        m.operator=personAt(em,m.operator,people,i,"operator");
                        em.persist(m.coordinates);
                        movies.saveImported(em,m);
                    } catch (Problem p) {
                        if (p.recordNumber != null) throw p;
                        String field = p.code.equals("PERSON_DATA_CONFLICT") ? "person" : "director";
                        throw p.at(i+1,"movies["+i+"]."+field);
                    }
                }
                ImportOperation op=em.find(ImportOperation.class,operation,LockModeType.PESSIMISTIC_WRITE);
                if (op.status != ImportStatus.RUNNING) throw new IllegalStateException("Unexpected import terminal status");
                op.status=ImportStatus.SUCCESS; op.addedCount=rows.size(); op.finishedAt=Instant.now();
                em.flush();
                return ImportHistoryService.dto(op);
            });
        } catch (RuntimeException error) {
            LOG.log(Level.WARNING,"Import operation="+operation+" failed",error);
            ImportOperation actual;
            try { actual=db.read(em -> em.find(ImportOperation.class,operation)); }
            catch (RuntimeException unavailable) { throw pending(operation); }
            if (actual != null && actual.status == ImportStatus.SUCCESS)
                return new ImportHistoryService(db).get(user,operation);
            String state=Database.sqlState(error);
            if ((state != null && state.startsWith("08")) || error.getSuppressed().length>0) throw pending(operation);
            Problem failure = error instanceof Problem p ? p : databaseProblem(error);
            try {
                db.metadata(em -> {
                    ImportOperation op=em.find(ImportOperation.class,operation,LockModeType.PESSIMISTIC_WRITE);
                    if (op.status == ImportStatus.RUNNING) {
                        op.status=ImportStatus.FAILED; op.addedCount=null; op.finishedAt=Instant.now();
                        op.errorCode=failure.code;
                        op.errorMessage=failure.getMessage().substring(0,Math.min(1000,failure.getMessage().length()));
                    }
                    return null;
                });
            } catch (RuntimeException historyFailure) {
                LOG.log(Level.SEVERE,"Cannot finalize import="+operation,historyFailure);
                throw pending(operation);
            }
            failure.operationId=operation;
            throw failure;
        }
    }

    private Problem pending(long id) {
        Problem p=new Problem(503,"COMMIT_OUTCOME_UNKNOWN","Проверьте историю операции; не повторяйте загрузку автоматически");
        p.operationId=id; p.operationStatus="RUNNING"; return p;
    }

    public static Problem databaseProblem(Throwable error) {
        String state=Database.sqlState(error);
        if (state != null && (state.startsWith("08") || Set.of("55P03","57014","40001","40P01","53300","57P01").contains(state)))
            return new Problem(503,"DATABASE_TEMPORARY","База данных временно недоступна или превышено время ожидания блокировки");
        if ("23505".equals(state)) return new Problem(409,"EXISTING_UNIQUE_CONFLICT","Конфликт существующего уникального поля");
        if (error instanceof OptimisticLockException) return new Problem(409,"VERSION_CONFLICT","Объект изменён другим пользователем");
        return new Problem(500,"INTERNAL_ERROR","Внутренняя ошибка сервера; операция отменена");
    }

    private Person person(EntityManager em, Person input, Map<String,Person> cache) {
        if (input == null) return null;
        Person existing=cache.get(input.passportID);
        if (existing == null) existing=em.createQuery("SELECT p FROM Person p WHERE p.passportID=:passport",Person.class)
                .setParameter("passport",input.passportID).getResultStream().findFirst().orElse(null);
        if (existing != null) {
            if (!samePerson(input,existing)) throw new Problem(409,"PERSON_DATA_CONFLICT","passportID: данные человека отличаются от сохранённых");
            cache.put(input.passportID,existing); return existing;
        }
        if (input.location != null) em.persist(input.location);
        em.persist(input); cache.put(input.passportID,input); return input;
    }

    private Person personAt(EntityManager em, Person input, Map<String,Person> cache, int index, String role) {
        try { return person(em,input,cache); }
        catch (Problem problem) { throw problem.at(index+1,"movies["+index+"]."+role); }
    }

    private static boolean samePerson(Person a,Person b) {
        return Objects.equals(a.name,b.name) && Objects.equals(a.eyeColor,b.eyeColor) && Objects.equals(a.hairColor,b.hairColor)
                && Objects.equals(a.birthday,b.birthday) && Objects.equals(a.height,b.height) && Objects.equals(a.weight,b.weight)
                && Objects.equals(a.passportID,b.passportID) && sameLocation(a.location,b.location);
    }
    private static boolean sameLocation(Location a,Location b) {
        return a==null ? b==null : b!=null && Objects.equals(a.x,b.x) && Objects.equals(a.y,b.y) && Objects.equals(a.name,b.name);
    }
}
