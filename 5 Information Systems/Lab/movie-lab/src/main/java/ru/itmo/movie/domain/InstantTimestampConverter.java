package ru.itmo.movie.domain;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;
import java.sql.Timestamp;
import java.time.Instant;

@Converter
public class InstantTimestampConverter implements AttributeConverter<Instant, Timestamp> {
    public Timestamp convertToDatabaseColumn(Instant value) { return value == null ? null : Timestamp.from(value); }
    public Instant convertToEntityAttribute(Timestamp value) { return value == null ? null : value.toInstant(); }
}
