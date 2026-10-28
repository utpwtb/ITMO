package ru.itmo.movie.persistence;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.persistence.*;

import java.util.Map;
import java.util.function.Function;

import ru.itmo.movie.domain.AppState;

/**
 * Each request owns its EntityManager; the database row serializes all mutations.
 */
@ApplicationScoped
public class Database {
    private EntityManagerFactory factory;

    public static String config(String key, String fallback) {
        return System.getProperty(key, System.getenv().getOrDefault(key, fallback));
    }

    @PostConstruct
    public void init() {
        factory = Persistence.createEntityManagerFactory(config("MOVIE_PERSISTENCE_UNIT", "movies"), Map.of(
                "jakarta.persistence.jdbc.driver", "org.postgresql.Driver",
                "jakarta.persistence.jdbc.url", config("MOVIE_DB_URL", "jdbc:postgresql://127.0.0.1:55441/movie_lab"),
                "jakarta.persistence.jdbc.user", config("MOVIE_DB_USER", "movie_lab"),
                "jakarta.persistence.jdbc.password", config("MOVIE_DB_PASSWORD", "")));
    }

    public <T> T read(Function<EntityManager, T> work) {
        try (EntityManager em = factory.createEntityManager()) {
            return work.apply(em);
        }
    }

    public <T> T write(Function<EntityManager, T> work) {
        return transaction(work, true);
    }

    /** History/account metadata commits independently, without changing the movie revision. */
    public <T> T metadata(Function<EntityManager, T> work) {
        return transaction(work, false);
    }

    public static String sqlState(Throwable error) {
        for (Throwable t = error; t != null; t = t.getCause())
            if (t instanceof java.sql.SQLException s) return s.getSQLState();
        return null;
    }

    private <T> T transaction(Function<EntityManager, T> work, boolean domain) {
        String isolation = config("MOVIE_ISOLATION", "READ COMMITTED");
        if (!isolation.equals("READ COMMITTED") && !isolation.equals("SERIALIZABLE"))
            throw new IllegalArgumentException("Unsupported isolation");
        int attempts = Integer.parseInt(config("MOVIE_TX_ATTEMPTS", "3"));
        for (int attempt = 1; ; attempt++) {
            try { return once(work, domain, isolation); }
            catch (RuntimeException error) {
                if (!"40001".equals(sqlState(error)) || attempt >= attempts) throw error;
                java.util.logging.Logger.getLogger(Database.class.getName()).info("Rolled-back serialization failure; retry=" + attempt);
            }
        }
    }

    private <T> T once(Function<EntityManager, T> work, boolean domain, String isolation) {
        try (EntityManager em = factory.createEntityManager()) {
            EntityTransaction tx = em.getTransaction();
            tx.begin();
            try {
                em.createNativeQuery("SET TRANSACTION ISOLATION LEVEL " + (domain ? isolation : "READ COMMITTED")).executeUpdate();
                int timeout = Integer.parseInt(config("MOVIE_LOCK_TIMEOUT_MS", "10000"));
                if (timeout < 1) throw new IllegalArgumentException("lock timeout must be positive");
                em.createNativeQuery("SET LOCAL lock_timeout = '" + timeout + "ms'").executeUpdate();
                AppState state = domain ? em.find(AppState.class, 1L, LockModeType.PESSIMISTIC_WRITE) : null;
                if (domain && state == null) throw new IllegalStateException("Сначала выполните database/schema.sql");
                T result = work.apply(em);
                if (domain) state.revision++;
                em.flush();
                tx.commit();
                return result;
            } catch (RuntimeException e) {
                if (tx.isActive()) {
                    try { tx.rollback(); } catch (RuntimeException rollback) { e.addSuppressed(rollback); }
                }
                throw e;
            }
        }
    }

    @PreDestroy
    public void close() {
        if (factory != null) factory.close();
    }
}
