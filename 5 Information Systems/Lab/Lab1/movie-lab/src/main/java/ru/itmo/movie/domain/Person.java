package ru.itmo.movie.domain;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
@Entity @Table(name="person")
public class Person {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Positive
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public Long id;
 @Version @Column(nullable=false) public long version;
 @NotNull @Size(min=1) @Column(nullable=false, columnDefinition="text")
 public String name;
 @Enumerated(EnumType.STRING)
 public Color eyeColor;
 @Enumerated(EnumType.STRING)
 public Color hairColor;
 @ManyToOne @JoinColumn(name="location_id")
 public Location location;
 @NotNull @Convert(converter=ZonedTimeConverter.class) @Column(nullable=false, columnDefinition="text")
 public java.time.ZonedDateTime birthday;
 @Positive @DecimalMax("3.4028235E38")
 public Float height;
 @Positive @DecimalMax("3.4028235E38")
 public Float weight;
 @NotNull @Column(nullable=false, unique=true, columnDefinition="text")
 public String passportID;
}
