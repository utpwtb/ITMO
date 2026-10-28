package ru.itmo.movie.service;

import jakarta.persistence.EntityManager;
import ru.itmo.movie.domain.Movie;

/** Called only while the AppState write lock is held. No database UNIQUE rule. */
public final class MovieUniquenessValidator {
    private MovieUniquenessValidator() {}
    public record MovieKey(String name, Long directorIdOrNull) {}

    public static void check(EntityManager em, Movie movie) {
        MovieKey key = new MovieKey(movie.name, movie.director == null ? null : movie.director.id);
        String director = movie.director == null ? "m.director IS NULL" : "m.director.id=:director";
        var query = em.createQuery("SELECT m FROM Movie m WHERE " + director, Movie.class);
        if (movie.director != null) query.setParameter("director", movie.director.id);
        // Java String.equals preserves exact comparison even under nondeterministic DB collation.
        boolean duplicate = query.getResultStream().anyMatch(m -> !java.util.Objects.equals(m.id, movie.id)
                && key.equals(new MovieKey(m.name, m.director == null ? null : m.director.id)));
        if (duplicate) throw new Problem(409, "DUPLICATE_MOVIE", "Название и режиссёр: такая комбинация уже существует");
    }
}
