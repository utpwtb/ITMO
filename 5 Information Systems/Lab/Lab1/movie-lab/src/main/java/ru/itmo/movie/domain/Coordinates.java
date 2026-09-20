package ru.itmo.movie.domain;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
@Entity @Table(name="coordinates")
public class Coordinates {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Positive
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public Long id;
 @Version @Column(nullable=false) public long version;
 @NotNull @Max(826) @Column(nullable=false)
 public Integer x;
 @NotNull @Column(nullable=false)
 public Integer y;
}
