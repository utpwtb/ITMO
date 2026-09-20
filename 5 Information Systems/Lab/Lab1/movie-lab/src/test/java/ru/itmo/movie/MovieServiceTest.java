package ru.itmo.movie;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.sql.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import ru.itmo.movie.persistence.Database;
import ru.itmo.movie.service.*;
import ru.itmo.movie.domain.*;

/** Real PostgreSQL + EclipseLink integration tests, isolated in a temporary schema. */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MovieServiceTest {
 Database db;MovieService service;Connection connection;String schema;
 @BeforeAll void setup() throws Exception {
  String url=System.getProperty("MOVIE_TEST_DB_URL","jdbc:postgresql://127.0.0.1:55441/movie_lab_test");
  String user=System.getProperty("MOVIE_DB_USER","movie_lab"),password=System.getProperty("MOVIE_DB_PASSWORD","");
  connection=DriverManager.getConnection(url,user,password);
  schema="test_"+UUID.randomUUID().toString().replace("-","");
  try(Statement s=connection.createStatement()){s.execute("CREATE SCHEMA "+schema);s.execute("SET search_path TO "+schema);s.execute(Files.readString(Path.of("database/schema.sql")));}
  System.setProperty("MOVIE_DB_URL",url+(url.contains("?")?"&":"?")+"currentSchema="+schema);
  db=new Database();db.init();service=new MovieService(db);
 }
 @AfterAll void close() throws Exception {if(db!=null)db.close();if(connection!=null){try(Statement s=connection.createStatement()){s.execute("DROP SCHEMA "+schema+" CASCADE");}connection.close();}}
 @BeforeEach void clean() throws Exception {try(Statement s=connection.createStatement()){s.execute("TRUNCATE movie,person,coordinates,location RESTART IDENTITY CASCADE");s.execute("UPDATE app_state SET revision=0");}}
 Coordinates coord(){return (Coordinates)service.save("coordinates",null,Map.of("x",826,"y",-10));}
 Map<String,Object> data(long c,String name,int oscars,MovieGenre genre){var m=new HashMap<String,Object>();m.put("name",name);m.put("coordinates",c);m.put("oscarsCount",oscars);m.put("budget","9223372036854775807");m.put("mpaaRating","PG_13");m.put("length",120);m.put("usaBoxOffice",100);m.put("tagline","Hello_world%");if(genre!=null)m.put("genre",genre.name());return m;}
 Movie movie(String name,int oscars,MovieGenre g){return (Movie)service.save("movies",null,data(coord().id,name,oscars,g));}
 Person person(Long location){var p=new HashMap<String,Object>();p.put("name","Александр");p.put("birthday","1990-01-01T12:00+03:00[Europe/Moscow]");p.put("passportID",UUID.randomUUID().toString());if(location!=null)p.put("location",location);return (Person)service.save("people",null,p);}
 @Test void createGeneratedFieldsAndNullableReferences(){Movie m=movie("Film",1,null);assertTrue(m.id>0);assertNotNull(m.creationDate);assertEquals(Long.MAX_VALUE,m.budget);assertNull(m.director);assertNull(m.screenwriter);assertNull(m.genre);}
 @Test void updateRetainsIdentityAndCreationDate(){Movie m=movie("Old",2,MovieGenre.COMEDY);Movie next=(Movie)service.save("movies",m.id,Map.of("name","New","version",m.version));assertEquals(m.creationDate,next.creationDate);assertEquals(m.id,next.id);assertTrue(next.version>m.version);}
 @Test void optimisticConflict(){Movie m=movie("Old",2,null);service.save("movies",m.id,Map.of("name","New","version",m.version));Problem p=assertThrows(Problem.class,()->service.save("movies",m.id,Map.of("name","Lost","version",m.version)));assertEquals(409,p.status);assertEquals("New",((Movie)service.get("movies",m.id)).name);}
 @Test void invalidMovieFieldsRejected(){var data=data(coord().id,"",0,null);Problem p=assertThrows(Problem.class,()->service.save("movies",null,data));assertTrue(p.getMessage().contains("name"));assertTrue(p.getMessage().contains("oscarsCount"));assertEquals(0L,service.page(0,10,"name",null,"id",false).get("total"));}
 @Test void coordinateBoundary(){coord();assertThrows(Problem.class,()->service.save("coordinates",null,Map.of("x",827,"y",0)));}
 @Test void requiredRelation(){var data=data(999L,"Bad",1,null);assertEquals(404,assertThrows(Problem.class,()->service.save("movies",null,data)).status);}
 @Test void immutableFieldsRejected(){var data=data(coord().id,"Bad",1,null);data.put("creationDate","2020-01-01");assertThrows(Problem.class,()->service.save("movies",null,data));}
 @Test void duplicatePassport(){Person p=person(null);assertEquals(409,assertThrows(Problem.class,()->service.save("people",null,Map.of("name","B","birthday",p.birthday.toString(),"passportID",p.passportID))).status);}
 @Test void zonedBirthdayRoundTrip(){Person p=person(null);Person read=(Person)service.get("people",p.id);assertEquals("Europe/Moscow",read.birthday.getZone().getId());assertEquals(p.birthday,read.birthday);}
 @Test void nonFiniteRejected(){assertThrows(Problem.class,()->service.save("locations",null,Map.of("name","X","x",1,"y","NaN")));}
 @Test void precisionAndRange(){var data=data(coord().id,"Bad",1,null);data.put("budget","9223372036854775808");assertThrows(Problem.class,()->service.save("movies",null,data));}
 @Test void exactFilteringSortingPagination(){movie("Alpha",1,null);movie("Alphabet",1,null);movie("Beta",1,null);assertEquals(1L,service.page(0,10,"name","Alpha","name",false).get("total"));var p=service.page(1,1,"name",null,"name",true);assertEquals("Alphabet",((Movie)((List<?>)p.get("items")).get(0)).name);assertEquals(3L,p.get("total"));}
 @Test void stringTaglineExactFilter(){movie("Alpha",1,null);assertEquals(0L,service.page(0,10,"tagline","Hello","id",false).get("total"));assertEquals(1L,service.page(0,10,"tagline","Hello_world%","id",false).get("total"));}
 @Test void pageBoundsAndSortInjection(){assertThrows(Problem.class,()->service.page(-1,10,"name",null,"id",false));assertThrows(Problem.class,()->service.page(0,101,"name",null,"id",false));assertThrows(Problem.class,()->service.page(0,10,"name",null,"name DESC; DELETE",false));}
 @Test void escapedPrefix(){Movie m=movie("A",1,null);movie("B",1,null);service.save("movies",m.id,Map.of("version",m.version,"tagline","HelloXworld!"));assertEquals(1,service.prefix("Hello_").size());assertEquals(1,service.prefix("Hello_world%").size());assertEquals(2,service.prefix("").size());assertEquals(0,service.prefix("%").size());}
 @Test void averageEmptyAndNonempty(){assertNull(service.average());Movie a=movie("A",1,null);movie("B",1,null);service.save("movies",a.id,Map.of("version",a.version,"usaBoxOffice",200));assertEquals(150d,service.average());}
 @Test void deleteByBoxOffice(){movie("A",1,null);movie("B",1,null);assertEquals(2,service.deleteByBoxOffice(100));assertNull(service.average());assertEquals(0,service.deleteByBoxOffice(100));}
 @Test void redistributionConservesAwardsAndRemainder(){Movie a=movie("A",5,MovieGenre.HORROR);Movie b=movie("B",4,MovieGenre.HORROR);Movie c=movie("C",2,MovieGenre.COMEDY);Movie d=movie("D",2,MovieGenre.COMEDY);var result=service.redistribute(MovieGenre.HORROR,MovieGenre.COMEDY);assertEquals(7L,result.get("transferred"));assertEquals(1,((Movie)service.get("movies",a.id)).oscarsCount);assertEquals(1,((Movie)service.get("movies",b.id)).oscarsCount);assertEquals(6,((Movie)service.get("movies",c.id)).oscarsCount);assertEquals(5,((Movie)service.get("movies",d.id)).oscarsCount);}
 @Test void redistributionRejectsSameAndEmpty(){movie("A",2,MovieGenre.HORROR);assertThrows(Problem.class,()->service.redistribute(MovieGenre.HORROR,MovieGenre.HORROR));assertThrows(Problem.class,()->service.redistribute(MovieGenre.HORROR,MovieGenre.COMEDY));}
 @Test void redistributionZeroPool(){movie("A",1,MovieGenre.HORROR);movie("B",2,MovieGenre.COMEDY);assertEquals(0L,service.redistribute(MovieGenre.HORROR,MovieGenre.COMEDY).get("transferred"));}
 @Test void awardStrictBoundary(){Movie a=movie("A",1,null);Movie b=movie("B",1,null);service.save("movies",b.id,Map.of("version",b.version,"length",121));assertEquals(1,service.award(120,3));assertEquals(1,((Movie)service.get("movies",a.id)).oscarsCount);assertEquals(4,((Movie)service.get("movies",b.id)).oscarsCount);}
 @Test void awardOverflowRollsBackWholeTransaction(){Movie a=movie("A",1,null);Movie b=movie("B",Integer.MAX_VALUE,null);long revision=service.revision();assertThrows(Problem.class,()->service.award(1,1));assertEquals(1,((Movie)service.get("movies",a.id)).oscarsCount);assertEquals(Integer.MAX_VALUE,((Movie)service.get("movies",b.id)).oscarsCount);assertEquals(revision,service.revision());}
 @Test void cascadeCoordinates(){Coordinates c=coord();Movie m=(Movie)service.save("movies",null,data(c.id,"A",1,null));assertEquals(2,service.delete("coordinates",c.id,c.version));assertThrows(Problem.class,()->service.get("movies",m.id));}
 @Test void cascadeLocationPersonMovie(){Location l=(Location)service.save("locations",null,Map.of("x",1,"y",2,"name","SPb"));Person p=person(l.id);var data=data(coord().id,"A",1,null);data.put("operator",p.id);Movie m=(Movie)service.save("movies",null,data);assertEquals(3,service.delete("locations",l.id,l.version));assertThrows(Problem.class,()->service.get("people",p.id));assertThrows(Problem.class,()->service.get("movies",m.id));}
 @Test void reusableReferencesSurviveMovieDeletion(){Person p=person(null);Coordinates c=coord();var data=data(c.id,"A",1,null);data.put("director",p.id);Movie a=(Movie)service.save("movies",null,data);data.put("name","B");Movie b=(Movie)service.save("movies",null,data);service.delete("movies",a.id,a.version);assertNotNull(service.get("people",p.id));assertEquals(p.id,((Movie)service.get("movies",b.id)).director.id);}
 @Test void databaseConstraintsIndependently() throws Exception {
  try(Statement s=connection.createStatement()){
   assertThrows(SQLException.class,()->s.execute("INSERT INTO coordinates(x,y) VALUES(827,1)"));
   assertThrows(SQLException.class,()->s.execute("INSERT INTO person(name,birthday,passportid) VALUES('', '1990-01-01T00:00Z','x')"));
   assertThrows(SQLException.class,()->s.execute("INSERT INTO location(x,y,name) VALUES(1,'NaN','x')"));
   assertThrows(SQLException.class,()->s.execute("INSERT INTO coordinates(x,y) VALUES(NULL,1)"));
  }
 }
 @Test void concurrentAwardsHaveNoLostUpdates() throws Exception {
  Movie m=movie("A",1,null);ExecutorService executor=Executors.newFixedThreadPool(4);
  try{List<Callable<Integer>> calls=new ArrayList<>();for(int i=0;i<12;i++)calls.add(()->service.award(1,1));for(Future<Integer> f:executor.invokeAll(calls))assertEquals(1,f.get());}finally{executor.shutdown();}
  assertEquals(13,((Movie)service.get("movies",m.id)).oscarsCount);
 }
 @Test void revisionOnlyAfterCommit(){long before=service.revision();coord();assertEquals(before+1,service.revision());assertThrows(Problem.class,()->service.save("coordinates",null,Map.of("x",999,"y",0)));assertEquals(before+1,service.revision());}
 @Test void nullableRoleSortingIncludesUnrelatedMovies(){Movie a=movie("A",1,null);Person p=person(null);Movie b=movie("B",1,null);service.save("movies",b.id,Map.of("version",b.version,"director",p.id));assertEquals(2,((List<?>)service.page(0,10,"name",null,"director",false).get("items")).size());assertEquals(1L,service.page(0,10,"director",p.name,"id",false).get("total"));}
 @Test void allPositiveMovieFieldsAtServiceAndDatabase() throws Exception {
  Coordinates c=coord();
  for(String field:List.of("oscarsCount","budget","totalBoxOffice","length","goldenPalmCount","usaBoxOffice")){
   var input=data(c.id,"Valid",2,null);input.put(field,0);assertThrows(Problem.class,()->service.save("movies",null,input),field);
  }
  Movie m=(Movie)service.save("movies",null,data(c.id,"Valid",2,null));
  try(Statement s=connection.createStatement()){
   for(String field:List.of("oscarscount","budget","totalboxoffice","length","goldenpalmcount","usaboxoffice"))assertThrows(SQLException.class,()->s.execute("UPDATE movie SET "+field+"=0 WHERE id="+m.id),field);
   for(String field:List.of("name","coordinates_id","creationdate","mpaarating","length","tagline"))assertThrows(SQLException.class,()->s.execute("UPDATE movie SET "+field+"=NULL WHERE id="+m.id),field);
   assertThrows(SQLException.class,()->s.execute("UPDATE movie SET mpaarating='BAD' WHERE id="+m.id));
   assertThrows(SQLException.class,()->s.execute("UPDATE movie SET genre='BAD' WHERE id="+m.id));
  }
 }
 @Test void personConstraintsAtDatabase() throws Exception {
  Person p=person(null);
  try(Statement s=connection.createStatement()){
   for(String field:List.of("height","weight"))assertThrows(SQLException.class,()->s.execute("UPDATE person SET "+field+"=0 WHERE id="+p.id));
   for(String field:List.of("name","birthday","passportid"))assertThrows(SQLException.class,()->s.execute("UPDATE person SET "+field+"=NULL WHERE id="+p.id));
   assertThrows(SQLException.class,()->s.execute("UPDATE person SET birthday='2020-99-99T00:00Z' WHERE id="+p.id));
   assertThrows(SQLException.class,()->s.execute("INSERT INTO person(name,birthday,passportid) SELECT name,birthday,passportid FROM person WHERE id="+p.id));
  }
 }
 @Test void redistributionOverflowRollsBack(){Movie a=movie("A",3,MovieGenre.HORROR);movie("B",Integer.MAX_VALUE,MovieGenre.COMEDY);assertThrows(Problem.class,()->service.redistribute(MovieGenre.HORROR,MovieGenre.COMEDY));assertEquals(3,((Movie)service.get("movies",a.id)).oscarsCount);}
}
