package ru.itmo.movie.domain;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "import_operation")
public class ImportOperation {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    @ManyToOne(optional = false) @JoinColumn(name = "user_id", nullable = false)
    public AppUser user;
    @Enumerated(EnumType.STRING) @Column(nullable = false)
    public ImportStatus status = ImportStatus.RUNNING;
    @Column(name = "added_count") public Integer addedCount;
    @Convert(converter = InstantTimestampConverter.class)
    @Column(name = "started_at", nullable = false) public Instant startedAt = Instant.now();
    @Convert(converter = InstantTimestampConverter.class)
    @Column(name = "finished_at") public Instant finishedAt;
    @Column(nullable = false, length = 255) public String filename;
    @Column(name = "error_code", length = 64) public String errorCode;
    @Column(name = "error_message", length = 1000) public String errorMessage;
}
