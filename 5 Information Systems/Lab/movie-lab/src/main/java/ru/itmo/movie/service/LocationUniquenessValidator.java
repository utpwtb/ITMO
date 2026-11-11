package ru.itmo.movie.service;

import jakarta.persistence.EntityManager;
import ru.itmo.movie.domain.Location;

import java.util.Objects;
import java.util.Optional;

/** Look up location keys under the AppState write lock. */
final class LocationUniquenessValidator {
    private LocationUniquenessValidator() {
    }

    static void check(EntityManager em, Location location) {
        if (findOther(em, location).isPresent())
            throw new Problem(409, "DUPLICATE_LOCATION", "Место с таким названием и координатами уже существует");
    }

    static Optional<Location> findOther(EntityManager em, Location location) {
        return em.createQuery("SELECT l FROM Location l WHERE l.x = :x AND l.y = :y ORDER BY l.id", Location.class)
                .setParameter("x", location.x)
                .setParameter("y", location.y)
                .getResultList().stream()
                .filter(other -> !Objects.equals(other.id, location.id) && sameKey(other, location))
                .findFirst();
    }

    static boolean sameKey(Location a, Location b) {
        return a == b || (a != null && b != null
                && a.name.equals(b.name) && a.x.equals(b.x) && a.y.doubleValue() == b.y.doubleValue());
    }
}
