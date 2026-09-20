package ru.itmo.movie.domain;
import jakarta.persistence.*;
@Entity @Table(name="app_state")
public class AppState { @Id public Long id; public long revision; }
