package ru.itmo.movie.service;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import ru.itmo.movie.domain.AppUser;
import ru.itmo.movie.persistence.Database;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

@ApplicationScoped
public class AuthService {
    private static final int ITERATIONS = 600_000;
    private static final SecureRandom RANDOM = new SecureRandom();

    @Inject
    Database db;

    public AuthService() {}

    public AuthService(Database db) {
        this.db = db;
    }

    private static AppUser find(EntityManager em, String username) {
        return em.createQuery("SELECT u FROM AppUser u WHERE u.username=:name", AppUser.class)
                .setParameter("name", username).getResultStream().findFirst().orElse(null);
    }

    private static String username(String value) {
        String name = value == null ? "" : value.strip();
        if (!name.matches("[\\p{L}\\p{N}_.-]{3,64}"))
            throw new Problem(400, "Имя пользователя: от 3 до 64 букв, цифр или символов _ . -");
        return name;
    }

    private static byte[] hash(String password, byte[] salt, int iterations) {
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, 256);
        try {
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("Не удалось обработать пароль", e);
        } finally {
            spec.clearPassword();
        }
    }

    private static AppUser credentials(String name, String password) {
        byte[] salt = new byte[16];
        RANDOM.nextBytes(salt);
        AppUser user = new AppUser();
        user.username = name;
        user.iterations = ITERATIONS;
        user.salt = Base64.getEncoder().encodeToString(salt);
        user.passwordHash = Base64.getEncoder().encodeToString(hash(password, salt, user.iterations));
        return user;
    }

    /** Seed once; restarting or changing environment variables never resets an existing password. */
    @PostConstruct
    public void seedDefaultAccount() {
        String name = username(Database.config("MOVIE_USER", "student"));
        if (db.read(em -> find(em, name)) != null) return;
        AppUser candidate = credentials(name, Database.config("MOVIE_PASSWORD", "student"));
        db.write(em -> {
            if (find(em, name) == null) em.persist(candidate);
            return null;
        });
    }

    public String register(String value, String password) {
        String name = username(value);
        if (password == null || password.length() < 8 || password.length() > 128)
            throw new Problem(400, "Пароль должен содержать от 8 до 128 символов");
        AppUser candidate = credentials(name, password);
        return db.write(em -> {
            if (find(em, name) != null) throw new Problem(409, "Это имя пользователя уже занято");
            em.persist(candidate);
            return name;
        });
    }

    public String authenticate(String value, String password) {
        String name = value == null ? "" : value.strip();
        if (name.length() > 64 || password == null || password.length() > 128)
            throw new Problem(401, "Неверное имя пользователя или пароль");
        AppUser user = db.read(em -> find(em, name));
        if (user == null || !MessageDigest.isEqual(Base64.getDecoder().decode(user.passwordHash),
                hash(password, Base64.getDecoder().decode(user.salt), user.iterations)))
            throw new Problem(401, "Неверное имя пользователя или пароль");
        return user.username;
    }
}
