package ru.itmo.movie.domain;

import jakarta.persistence.*;

/** Credentials are never returned by the REST API. */
@Entity
@Table(name = "app_user")
public class AppUser {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;

    @Column(nullable = false, unique = true, length = 64)
    public String username;

    @Column(name = "password_hash", nullable = false, length = 64)
    public String passwordHash;

    @Column(nullable = false, length = 32)
    public String salt;

    @Column(nullable = false)
    public int iterations;
}
