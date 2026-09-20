package ru.itmo.movie.persistence;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.persistence.*;
import java.util.Map;
import java.util.function.Function;
import ru.itmo.movie.domain.AppState;

/** Each request owns its EntityManager; the database row serializes all mutations. */
@ApplicationScoped
public class Database {
 private EntityManagerFactory factory;
 public static String config(String key,String fallback) {
  return System.getProperty(key,System.getenv().getOrDefault(key,fallback));
 }
 @PostConstruct public void init() {
  factory=Persistence.createEntityManagerFactory("movies",Map.of(
   "jakarta.persistence.jdbc.driver","org.postgresql.Driver",
   "jakarta.persistence.jdbc.url",config("MOVIE_DB_URL","jdbc:postgresql://127.0.0.1:55441/movie_lab"),
   "jakarta.persistence.jdbc.user",config("MOVIE_DB_USER","movie_lab"),
   "jakarta.persistence.jdbc.password",config("MOVIE_DB_PASSWORD","")));
 }
 public <T> T read(Function<EntityManager,T> work) {
  try(EntityManager em=factory.createEntityManager()) { return work.apply(em); }
 }
 public <T> T write(Function<EntityManager,T> work) {
  try(EntityManager em=factory.createEntityManager()) {
   EntityTransaction tx=em.getTransaction(); tx.begin();
   try {
    AppState state=em.find(AppState.class,1L,LockModeType.PESSIMISTIC_WRITE,Map.of("jakarta.persistence.lock.timeout",10000));
    if(state==null) throw new IllegalStateException("Сначала выполните database/schema.sql");
    T result=work.apply(em); state.revision++; em.flush(); tx.commit(); return result;
   } catch(RuntimeException e) { if(tx.isActive()) tx.rollback(); throw e; }
  }
 }
 @PreDestroy public void close() { if(factory!=null) factory.close(); }
}
