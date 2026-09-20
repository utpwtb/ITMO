package ru.itmo.movie.domain;
import jakarta.persistence.*;
import java.time.ZonedDateTime;
@Converter
public class ZonedTimeConverter implements AttributeConverter<ZonedDateTime,String> {
 public String convertToDatabaseColumn(ZonedDateTime value) { return value==null?null:value.toString(); }
 public ZonedDateTime convertToEntityAttribute(String value) { return value==null?null:ZonedDateTime.parse(value); }
}
