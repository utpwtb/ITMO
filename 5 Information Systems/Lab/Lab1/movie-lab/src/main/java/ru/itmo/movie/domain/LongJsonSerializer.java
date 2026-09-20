package ru.itmo.movie.domain;
import jakarta.json.bind.serializer.*;
import jakarta.json.stream.JsonGenerator;
/** Decimal strings preserve the complete Java Long range in JavaScript clients. */
public class LongJsonSerializer implements JsonbSerializer<Long> {
 public void serialize(Long value,JsonGenerator generator,SerializationContext context){generator.write(value.toString());}
}
