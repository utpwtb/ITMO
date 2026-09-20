package ru.itmo.movie.domain;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
@Entity @Table(name="movie")
public class Movie {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Positive
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public Long id;
 @Version @Column(nullable=false) public long version;
 @NotNull @Size(min=1) @Column(nullable=false, columnDefinition="text")
 public String name;
 @NotNull @ManyToOne(optional=false) @JoinColumn(name="coordinates_id",nullable=false)
 public Coordinates coordinates;
 @NotNull @Column(nullable=false,insertable=false,updatable=false)
 public java.time.LocalDate creationDate;
 @Positive @Column(nullable=false)
 public int oscarsCount;
 @Positive @Column(nullable=false)
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public long budget;
 @Positive @DecimalMax("1.7976931348623157E308")
 public Double totalBoxOffice;
 @NotNull @Enumerated(EnumType.STRING) @Column(nullable=false)
 public MpaaRating mpaaRating;
 @ManyToOne @JoinColumn(name="director_id")
 public Person director;
 @ManyToOne @JoinColumn(name="screenwriter_id")
 public Person screenwriter;
 @ManyToOne @JoinColumn(name="operator_id")
 public Person operator;
 @NotNull @Positive @Column(nullable=false)
 public Integer length;
 @Positive
 @jakarta.json.bind.annotation.JsonbTypeSerializer(LongJsonSerializer.class) public Long goldenPalmCount;
 @Positive @Column(nullable=false)
 public int usaBoxOffice;
 @NotNull @Column(nullable=false, columnDefinition="text")
 public String tagline;
 @Enumerated(EnumType.STRING)
 public MovieGenre genre;
 @PrePersist void created() { creationDate=java.time.LocalDate.now(); }
}
