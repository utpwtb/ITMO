package ru.itmo.movie.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import java.util.*;
import ru.itmo.movie.domain.*;
import ru.itmo.movie.persistence.Database;

@ApplicationScoped
public class ImportHistoryService {
    @Inject Database db;
    public ImportHistoryService() {}
    public ImportHistoryService(Database db) { this.db = db; }

    public static AppUser account(EntityManager em, String username) {
        return em.createQuery("SELECT u FROM AppUser u WHERE u.username=:name", AppUser.class)
                .setParameter("name", username).getResultStream().findFirst().orElseThrow(() -> new Problem(401,"AUTH_REQUIRED","Войдите в систему"));
    }
    public static Map<String,Object> dto(ImportOperation op) {
        Map<String,Object> row = new LinkedHashMap<>();
        row.put("id", op.id.toString()); row.put("operationId", op.id.toString());
        row.put("userId",op.user.id.toString()); row.put("user",op.user.username);
        row.put("status",op.status.name()); row.put("addedCount",op.status == ImportStatus.SUCCESS ? op.addedCount : null);
        row.put("startedAt",op.startedAt.toString()); row.put("finishedAt",op.finishedAt == null ? null : op.finishedAt.toString());
        row.put("filename",op.filename); row.put("errorCode",op.errorCode); row.put("errorMessage",op.errorMessage);
        return row;
    }
    public Map<String,Object> list(String user, int page, int size) {
        if (page < 0 || size < 1 || size > 100 || (long)page*size > Integer.MAX_VALUE) throw new Problem(400,"Неверная страница");
        return db.read(em -> {
            AppUser actor = account(em,user);
            String where = actor.role == UserRole.ADMIN ? "" : " WHERE o.user.id=:user";
            var q = em.createQuery("SELECT o FROM ImportOperation o" + where + " ORDER BY o.startedAt DESC, o.id DESC",ImportOperation.class);
            var count = em.createQuery("SELECT COUNT(o) FROM ImportOperation o" + where,Long.class);
            if (actor.role != UserRole.ADMIN) { q.setParameter("user",actor.id); count.setParameter("user",actor.id); }
            return Map.of("items",q.setFirstResult(page*size).setMaxResults(size).getResultStream().map(ImportHistoryService::dto).toList(),"total",count.getSingleResult(),"page",page,"size",size);
        });
    }
    public Map<String,Object> get(String user, long id) {
        return db.read(em -> {
            AppUser actor = account(em,user);
            ImportOperation op = em.find(ImportOperation.class,id);
            if (op == null || (actor.role != UserRole.ADMIN && !op.user.id.equals(actor.id))) throw new Problem(404,"NOT_FOUND","Операция не найдена");
            return dto(op);
        });
    }
}
