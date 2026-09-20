package ru.itmo.movie.domain;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
@Entity @Table(name="location")
public class Location {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Positive
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public Long id;
 @Version @Column(nullable=false) public long version;
 @NotNull @Column(nullable=false)
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public Long x;
 @NotNull @DecimalMin("-1.7976931348623157E308") @DecimalMax("1.7976931348623157E308") @Column(nullable=false)
 public Double y;
 @NotNull @Column(nullable=false, columnDefinition="text")
 public String name;
}
