package ru.itmo.movie.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.*;
import jakarta.validation.*;
import java.lang.reflect.Field;
import java.time.ZonedDateTime;
import java.util.*;
import java.util.stream.Collectors;
import ru.itmo.movie.domain.*;
import ru.itmo.movie.persistence.Database;

@ApplicationScoped
public class MovieService {
 @Inject Database db;
 private static final ValidatorFactory VF=Validation.buildDefaultValidatorFactory();
 private static final Map<String,Class<?>> TYPES=Map.of("movies",Movie.class,"people",Person.class,"coordinates",Coordinates.class,"locations",Location.class);
 private static final Map<String,String> COLUMNS=Map.of("name","m.name","tagline","m.tagline","genre","m.genre","mpaaRating","m.mpaaRating","director","d.name","screenwriter","s.name","operator","o.name");
 public MovieService() {}
 public MovieService(Database db) { this.db=db; }
 private Class<?> type(String kind) { Class<?> t=TYPES.get(kind); if(t==null) throw new Problem(404,"Неизвестный раздел"); return t; }
 private <T> T required(EntityManager em,Class<T> type,long id) {
  T value=em.find(type,id); if(value==null) throw new Problem(404,"Объект "+type.getSimpleName()+" #"+id+" не найден"); return value;
 }
 public long revision() { return db.read(em->required(em,AppState.class,1L).revision); }
 public Object get(String kind,long id) { return db.read(em->required(em,type(kind),id)); }
 public List<?> all(String kind) { return db.read(em->em.createQuery("SELECT e FROM "+type(kind).getSimpleName()+" e ORDER BY e.id").getResultList()); }
 public Map<String,Object> page(int page,int size,String filter,String value,String sort,boolean descending) {
  if(page<0||size<1||size>100) throw new Problem(400,"page ≥ 0; размер страницы от 1 до 100");
  if(!COLUMNS.containsKey(filter)||!(COLUMNS.containsKey(sort)||sort.equals("id"))) throw new Problem(400,"Неизвестная колонка");
  return db.read(em->{
   String where=value==null?"":" WHERE "+COLUMNS.get(filter)+" = :value";
   String order=sort.equals("id")?"m.id":COLUMNS.get(sort);
   String joins=" LEFT JOIN m.director d LEFT JOIN m.screenwriter s LEFT JOIN m.operator o";
   TypedQuery<Movie> q=em.createQuery("SELECT m FROM Movie m"+joins+where+" ORDER BY "+order+(descending?" DESC":" ASC")+(sort.equals("id")?"":", m.id ASC"),Movie.class);
   TypedQuery<Long> count=em.createQuery("SELECT COUNT(m) FROM Movie m"+joins+where,Long.class);
   if(value!=null) { Object v=filter.equals("genre")?parseEnum(MovieGenre.class,value):filter.equals("mpaaRating")?parseEnum(MpaaRating.class,value):value; q.setParameter("value",v);count.setParameter("value",v); }
   long total=count.getSingleResult();
   int safePage=(int)Math.min(page,Math.max(0,(total-1)/size));
   return Map.of("items",q.setFirstResult(Math.multiplyExact(safePage,size)).setMaxResults(size).getResultList(),"total",total,"page",safePage,"size",size);
  });
 }
 private static <E extends Enum<E>> E parseEnum(Class<E> type,String value) { try{return Enum.valueOf(type,value);}catch(IllegalArgumentException e){throw new Problem(400,"Недопустимое значение "+type.getSimpleName());} }
 /** A strict allow-list is derived from the domain fields; references use existing IDs. */
 public Object save(String kind,Long id,Map<String,Object> input) {
  Class<?> t=type(kind);
  return db.write(em->{
   Object entity;
   try {
    entity=id==null?t.getDeclaredConstructor().newInstance():required(em,t,id);
    if(id!=null) {
     Object expected=input.get("version");
     if(expected==null||Long.parseLong(expected.toString())!=t.getField("version").getLong(entity)) throw new Problem(409,"Объект изменён другим пользователем. Откройте форму заново.");
    }
    for(String key:input.keySet()) {
     if(key.equals("version")&&id!=null) continue;
     if(key.equals("id")||key.equals("version")||key.equals("creationDate")) throw new Problem(400,"Поле "+key+" формируется автоматически");
     Field field;
     try{field=t.getField(key);}catch(NoSuchFieldException e){throw new Problem(400,"Неизвестное поле: "+key);}
     Object raw=input.get(key); Class<?> ft=field.getType(); Object v=null;
     if(raw!=null) {
      String s=raw.toString();
      try {
       if(ft==String.class) { if(!(raw instanceof String)) throw new IllegalArgumentException(); v=raw; }
       else if(ft==Integer.class||ft==int.class) v=Integer.valueOf(s);
       else if(ft==Long.class||ft==long.class) v=Long.valueOf(s);
       else if(ft==Double.class) { double n=Double.parseDouble(s);if(!Double.isFinite(n))throw new IllegalArgumentException();v=n; }
       else if(ft==Float.class) { float n=Float.parseFloat(s);if(!Float.isFinite(n))throw new IllegalArgumentException();v=n; }
       else if(ft==ZonedDateTime.class) v=ZonedDateTime.parse(s);
       else if(ft.isEnum()) { v=Enum.valueOf(ft.asSubclass(Enum.class),s); }
       else v=required(em,ft,Long.parseLong(s));
      } catch(IllegalArgumentException|java.time.DateTimeException e) { throw new Problem(400,"Некорректное поле "+key+": проверьте формат и диапазон"); }
     }
     if(v==null&&ft.isPrimitive()) throw new Problem(400,"Поле "+key+" обязательно");
     field.set(entity,v);
    }
    // Creation date is assigned by PostgreSQL; set a temporary value for Bean Validation.
    if(entity instanceof Movie m&&id==null) m.creationDate=java.time.LocalDate.now();
    var violations=VF.getValidator().validate(entity);
    if(!violations.isEmpty()) throw new Problem(400,violations.stream().map(v->v.getPropertyPath()+": "+validationMessage(v)).sorted().collect(Collectors.joining("; ")));
    if(entity instanceof Person p) {
     var query=em.createQuery("SELECT COUNT(p) FROM Person p WHERE p.passportID=:p"+(id==null?"":" AND p.id<>:id"),Long.class).setParameter("p",p.passportID);
     if(id!=null)query.setParameter("id",id);
     Long duplicates=query.getSingleResult();
     if(duplicates>0) throw new Problem(409,"passportID: паспорт уже существует");
    }
    if(id==null) em.persist(entity); em.flush(); em.refresh(entity); return entity;
   } catch(ReflectiveOperationException e) { throw new IllegalStateException(e); }
  });
 }
 public int delete(String kind,long id,long version) {
  return db.write(em->{
   Object entity=required(em,type(kind),id);
   try {if(type(kind).getField("version").getLong(entity)!=version) throw new Problem(409,"Объект изменён. Обновите данные перед удалением.");}catch(ReflectiveOperationException e){throw new IllegalStateException(e);}
   int deleted=0;
   if(entity instanceof Location) {
    List<Person> people=em.createQuery("SELECT p FROM Person p WHERE p.location.id=:id",Person.class).setParameter("id",id).getResultList();
    for(Person p:people){ deleted+=deletePerson(em,p); }
   } else if(entity instanceof Person p) deleted+=deletePersonMovies(em,p.id);
   else if(entity instanceof Coordinates) { for(Movie m:em.createQuery("SELECT m FROM Movie m WHERE m.coordinates.id=:id",Movie.class).setParameter("id",id).getResultList()){em.remove(m);deleted++;} }
   em.remove(entity); return deleted+1;
  });
 }
 private int deletePerson(EntityManager em,Person p) {int n=deletePersonMovies(em,p.id);em.remove(p);em.flush();return n+1;}
 private int deletePersonMovies(EntityManager em,long id) {
  List<Movie> movies=em.createQuery("SELECT m FROM Movie m WHERE m.director.id=:id OR m.screenwriter.id=:id OR m.operator.id=:id",Movie.class).setParameter("id",id).getResultList();
  movies.forEach(em::remove);em.flush();return movies.size();
 }
 public int deleteByBoxOffice(int amount) {if(amount<=0)throw new Problem(400,"usaBoxOffice должен быть > 0");return db.write(em->{var rows=em.createQuery("SELECT m FROM Movie m WHERE m.usaBoxOffice=:v",Movie.class).setParameter("v",amount).getResultList();rows.forEach(em::remove);return rows.size();});}
 public Double average() {return db.read(em->em.createQuery("SELECT AVG(m.usaBoxOffice) FROM Movie m",Double.class).getSingleResult());}
 public List<Movie> prefix(String prefix) {
  if(prefix==null) throw new Problem(400,"Укажите префикс");
  // Escape LIKE metacharacters: the input is a literal prefix, never a pattern.
  String escaped=prefix.replace("!","!!").replace("%","!%").replace("_","!_");
  return db.read(em->em.createQuery("SELECT m FROM Movie m WHERE m.tagline LIKE :p ESCAPE '!' ORDER BY m.id",Movie.class).setParameter("p",escaped+"%").getResultList());
 }
 public Map<String,Object> redistribute(MovieGenre from,MovieGenre to) {
  if(from==null||to==null||from==to) throw new Problem(400,"Выберите два разных жанра");
  return db.write(em->{
   List<Movie> source=em.createQuery("SELECT m FROM Movie m WHERE m.genre=:g ORDER BY m.id",Movie.class).setParameter("g",from).getResultList();
   List<Movie> target=em.createQuery("SELECT m FROM Movie m WHERE m.genre=:g ORDER BY m.id",Movie.class).setParameter("g",to).getResultList();
   if(source.isEmpty()||target.isEmpty()) throw new Problem(400,"Оба жанра должны содержать фильмы");
   long pool=source.stream().mapToLong(m->m.oscarsCount-1L).sum(); long each=pool/target.size(),rest=pool%target.size();
   for(int i=0;i<target.size();i++) {Movie m=target.get(i);m.oscarsCount=checkedOscars(m.oscarsCount+each+(i<rest?1:0));}
   source.forEach(m->m.oscarsCount=1);
   return Map.of("transferred",pool,"recipients",target.size(),"each",each,"remainder",rest);
  });
 }
 public int award(int minLength,int count) {
  if(minLength<0||count<=0)throw new Problem(400,"Порог ≥ 0, число наград > 0");
  return db.write(em->{var movies=em.createQuery("SELECT m FROM Movie m WHERE m.length>:n",Movie.class).setParameter("n",minLength).getResultList();for(Movie m:movies)m.oscarsCount=checkedOscars((long)m.oscarsCount+count);return movies.size();});
 }
 private static int checkedOscars(long value) {if(value>Integer.MAX_VALUE)throw new Problem(400,"Переполнение oscarsCount: операция отменена целиком");return (int)value;}
 private static String validationMessage(ConstraintViolation<?> v) {
  return switch(v.getConstraintDescriptor().getAnnotation().annotationType().getSimpleName()) {
   case "NotNull" -> "обязательное поле";case "Positive" -> "значение должно быть больше 0";
   case "Size" -> "строка не должна быть пустой";case "Max" -> "значение не должно превышать 826";
   case "DecimalMax","DecimalMin" -> "значение должно быть конечным числом в допустимом диапазоне";
   default -> v.getMessage();
  };
 }
}
