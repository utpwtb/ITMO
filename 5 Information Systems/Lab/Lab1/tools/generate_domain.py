from pathlib import Path
root=Path(__file__).resolve().parents[1]/'movie-lab'
d=root/'src/main/java/ru/itmo/movie/domain'; d.mkdir(parents=True,exist_ok=True)
enums={'MpaaRating':'G, PG, PG_13, R, NC_17','MovieGenre':'WESTERN, COMEDY, TRAGEDY, HORROR','Color':'GREEN, BLACK, ORANGE, WHITE, BROWN','Country':'GERMANY, VATICAN, ITALY, NORTH_KOREA'}
for name,values in enums.items():
 (d/f'{name}.java').write_text(f'package ru.itmo.movie.domain;\npublic enum {name} {{ {values} }}\n',encoding='utf-8')
entities={
'Coordinates': [('Integer','x','@NotNull @Max(826) @Column(nullable=false)'),('Integer','y','@NotNull @Column(nullable=false)')],
'Location':[('Long','x','@NotNull @Column(nullable=false)'),('Double','y','@NotNull @Column(nullable=false)'),('String','name','@NotNull @Column(nullable=false, columnDefinition="text")')],
'Person':[('String','name','@NotNull @Size(min=1) @Column(nullable=false, columnDefinition="text")'),('Color','eyeColor','@Enumerated(EnumType.STRING)'),('Color','hairColor','@Enumerated(EnumType.STRING)'),('Location','location','@ManyToOne @JoinColumn(name="location_id")'),('java.time.ZonedDateTime','birthday','@NotNull @Convert(converter=ZonedTimeConverter.class) @Column(nullable=false, columnDefinition="text")'),('Float','height','@Positive'),('Float','weight','@Positive'),('String','passportID','@NotNull @Column(nullable=false, unique=true, columnDefinition="text")')],
'Movie':[('String','name','@NotNull @Size(min=1) @Column(nullable=false, columnDefinition="text")'),('Coordinates','coordinates','@NotNull @ManyToOne(optional=false) @JoinColumn(name="coordinates_id",nullable=false)'),('java.time.LocalDate','creationDate','@NotNull @Column(nullable=false,insertable=false,updatable=false)'),('int','oscarsCount','@Positive @Column(nullable=false)'),('long','budget','@Positive @Column(nullable=false)'),('Double','totalBoxOffice','@Positive'),('MpaaRating','mpaaRating','@NotNull @Enumerated(EnumType.STRING) @Column(nullable=false)'),('Person','director','@ManyToOne @JoinColumn(name="director_id")'),('Person','screenwriter','@ManyToOne @JoinColumn(name="screenwriter_id")'),('Person','operator','@ManyToOne @JoinColumn(name="operator_id")'),('Integer','length','@NotNull @Positive @Column(nullable=false)'),('Long','goldenPalmCount','@Positive'),('int','usaBoxOffice','@Positive @Column(nullable=false)'),('String','tagline','@NotNull @Column(nullable=false, columnDefinition="text")'),('MovieGenre','genre','@Enumerated(EnumType.STRING)')]
}
for name,fields in entities.items():
 text='package ru.itmo.movie.domain;\nimport jakarta.persistence.*;\nimport jakarta.validation.constraints.*;\n@Entity @Table(name="'+name.lower()+'")\npublic class '+name+' {\n'
 text+=' @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Positive\n public Long id;\n @Version @Column(nullable=false) public long version;\n'
 for typ,field,anno in fields: text+=f' {anno}\n public {typ} {field};\n'
 if name=='Movie': text+=' @PrePersist void created() { creationDate=java.time.LocalDate.now(); }\n'
 text+='}\n';(d/f'{name}.java').write_text(text,encoding='utf-8')
(d/'AppState.java').write_text('''package ru.itmo.movie.domain;
import jakarta.persistence.*;
@Entity @Table(name="app_state")
public class AppState { @Id public Long id; public long revision; }
''',encoding='utf-8')
(d/'ZonedTimeConverter.java').write_text('''package ru.itmo.movie.domain;
import jakarta.persistence.*;
import java.time.ZonedDateTime;
@Converter
public class ZonedTimeConverter implements AttributeConverter<ZonedDateTime,String> {
 public String convertToDatabaseColumn(ZonedDateTime value) { return value==null?null:value.toString(); }
 public ZonedDateTime convertToEntityAttribute(String value) { return value==null?null:ZonedDateTime.parse(value); }
}
''',encoding='utf-8')
sql='''-- PostgreSQL 17. Run once in a dedicated database/schema; no destructive reset.
CREATE TABLE coordinates (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 x integer NOT NULL CHECK(x<=826), y integer NOT NULL);
CREATE TABLE location (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 x bigint NOT NULL, y double precision NOT NULL CHECK(y > '-Infinity'::float8 AND y < 'Infinity'::float8), name text NOT NULL);
CREATE TABLE person (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 name text NOT NULL CHECK(length(name)>0),
 eyecolor varchar(20) CHECK(eyecolor IN ('GREEN','BLACK','ORANGE','WHITE','BROWN')),
 haircolor varchar(20) CHECK(haircolor IN ('GREEN','BLACK','ORANGE','WHITE','BROWN')),
 location_id bigint REFERENCES location(id) ON DELETE CASCADE,
 birthday text NOT NULL CHECK(birthday ~ '^\\d{4}-\\d{2}-\\d{2}T.*(Z|[+-]\\d{2}:\\d{2})(\\[.*\\])?$'),
 height real CHECK(height>0 AND height<'Infinity'::real), weight real CHECK(weight>0 AND weight<'Infinity'::real),
 passportid text NOT NULL UNIQUE);
CREATE TABLE movie (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 name text NOT NULL CHECK(length(name)>0), coordinates_id bigint NOT NULL REFERENCES coordinates(id) ON DELETE CASCADE,
 creationdate date NOT NULL DEFAULT CURRENT_DATE, oscarscount integer NOT NULL CHECK(oscarscount>0),
 budget bigint NOT NULL CHECK(budget>0), totalboxoffice double precision CHECK(totalboxoffice>0 AND totalboxoffice<'Infinity'::float8),
 mpaarating varchar(20) NOT NULL CHECK(mpaarating IN ('G','PG','PG_13','R','NC_17')),
 director_id bigint REFERENCES person(id) ON DELETE CASCADE,
 screenwriter_id bigint REFERENCES person(id) ON DELETE CASCADE,
 operator_id bigint REFERENCES person(id) ON DELETE CASCADE,
 length integer NOT NULL CHECK(length>0), goldenpalmcount bigint CHECK(goldenpalmcount>0),
 usaboxoffice integer NOT NULL CHECK(usaboxoffice>0), tagline text NOT NULL,
 genre varchar(20) CHECK(genre IN ('WESTERN','COMEDY','TRAGEDY','HORROR')));
CREATE INDEX movie_name_idx ON movie(name);
CREATE INDEX movie_genre_idx ON movie(genre);
CREATE INDEX movie_coordinates_idx ON movie(coordinates_id);
CREATE INDEX movie_director_idx ON movie(director_id);
CREATE INDEX movie_screenwriter_idx ON movie(screenwriter_id);
CREATE INDEX movie_operator_idx ON movie(operator_id);
CREATE INDEX person_location_idx ON person(location_id);
CREATE TABLE app_state (id bigint PRIMARY KEY CHECK(id=1), revision bigint NOT NULL DEFAULT 0);
INSERT INTO app_state(id,revision) VALUES(1,0);
'''
(root/'database').mkdir(exist_ok=True);(root/'database/schema.sql').write_text(sql,encoding='utf-8')
