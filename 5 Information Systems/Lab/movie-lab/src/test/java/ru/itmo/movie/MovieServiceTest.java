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

/**
 * Real PostgreSQL + EclipseLink integration tests, isolated in a temporary schema.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MovieServiceTest {
    Database db;
    MovieService service;
    Connection connection;
    String schema;

    boolean sharedSchema;
    boolean created;

    String sql(String statement) {
        return sharedSchema ? statement.replaceAll("\\b(movie|person|coordinates|location|app_state|app_user|import_operation)\\b", "lab2_4101_test_$1")
                .replaceAll("\\b(movie_[a-z]+_idx|person_location_idx|import_operation_user_idx)\\b", "lab2_4101_test_$1") : statement;
    }

    @BeforeAll
    void setup() throws Exception {
        String url = Database.config("MOVIE_TEST_DB_URL", "jdbc:postgresql://127.0.0.1:55441/movie_lab_test");
        String user = Database.config("MOVIE_DB_USER", "movie_lab"), password = Database.config("MOVIE_DB_PASSWORD", "");
        connection = DriverManager.getConnection(url, user, password);
        schema = Database.config("MOVIE_TEST_SCHEMA", "");
        sharedSchema = !schema.isEmpty();
        if (!sharedSchema) schema = "test_" + UUID.randomUUID().toString().replace("-", "");
        if (!schema.matches("[a-z][a-z0-9_]*")) throw new IllegalArgumentException("Invalid test schema");
        connection.setAutoCommit(false);
        try (Statement s = connection.createStatement()) {
            if (!sharedSchema) s.execute("CREATE SCHEMA " + schema);
            s.execute("SET search_path TO " + schema);
            // Plain CREATE TABLE intentionally refuses to overwrite existing test data.
            s.execute(sql(Files.readString(Path.of("database/schema.sql"))));
            connection.commit();
            created = true;
        } catch (Exception e) {
            connection.rollback();
            throw e;
        } finally {
            connection.setAutoCommit(true);
        }
        System.setProperty("MOVIE_DB_URL", url + (url.contains("?") ? "&" : "?") + "currentSchema=" + schema);
        System.setProperty("MOVIE_PERSISTENCE_UNIT", sharedSchema ? "movies-helios-test" : "movies");
        db = new Database();
        db.init();
        service = new MovieService(db);
    }

    @AfterAll
    void close() throws Exception {
        if (db != null) db.close();
        if (connection != null) {
            try (Statement s = connection.createStatement()) {
                if (created) {
                    if (sharedSchema) s.execute(sql("DROP TABLE import_operation,movie,person,coordinates,location,app_state,app_user"));
                    else s.execute("DROP SCHEMA " + schema + " CASCADE");
                }
            } finally {
                connection.close();
            }
        }
    }

    @BeforeEach
    void clean() throws Exception {
        try (Statement s = connection.createStatement()) {
            s.execute(sql("TRUNCATE import_operation,movie,person,coordinates,location,app_user RESTART IDENTITY"));
            s.execute(sql("UPDATE app_state SET revision=0"));
        }
    }

    Coordinates coord() {
        return (Coordinates) service.save("coordinates", null, Map.of("x", 826, "y", -10));
    }

    @Test
    void registeredAccountPersistsAndUsesDistinctSalt() {
        AuthService auth = new AuthService(db);
        String password = "Integration password 2026";
        assertEquals("tester_one", auth.register(" tester_one ", password));
        auth.register("tester_two", password);
        AppUser one = db.read(em -> em.createQuery("SELECT u FROM AppUser u WHERE u.username='tester_one'", AppUser.class).getSingleResult());
        AppUser two = db.read(em -> em.createQuery("SELECT u FROM AppUser u WHERE u.username='tester_two'", AppUser.class).getSingleResult());
        assertNotEquals(password, one.passwordHash);
        assertNotEquals(one.passwordHash, two.passwordHash);
        assertNotEquals(one.salt, two.salt);
        assertEquals(32, Base64.getDecoder().decode(one.passwordHash).length);
        assertEquals(16, Base64.getDecoder().decode(one.salt).length);
        assertEquals("tester_one", new AuthService(db).authenticate("tester_one", password));
    }

    @Test
    void duplicateAccountIsRejectedWithoutChangingPassword() {
        AuthService auth = new AuthService(db);
        auth.register("tester", "First password 2026");
        Problem p = assertThrows(Problem.class, () -> auth.register(" tester ", "Second password 2026"));
        assertEquals(409, p.status);
        assertEquals("tester", auth.authenticate("tester", "First password 2026"));
        assertEquals(401, assertThrows(Problem.class, () -> auth.authenticate("tester", "Second password 2026")).status);
    }

    @Test
    void invalidRegistrationIsRejected() {
        AuthService auth = new AuthService(db);
        for (String name : new String[]{"ab", "with space", "<script>", "x".repeat(65)})
            assertEquals(400, assertThrows(Problem.class, () -> auth.register(name, "Long password 2026")).status);
        for (String password : new String[]{"short", "x".repeat(129)})
            assertEquals(400, assertThrows(Problem.class, () -> auth.register("tester", password)).status);
        assertEquals(400, assertThrows(Problem.class, () -> auth.register(null, null)).status);
        assertEquals(0L, db.read(em -> em.createQuery("SELECT COUNT(u) FROM AppUser u", Long.class).getSingleResult()).longValue());
    }

    @Test
    void incorrectLoginIsRejected() {
        AuthService auth = new AuthService(db);
        auth.register("tester", "Correct password 2026");
        for (String name : new String[]{"tester", "missing"})
            assertEquals(401, assertThrows(Problem.class, () -> auth.authenticate(name, "wrong")).status);
        assertEquals(401, assertThrows(Problem.class, () -> auth.authenticate(null, null)).status);
    }

    @Test
    void defaultAccountIsSeededOnlyOnce() {
        AuthService auth = new AuthService(db);
        auth.seedDefaultAccount();
        String name = Database.config("MOVIE_USER", "student");
        String password = Database.config("MOVIE_PASSWORD", "student");
        assertEquals(name, auth.authenticate(name, password));
        String previous = System.getProperty("MOVIE_PASSWORD");
        try {
            System.setProperty("MOVIE_PASSWORD", "Changed bootstrap password");
            new AuthService(db).seedDefaultAccount();
            assertEquals(name, auth.authenticate(name, password));
            assertEquals(401, assertThrows(Problem.class, () -> auth.authenticate(name, "Changed bootstrap password")).status);
            assertEquals(1L, db.read(em -> em.createQuery("SELECT COUNT(u) FROM AppUser u", Long.class).getSingleResult()).longValue());
        } finally {
            if (previous == null) System.clearProperty("MOVIE_PASSWORD");
            else System.setProperty("MOVIE_PASSWORD", previous);
        }
    }

    @Test
    void concurrentRegistrationCreatesExactlyOneAccount() throws Exception {
        ExecutorService workers = Executors.newFixedThreadPool(2);
        CountDownLatch ready = new CountDownLatch(2), start = new CountDownLatch(1);
        Callable<Integer> create = () -> {
            ready.countDown();
            start.await();
            try {
                new AuthService(db).register("same_user", "Concurrent password 2026");
                return 201;
            } catch (Problem p) {
                return p.status;
            }
        };
        try {
            Future<Integer> first = workers.submit(create), second = workers.submit(create);
            assertTrue(ready.await(10, TimeUnit.SECONDS));
            start.countDown();
            var statuses = new ArrayList<>(List.of(first.get(30, TimeUnit.SECONDS), second.get(30, TimeUnit.SECONDS)));
            Collections.sort(statuses);
            assertEquals(List.of(201, 409), statuses);
            assertEquals(1L, db.read(em -> em.createQuery("SELECT COUNT(u) FROM AppUser u", Long.class).getSingleResult()).longValue());
        } finally {
            start.countDown();
            workers.shutdownNow();
        }
    }

    Map<String, Object> data(long c, String name, int oscars, MovieGenre genre) {
        var m = new HashMap<String, Object>();
        m.put("name", name);
        m.put("coordinates", c);
        m.put("oscarsCount", oscars);
        m.put("budget", "9223372036854775807");
        m.put("mpaaRating", "PG_13");
        m.put("length", 120);
        m.put("usaBoxOffice", 100);
        m.put("tagline", "Hello_world%");
        if (genre != null) m.put("genre", genre.name());
        return m;
    }

    Movie movie(String name, int oscars, MovieGenre g) {
        return (Movie) service.save("movies", null, data(coord().id, name, oscars, g));
    }

    Person person(Long location) {
        var p = new HashMap<String, Object>();
        p.put("name", "Александр");
        p.put("birthday", "1990-01-01T12:00+03:00[Europe/Moscow]");
        p.put("passportID", UUID.randomUUID().toString());
        if (location != null) p.put("location", location);
        return (Person) service.save("people", null, p);
    }

    @Test
    void createGeneratedFieldsAndNullableReferences() {
        Movie m = movie("Film", 1, null);
        assertTrue(m.id > 0);
        assertNotNull(m.creationDate);
        assertEquals(Long.MAX_VALUE, m.budget);
        assertNull(m.director);
        assertNull(m.screenwriter);
        assertNull(m.genre);
    }

    @Test
    void updateRetainsIdentityAndCreationDate() {
        Movie m = movie("Old", 2, MovieGenre.COMEDY);
        Movie next = (Movie) service.save("movies", m.id, Map.of("name", "New", "version", m.version));
        assertEquals(m.creationDate, next.creationDate);
        assertEquals(m.id, next.id);
        assertTrue(next.version > m.version);
    }

    @Test
    void optimisticConflict() {
        Movie m = movie("Old", 2, null);
        service.save("movies", m.id, Map.of("name", "New", "version", m.version));
        Problem p = assertThrows(Problem.class, () -> service.save("movies", m.id, Map.of("name", "Lost", "version", m.version)));
        assertEquals(409, p.status);
        assertEquals("New", ((Movie) service.get("movies", m.id)).name);
    }

    @Test
    void invalidMovieFieldsRejected() {
        var data = data(coord().id, "", 0, null);
        Problem p = assertThrows(Problem.class, () -> service.save("movies", null, data));
        assertTrue(p.getMessage().contains("name"));
        assertTrue(p.getMessage().contains("oscarsCount"));
        assertEquals(0L, service.page(0, 10, "name", null, "id", false).get("total"));
    }

    @Test
    void coordinateBoundary() {
        coord();
        assertThrows(Problem.class, () -> service.save("coordinates", null, Map.of("x", 827, "y", 0)));
    }

    @Test
    void requiredRelation() {
        var data = data(999L, "Bad", 1, null);
        assertEquals(404, assertThrows(Problem.class, () -> service.save("movies", null, data)).status);
    }

    @Test
    void immutableFieldsRejected() {
        var data = data(coord().id, "Bad", 1, null);
        data.put("creationDate", "2020-01-01");
        assertThrows(Problem.class, () -> service.save("movies", null, data));
    }

    @Test
    void duplicatePassport() {
        Person p = person(null);
        assertEquals(409, assertThrows(Problem.class, () -> service.save("people", null, Map.of("name", "B", "birthday", p.birthday.toString(), "passportID", p.passportID))).status);
    }

    @Test
    void zonedBirthdayRoundTrip() {
        Person p = person(null);
        Person read = (Person) service.get("people", p.id);
        assertEquals("Europe/Moscow", read.birthday.getZone().getId());
        assertEquals(p.birthday, read.birthday);
    }

    @Test
    void nonFiniteRejected() {
        assertThrows(Problem.class, () -> service.save("locations", null, Map.of("name", "X", "x", 1, "y", "NaN")));
    }

    @Test
    void precisionAndRange() {
        var data = data(coord().id, "Bad", 1, null);
        data.put("budget", "9223372036854775808");
        assertThrows(Problem.class, () -> service.save("movies", null, data));
    }

    @Test
    void boxOfficeRelationshipRejectsCreateAndRollsBackUpdate() {
        Coordinates c = coord();
        var input = data(c.id, "Box office", 1, null);
        input.put("totalBoxOffice", 99.5);
        long revision = service.revision();
        Problem error = assertThrows(Problem.class, () -> service.save("movies", null, input));
        assertEquals(400, error.status);
        assertTrue(error.getMessage().contains("usaBoxOffice"));
        assertEquals(revision, service.revision());
        assertEquals(0L, service.page(0, 10, "name", null, "id", false).get("total"));

        input.put("totalBoxOffice", 100);
        Movie m = (Movie) service.save("movies", null, input);
        assertThrows(Problem.class, () -> service.save("movies", m.id,
                Map.of("version", m.version, "usaBoxOffice", 101)));
        assertThrows(Problem.class, () -> service.save("movies", m.id,
                Map.of("version", m.version, "totalBoxOffice", 99.5)));
        Movie unchanged = (Movie) service.get("movies", m.id);
        assertEquals(100, unchanged.usaBoxOffice);
        assertEquals(100.0, unchanged.totalBoxOffice);
        assertEquals(m.version, unchanged.version);
    }

    @Test
    void boxOfficeRelationshipAllowsEqualGreaterAndUnknownTotal() {
        var input = data(coord().id, "Box office", 1, null);
        input.put("totalBoxOffice", 100);
        Movie m = (Movie) service.save("movies", null, input);
        m = (Movie) service.save("movies", m.id, Map.of("version", m.version, "totalBoxOffice", 100.5));
        assertEquals(100.5, m.totalBoxOffice);
        var update = new HashMap<String, Object>();
        update.put("version", m.version);
        update.put("totalBoxOffice", null);
        Movie next = (Movie) service.save("movies", m.id, update);
        assertNull(next.totalBoxOffice);
        assertEquals(100, next.usaBoxOffice);
    }

    @Test
    void databaseEnforcesBoxOfficeRelationshipWithoutService() throws Exception {
        Movie m = movie("Box office", 1, null);
        try (Statement s = connection.createStatement()) {
            s.execute(sql("UPDATE movie SET totalboxoffice=100 WHERE id=" + m.id));
            assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET usaboxoffice=101 WHERE id=" + m.id)));
            assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET totalboxoffice=99.5 WHERE id=" + m.id)));
            s.execute(sql("UPDATE movie SET totalboxoffice=100.5 WHERE id=" + m.id));
            s.execute(sql("UPDATE movie SET totalboxoffice=NULL WHERE id=" + m.id));
            s.execute(sql("UPDATE movie SET usaboxoffice=200 WHERE id=" + m.id));
        }
    }

    @Test
    void boxOfficeMigrationValidatesExistingDataAndCanBeRepeated() throws Exception {
        Movie m = movie("Migration", 1, null);
        String migration = sql(Files.readString(Path.of("database/migrations/002_box_office.sql")));
        try (Statement s = connection.createStatement()) {
            s.execute(sql("ALTER TABLE movie DROP CONSTRAINT movie_box_office_consistency"));
            s.execute(sql("UPDATE movie SET totalboxoffice=50 WHERE id=" + m.id));
            assertThrows(SQLException.class, () -> s.execute(migration));
            try (ResultSet rows = s.executeQuery(sql("SELECT totalboxoffice FROM movie WHERE id=" + m.id))) {
                assertTrue(rows.next());
                assertEquals(50, rows.getDouble(1)); // Migration did not rewrite inconsistent records.
            }
            s.execute(sql("UPDATE movie SET totalboxoffice=100 WHERE id=" + m.id));
            s.execute(migration);
            s.execute(migration);
            assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET usaboxoffice=101 WHERE id=" + m.id)));
        }
    }

    @Test
    void exactFilteringSortingPagination() {
        movie("Alpha", 1, null);
        movie("Alphabet", 1, null);
        movie("Beta", 1, null);
        assertEquals(1L, service.page(0, 10, "name", "Alpha", "name", false).get("total"));
        var p = service.page(1, 1, "name", null, "name", true);
        assertEquals("Alphabet", ((Movie) ((List<?>) p.get("items")).get(0)).name);
        assertEquals(3L, p.get("total"));
    }

    @Test
    void stringTaglineExactFilter() {
        movie("Alpha", 1, null);
        assertEquals(0L, service.page(0, 10, "tagline", "Hello", "id", false).get("total"));
        assertEquals(1L, service.page(0, 10, "tagline", "Hello_world%", "id", false).get("total"));
    }

    @Test
    void pageBoundsAndSortInjection() {
        assertThrows(Problem.class, () -> service.page(-1, 10, "name", null, "id", false));
        assertThrows(Problem.class, () -> service.page(0, 101, "name", null, "id", false));
        assertThrows(Problem.class, () -> service.page(0, 10, "name", null, "name DESC; DELETE", false));
    }

    @Test
    void escapedPrefix() {
        Movie m = movie("A", 1, null);
        movie("B", 1, null);
        service.save("movies", m.id, Map.of("version", m.version, "tagline", "HelloXworld!"));
        assertEquals(1, service.prefix("Hello_").size());
        assertEquals(1, service.prefix("Hello_world%").size());
        assertEquals(2, service.prefix("").size());
        assertEquals(0, service.prefix("%").size());
    }

    @Test
    void averageEmptyAndNonempty() {
        assertNull(service.average());
        Movie a = movie("A", 1, null);
        movie("B", 1, null);
        service.save("movies", a.id, Map.of("version", a.version, "usaBoxOffice", 200));
        assertEquals(150d, service.average());
    }

    @Test
    void deleteByBoxOffice() {
        movie("A", 1, null);
        movie("B", 1, null);
        assertEquals(2, service.deleteByBoxOffice(100));
        assertNull(service.average());
        assertEquals(0, service.deleteByBoxOffice(100));
    }

    @Test
    void redistributionConservesAwardsAndRemainder() {
        Movie a = movie("A", 5, MovieGenre.HORROR);
        Movie b = movie("B", 4, MovieGenre.HORROR);
        Movie c = movie("C", 2, MovieGenre.COMEDY);
        Movie d = movie("D", 2, MovieGenre.COMEDY);
        var result = service.redistribute(MovieGenre.HORROR, MovieGenre.COMEDY);
        assertEquals(7L, result.get("transferred"));
        assertEquals(1, ((Movie) service.get("movies", a.id)).oscarsCount);
        assertEquals(1, ((Movie) service.get("movies", b.id)).oscarsCount);
        assertEquals(6, ((Movie) service.get("movies", c.id)).oscarsCount);
        assertEquals(5, ((Movie) service.get("movies", d.id)).oscarsCount);
    }

    @Test
    void redistributionRejectsSameAndEmpty() {
        movie("A", 2, MovieGenre.HORROR);
        assertThrows(Problem.class, () -> service.redistribute(MovieGenre.HORROR, MovieGenre.HORROR));
        assertThrows(Problem.class, () -> service.redistribute(MovieGenre.HORROR, MovieGenre.COMEDY));
    }

    @Test
    void redistributionZeroPool() {
        movie("A", 1, MovieGenre.HORROR);
        movie("B", 2, MovieGenre.COMEDY);
        assertEquals(0L, service.redistribute(MovieGenre.HORROR, MovieGenre.COMEDY).get("transferred"));
    }

    @Test
    void awardStrictBoundary() {
        Movie a = movie("A", 1, null);
        Movie b = movie("B", 1, null);
        service.save("movies", b.id, Map.of("version", b.version, "length", 121));
        assertEquals(1, service.award(120, 3));
        assertEquals(1, ((Movie) service.get("movies", a.id)).oscarsCount);
        assertEquals(4, ((Movie) service.get("movies", b.id)).oscarsCount);
    }

    @Test
    void awardOverflowRollsBackWholeTransaction() {
        Movie a = movie("A", 1, null);
        Movie b = movie("B", Integer.MAX_VALUE, null);
        long revision = service.revision();
        assertThrows(Problem.class, () -> service.award(1, 1));
        assertEquals(1, ((Movie) service.get("movies", a.id)).oscarsCount);
        assertEquals(Integer.MAX_VALUE, ((Movie) service.get("movies", b.id)).oscarsCount);
        assertEquals(revision, service.revision());
    }

    @Test
    void cascadeCoordinates() {
        Coordinates c = coord();
        Movie m = (Movie) service.save("movies", null, data(c.id, "A", 1, null));
        assertEquals(2, service.delete("coordinates", c.id, c.version));
        assertThrows(Problem.class, () -> service.get("movies", m.id));
    }

    @Test
    void cascadeLocationPersonMovie() {
        Location l = (Location) service.save("locations", null, Map.of("x", 1, "y", 2, "name", "SPb"));
        Person p = person(l.id);
        var data = data(coord().id, "A", 1, null);
        data.put("operator", p.id);
        Movie m = (Movie) service.save("movies", null, data);
        assertEquals(3, service.delete("locations", l.id, l.version));
        assertThrows(Problem.class, () -> service.get("people", p.id));
        assertThrows(Problem.class, () -> service.get("movies", m.id));
    }

    @Test
    void reusableReferencesSurviveMovieDeletion() {
        Person p = person(null);
        Coordinates c = coord();
        var data = data(c.id, "A", 1, null);
        data.put("director", p.id);
        Movie a = (Movie) service.save("movies", null, data);
        data.put("name", "B");
        Movie b = (Movie) service.save("movies", null, data);
        service.delete("movies", a.id, a.version);
        assertNotNull(service.get("people", p.id));
        assertEquals(p.id, ((Movie) service.get("movies", b.id)).director.id);
    }

    @Test
    void databaseConstraintsIndependently() throws Exception {
        try (Statement s = connection.createStatement()) {
            assertThrows(SQLException.class, () -> s.execute(sql("INSERT INTO coordinates(x,y) VALUES(827,1)")));
            assertThrows(SQLException.class, () -> s.execute(sql("INSERT INTO person(name,birthday,passportid) VALUES('', '1990-01-01T00:00Z','x')")));
            assertThrows(SQLException.class, () -> s.execute(sql("INSERT INTO location(x,y,name) VALUES(1,'NaN','x')")));
            assertThrows(SQLException.class, () -> s.execute(sql("INSERT INTO coordinates(x,y) VALUES(NULL,1)")));
        }
    }

    @Test
    void concurrentAwardsHaveNoLostUpdates() throws Exception {
        Movie m = movie("A", 1, null);
        ExecutorService executor = Executors.newFixedThreadPool(4);
        try {
            List<Callable<Integer>> calls = new ArrayList<>();
            for (int i = 0; i < 12; i++) calls.add(() -> service.award(1, 1));
            for (Future<Integer> f : executor.invokeAll(calls)) assertEquals(1, f.get());
        } finally {
            executor.shutdown();
        }
        assertEquals(13, ((Movie) service.get("movies", m.id)).oscarsCount);
    }

    @Test
    void revisionOnlyAfterCommit() {
        long before = service.revision();
        coord();
        assertEquals(before + 1, service.revision());
        assertThrows(Problem.class, () -> service.save("coordinates", null, Map.of("x", 999, "y", 0)));
        assertEquals(before + 1, service.revision());
    }

    @Test
    void nullableRoleSortingIncludesUnrelatedMovies() {
        Movie a = movie("A", 1, null);
        Person p = person(null);
        Movie b = movie("B", 1, null);
        service.save("movies", b.id, Map.of("version", b.version, "director", p.id));
        assertEquals(2, ((List<?>) service.page(0, 10, "name", null, "director", false).get("items")).size());
        assertEquals(1L, service.page(0, 10, "director", p.name, "id", false).get("total"));
    }

    @Test
    void allPositiveMovieFieldsAtServiceAndDatabase() throws Exception {
        Coordinates c = coord();
        for (String field : List.of("oscarsCount", "budget", "totalBoxOffice", "length", "goldenPalmCount", "usaBoxOffice")) {
            var input = data(c.id, "Valid", 2, null);
            input.put(field, 0);
            assertThrows(Problem.class, () -> service.save("movies", null, input), field);
        }
        Movie m = (Movie) service.save("movies", null, data(c.id, "Valid", 2, null));
        try (Statement s = connection.createStatement()) {
            for (String field : List.of("oscarscount", "budget", "totalboxoffice", "length", "goldenpalmcount", "usaboxoffice"))
                assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET " + field + "=0 WHERE id=" + m.id)), field);
            for (String field : List.of("name", "coordinates_id", "creationdate", "mpaarating", "length", "tagline"))
                assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET " + field + "=NULL WHERE id=" + m.id)), field);
            assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET mpaarating='BAD' WHERE id=" + m.id)));
            assertThrows(SQLException.class, () -> s.execute(sql("UPDATE movie SET genre='BAD' WHERE id=" + m.id)));
        }
    }

    @Test
    void personConstraintsAtDatabase() throws Exception {
        Person p = person(null);
        try (Statement s = connection.createStatement()) {
            for (String field : List.of("height", "weight"))
                assertThrows(SQLException.class, () -> s.execute(sql("UPDATE person SET " + field + "=0 WHERE id=" + p.id)));
            for (String field : List.of("name", "birthday", "passportid"))
                assertThrows(SQLException.class, () -> s.execute(sql("UPDATE person SET " + field + "=NULL WHERE id=" + p.id)));
            assertThrows(SQLException.class, () -> s.execute(sql("UPDATE person SET birthday='2020-99-99T00:00Z' WHERE id=" + p.id)));
            assertThrows(SQLException.class, () -> s.execute(sql("INSERT INTO person(name,birthday,passportid) SELECT name,birthday,passportid FROM person WHERE id=" + p.id)));
        }
    }

    @Test
    void redistributionOverflowRollsBack() {
        Movie a = movie("A", 3, MovieGenre.HORROR);
        movie("B", Integer.MAX_VALUE, MovieGenre.COMEDY);
        assertThrows(Problem.class, () -> service.redistribute(MovieGenre.HORROR, MovieGenre.COMEDY));
        assertEquals(3, ((Movie) service.get("movies", a.id)).oscarsCount);
    }

    @Nested
    class Lab2 {
        final com.fasterxml.jackson.databind.ObjectMapper json = new com.fasterxml.jackson.databind.ObjectMapper();
        byte[] fixture() throws Exception { return Files.readAllBytes(Path.of("src/test/resources/import/import-valid.json")); }
        com.fasterxml.jackson.databind.node.ObjectNode document() throws Exception { return (com.fasterxml.jackson.databind.node.ObjectNode)json.readTree(fixture()); }
        byte[] bytes(Object value) throws Exception { return json.writeValueAsBytes(value); }
        ImportService importer() { return new ImportService(db,service); }
        ImportHistoryService history() { return new ImportHistoryService(db); }
        long count(Class<?> type) { return db.read(em -> em.createQuery("SELECT COUNT(x) FROM "+type.getSimpleName()+" x",Long.class).getSingleResult()); }
        List<Long> domains() { return List.of(count(Movie.class),count(Person.class),count(Coordinates.class),count(Location.class)); }
        void user(String name) { new AuthService(db).register(name,"Integration password 2026"); }
        void users() { user("ordinary_a"); user("ordinary_b"); user("admin_a"); user("admin_b"); db.metadata(em -> { for(String n:List.of("admin_a","admin_b")) ImportHistoryService.account(em,n).role=UserRole.ADMIN; return null; }); }

        @Test void F01_F07_exactIntegersPersonReuseAndSingleRevision() throws Exception {
            user("ordinary_a"); long revision=service.revision();
            var doc=document(); ((com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(0)).put("budget",9007199254740993L);
            var result=importer().upload("ordinary_a","example.json",bytes(doc));
            assertEquals("SUCCESS",result.get("status")); assertEquals(2,result.get("addedCount"));
            assertEquals(List.of(2L,1L,2L,1L),domains()); assertEquals(revision+1,service.revision());
            assertEquals(9007199254740993L,((Movie)service.all("movies").get(0)).budget);
            assertEquals(1,history().list("ordinary_a",0,10).get("total") instanceof Long n ? n.intValue() : -1);
        }

        @TestFactory java.util.stream.Stream<DynamicTest> F02_F04_F06_strictFieldMatrix() throws Exception {
            List<DynamicTest> cases=new ArrayList<>();
            var base=document();
            Map<String,List<String>> required=Map.of("",List.of("name","coordinates","oscarsCount","budget","mpaaRating","length","usaBoxOffice","tagline"),"coordinates",List.of("x","y"),"director",List.of("name","birthday","passportID"),"director.location",List.of("x","y","name"));
            for(var entry:required.entrySet()) for(String key:entry.getValue()) for(boolean missing:List.of(false,true)) {
                String group=entry.getKey();
                cases.add(DynamicTest.dynamicTest("required "+group+"."+key+" missing="+missing,()->{
                    var doc=base.deepCopy(); var node=(com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(0);
                    for(String part:group.split("\\.")) if(!part.isEmpty()) node=(com.fasterxml.jackson.databind.node.ObjectNode)node.get(part);
                    if(missing) node.remove(key); else node.putNull(key);
                    Problem p=assertThrows(Problem.class,()->new ImportParser().parse(bytes(doc)));
                    assertEquals(400,p.status); assertEquals(1,p.recordNumber); assertNotNull(p.path);
                }));
            }
            Map<String,List<String>> invalid=new LinkedHashMap<>();
            for(String key:List.of("oscarsCount","budget","totalBoxOffice","length","goldenPalmCount","usaBoxOffice","director.height","director.weight")) invalid.put(key,List.of("0","-1"));
            invalid.put("coordinates.x",List.of("827","2147483648","1.1","true","\"1\""));
            invalid.put("coordinates.y",List.of("2147483648","1.2","false"));
            invalid.put("budget",List.of("0","-1","9223372036854775808","\"9223372036854775808\"","1.1","true","\"1.0\""));
            invalid.put("goldenPalmCount",List.of("0","-1","9223372036854775808","1.1"));
            invalid.put("length",List.of("0","-1","2147483648","1.0"));
            invalid.put("mpaaRating",List.of("\"BAD\"","1")); invalid.put("genre",List.of("\"BAD\""));
            invalid.put("director.eyeColor",List.of("\"BAD\"")); invalid.put("director.hairColor",List.of("\"BAD\""));
            invalid.put("director.birthday",List.of("\"2000-01-01T00:00\"","\"invalid\""));
            invalid.put("director.height",List.of("0","-1","1e100","1e-100")); invalid.put("director.weight",List.of("0","-1","1e100","1e-100"));
            invalid.put("director.location.x",List.of("9223372036854775808","1.1")); invalid.put("director.location.y",List.of("1e999","\"Infinity\""));
            invalid.put("totalBoxOffice",List.of("0","-1","1e999","\"NaN\"","100"));
            for(var entry:invalid.entrySet()) for(String value:entry.getValue()) {
                String path=entry.getKey(); cases.add(DynamicTest.dynamicTest("invalid "+path+"="+value,()->{
                    var doc=base.deepCopy(); var node=(com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(0); String[] parts=path.split("\\.");
                    for(int i=0;i<parts.length-1;i++) node=(com.fasterxml.jackson.databind.node.ObjectNode)node.get(parts[i]);
                    node.set(parts[parts.length-1],json.readTree(value));
                    assertEquals(400,assertThrows(Problem.class,()->new ImportParser().parse(bytes(doc))).status);
                }));
            }
            return cases.stream();
        }

        @Test void F04_F05_F06_validBoundaries() throws Exception {
            var doc=document(); var m=(com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(0);
            m.put("budget","9223372036854775807"); m.put("goldenPalmCount",9223372036854775807L);
            m.put("usaBoxOffice",1); m.put("totalBoxOffice",1); m.put("oscarsCount",1); m.put("length",1); m.put("tagline","");
            ((com.fasterxml.jackson.databind.node.ObjectNode)m.get("coordinates")).put("x",826).put("y",Integer.MIN_VALUE);
            ((com.fasterxml.jackson.databind.node.ObjectNode)m.path("director").path("location")).put("x",Long.MIN_VALUE).put("y",-2).put("name","");
            assertEquals(Long.MAX_VALUE,new ImportParser().parse(bytes(doc)).movies().get(0).budget);
            m.putNull("totalBoxOffice"); assertEquals(2,new ImportParser().parse(bytes(doc)).movies().size());
        }

        @Test void F03_U06_lastDuplicateRollsBackAllNestedObjects() throws Exception {
            user("ordinary_a"); var doc=document(); var rows=(com.fasterxml.jackson.databind.node.ArrayNode)doc.get("movies"); rows.add(rows.get(0).deepCopy());
            long revision=service.revision(); Problem p=assertThrows(Problem.class,()->importer().upload("ordinary_a","duplicate.json",bytes(doc)));
            assertEquals("DUPLICATE_MOVIE",p.code); assertEquals(3,p.recordNumber); assertEquals(List.of(0L,0L,0L,0L),domains());
            assertEquals(revision,service.revision()); assertEquals("FAILED",history().get("ordinary_a",p.operationId).get("status"));
        }

        @Test void F08_failureAfterActualInsertFlush() throws Exception {
            user("ordinary_a");
            MovieService injected=new MovieService(db) { @Override public Movie saveImported(jakarta.persistence.EntityManager em,Movie m) { super.saveImported(em,m); assertNotNull(m.id); throw new IllegalStateException("test: after actual first flush"); } };
            Problem p=assertThrows(Problem.class,()->new ImportService(db,injected).upload("ordinary_a","flush.json",fixture()));
            assertEquals(500,p.status); assertEquals(List.of(0L,0L,0L,0L),domains()); assertEquals("FAILED",history().get("ordinary_a",p.operationId).get("status"));
        }

        @Test void F09_actualDeferredCommitFailure() throws Exception {
            user("ordinary_a");
            try(Statement s=connection.createStatement()) {
                s.execute("CREATE FUNCTION lab2_test_commit_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'test deferred commit' USING ERRCODE='23514'; END $$");
                s.execute(sql("CREATE CONSTRAINT TRIGGER lab2_test_commit_failure AFTER INSERT ON movie DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION lab2_test_commit_failure()"));
                try {
                    Problem p=assertThrows(Problem.class,()->importer().upload("ordinary_a","commit.json",fixture()));
                    assertEquals(500,p.status); assertEquals(List.of(0L,0L,0L,0L),domains()); assertEquals("FAILED",history().get("ordinary_a",p.operationId).get("status"));
                } finally {
                    s.execute(sql("DROP TRIGGER lab2_test_commit_failure ON movie")); s.execute("DROP FUNCTION lab2_test_commit_failure()");
                }
            }
        }

        @Test void F07_personConflictAfterEarlierRowsAndExistingPersonImmutable() throws Exception {
            user("ordinary_a"); importer().upload("ordinary_a","first.json",fixture());
            var doc=document(); var rows=doc.path("movies");
            ((com.fasterxml.jackson.databind.node.ObjectNode)rows.get(0)).put("name","Unique 1");
            ((com.fasterxml.jackson.databind.node.ObjectNode)rows.get(1)).put("name","Unique 2");
            ((com.fasterxml.jackson.databind.node.ObjectNode)rows.get(1).get("director")).put("name","Changed");
            Problem p=assertThrows(Problem.class,()->importer().upload("ordinary_a","conflict.json",bytes(doc)));
            assertEquals("PERSON_DATA_CONFLICT",p.code); assertEquals(List.of(2L,1L,2L,1L),domains());
            assertEquals("Example Director",((Person)service.all("people").get(0)).name);
            ((com.fasterxml.jackson.databind.node.ObjectNode)rows.get(1).get("director")).put("name","Example Director");
            importer().upload("ordinary_a","reuse.json",bytes(doc)); assertEquals(List.of(4L,1L,4L,1L),domains());
        }

        @Test void F07_personAcrossRolesNullOmissionAndTimezoneIdentity() throws Exception {
            user("ordinary_a"); var doc=document();
            var first=(com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(0);
            var second=(com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(1);
            first.set("screenwriter",first.get("director").deepCopy()); first.set("operator",first.get("director").deepCopy());
            ((com.fasterxml.jackson.databind.node.ObjectNode)second.get("director")).put("birthday","1980-01-02T12:00+03:00");
            importer().upload("ordinary_a","roles.json",bytes(doc)); assertEquals(1,count(Person.class));
            Movie stored=(Movie)service.all("movies").get(0);assertEquals(stored.director.id,stored.screenwriter.id);assertEquals(stored.director.id,stored.operator.id);
            first.put("name","Timezone identity"); second.put("name","Timezone identity two");
            ((com.fasterxml.jackson.databind.node.ObjectNode)first.get("director")).put("birthday","1980-01-02T12:00+03:00[Europe/Moscow]");
            assertEquals("PERSON_DATA_CONFLICT",assertThrows(Problem.class,()->importer().upload("ordinary_a","zone.json",bytes(doc))).code);
            assertEquals(2,count(Movie.class));
        }

        @Test void F10_syntaxUnknownGeneratedAndEncodingFailuresKeepHistory() throws Exception {
            user("ordinary_a");
            for(String text:List.of("[]","{}","{\"formatVersion\":1,\"movies\":[]}","{\"formatVersion\":1,\"formatVersion\":1,\"movies\":[]}","{} {}","{bad", "{\"formatVersion\":1,}")) {
                Problem p=assertThrows(Problem.class,()->importer().upload("ordinary_a","bad.json",text.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
                assertEquals(400,p.status); assertEquals("FAILED",history().get("ordinary_a",p.operationId).get("status"));
            }
            assertEquals(400,assertThrows(Problem.class,()->new ImportParser().parse(new byte[]{(byte)0xff})).status);
            for(String key:List.of("id","version","creationDate","directorId","userId","unknown")) {
                var doc=document(); ((com.fasterxml.jackson.databind.node.ObjectNode)doc.path("movies").get(0)).put(key,1);
                assertThrows(Problem.class,()->new ImportParser().parse(bytes(doc)));
            }
            assertThrows(Problem.class,()->new ImportParser().parse(new byte[ImportParser.maxBytes()+1]));
            byte[] bom=new byte[fixture().length+3]; bom[0]=(byte)0xef; bom[1]=(byte)0xbb; bom[2]=(byte)0xbf; System.arraycopy(fixture(),0,bom,3,fixture().length);
            assertEquals(2,new ImportParser().parse(bom).movies().size()); assertEquals(List.of(0L,0L,0L,0L),domains());
        }

        @Test void U01_U02_U03_U04_U05_U07_identityNullPartialAndExactNames() {
            Coordinates c=coord(); Person p=person(null);
            Movie a=(Movie)service.save("movies",null,data(c.id,"A",1,null));
            assertEquals("DUPLICATE_MOVIE",assertThrows(Problem.class,()->service.save("movies",null,data(c.id,"A",1,null))).code);
            var directed=data(c.id,"A",1,null); directed.put("director",p.id); Movie b=(Movie)service.save("movies",null,directed);
            assertEquals(409,assertThrows(Problem.class,()->service.save("movies",b.id,new HashMap<>(Map.of("version",b.version)){{put("director",null);}})).status);
            Movie self=(Movie)service.save("movies",a.id,Map.of("name","A","version",a.version)); assertNotNull(self);
            for(String name:List.of("a"," A","A ","A|")) service.save("movies",null,data(c.id,name,1,null));
            Person second=(Person)service.save("people",null,Map.of("name",p.name,"birthday",p.birthday.toString(),"passportID","different-passport"));
            directed.put("director",second.id); service.save("movies",null,directed);
            service.save("people",p.id,Map.of("version",p.version,"name","Renamed","passportID","new-passport"));
            directed.put("director",p.id); assertEquals(409,assertThrows(Problem.class,()->service.save("movies",null,directed)).status);
            assertEquals(7,count(Movie.class));
        }

        @Test void H01_H02_H03_H04_historyPermissionsPaginationAndReopen() throws Exception {
            users(); var a=importer().upload("ordinary_a","a.json",fixture());
            assertThrows(Problem.class,()->importer().upload("ordinary_b","bad.json",fixture()));
            long id=Long.parseLong(a.get("operationId").toString());
            assertEquals(1L,history().list("ordinary_a",0,10).get("total")); assertEquals(1L,history().list("ordinary_b",0,10).get("total"));
            assertEquals(2L,history().list("admin_a",0,1).get("total")); assertEquals(1,((List<?>)history().list("admin_b",0,1).get("items")).size());
            assertEquals(404,assertThrows(Problem.class,()->history().get("ordinary_b",id)).status);
            Database reopened=new Database(); reopened.init();
            try { assertEquals("SUCCESS",new ImportHistoryService(reopened).get("admin_a",id).get("status")); assertEquals(UserRole.ADMIN,new AuthService(reopened).identity("admin_a").role); }
            finally { reopened.close(); }
        }

        @Test void C03_C04_concurrentCreatesOneCommit() throws Exception {
            Coordinates c=coord(); Person p=person(null);
            for(boolean director:List.of(false,true)) {
                var data=data(c.id,"race-"+director,1,null); if(director)data.put("director",p.id);
                ExecutorService executor=Executors.newFixedThreadPool(4); CyclicBarrier barrier=new CyclicBarrier(4);
                List<Callable<Integer>> calls=new ArrayList<>();
                for(int i=0;i<4;i++)calls.add(()->{barrier.await(10,TimeUnit.SECONDS);try{service.save("movies",null,data);return 201;}catch(Problem e){assertEquals("DUPLICATE_MOVIE",e.code);return e.status;}});
                try { var results=executor.invokeAll(calls); List<Integer> statuses=new ArrayList<>();for(var f:results)statuses.add(f.get(20,TimeUnit.SECONDS));Collections.sort(statuses);assertEquals(List.of(201,409,409,409),statuses); }
                finally{executor.shutdownNow();}
            }
        }

        @Test void C11_H06_deterministicNoPartialReadBeforeCommitAndRollback() throws Exception {
            user("ordinary_a");
            for(boolean rollback:List.of(true,false)) {
                long before=count(Movie.class); CountDownLatch flushed=new CountDownLatch(1),release=new CountDownLatch(1);
                MovieService paused=new MovieService(db){@Override public Movie saveImported(jakarta.persistence.EntityManager em,Movie m){super.saveImported(em,m);flushed.countDown();try{assertTrue(release.await(15,TimeUnit.SECONDS));}catch(InterruptedException e){throw new RuntimeException(e);}if(rollback)throw new IllegalStateException("test rollback after pause");return m;}};
                ExecutorService executor=Executors.newSingleThreadExecutor();
                Future<?> f=executor.submit(()->new ImportService(db,paused).upload("ordinary_a","pause.json",uncheckedFixture()));
                try {
                    assertTrue(flushed.await(15,TimeUnit.SECONDS)); assertEquals(before,count(Movie.class));
                    var latest=(Map<?,?>)((List<?>)history().list("ordinary_a",0,10).get("items")).get(0);assertEquals("RUNNING",latest.get("status"));assertNull(latest.get("addedCount"));
                    release.countDown(); if(rollback)assertThrows(ExecutionException.class,()->f.get(20,TimeUnit.SECONDS));else f.get(20,TimeUnit.SECONDS);
                    assertEquals(before+(rollback?0:2),count(Movie.class));
                }finally{release.countDown();executor.shutdownNow();}
            }
        }
        byte[] uncheckedFixture(){try{return fixture();}catch(Exception e){throw new RuntimeException(e);}}

        @Test void isolationAndRealLockTimeout() throws Exception {
            String expected=Database.config("MOVIE_ISOLATION","READ COMMITTED").toLowerCase();
            assertEquals(expected,db.write(em->em.createNativeQuery("SHOW transaction_isolation").getSingleResult().toString()));
            assertEquals("read committed",db.metadata(em->em.createNativeQuery("SHOW transaction_isolation").getSingleResult().toString()));
            System.out.println("LAB2_ACTUAL_BUSINESS_ISOLATION="+expected+"; METADATA=read committed; LOCK=AppState FOR UPDATE");
            connection.setAutoCommit(false);try(Statement s=connection.createStatement()){
                s.execute(sql("SELECT id FROM app_state WHERE id=1 FOR UPDATE")); System.setProperty("MOVIE_LOCK_TIMEOUT_MS","200");
                long start=System.nanoTime(); RuntimeException error=assertThrows(RuntimeException.class,()->coord());
                assertEquals("55P03",Database.sqlState(error)); long elapsed=TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-start); assertTrue(elapsed>=150 && elapsed<5000);
                System.out.println("LAB2_LOCK_TIMEOUT_MS="+elapsed+" SQLSTATE=55P03");
            }finally{System.clearProperty("MOVIE_LOCK_TIMEOUT_MS");connection.rollback();connection.setAutoCommit(true);}
        }

        @Test void U08_databaseHasNoMovieCombinationUniqueOrTrigger() throws Exception {
            try(Statement s=connection.createStatement();ResultSet rs=s.executeQuery(sql("SELECT count(*) FROM pg_constraint WHERE conrelid='movie'::regclass AND contype='u'"))) {rs.next();assertEquals(0,rs.getInt(1));}
            try(Statement s=connection.createStatement();ResultSet rs=s.executeQuery(sql("SELECT count(*) FROM pg_trigger WHERE tgrelid='movie'::regclass AND NOT tgisinternal"))) {rs.next();assertEquals(0,rs.getInt(1));}
            try(Statement s=connection.createStatement();ResultSet rs=s.executeQuery(sql("SELECT count(*) FROM pg_index WHERE indrelid='movie'::regclass AND indisunique AND NOT indisprimary"))) {rs.next();assertEquals(0,rs.getInt(1));}
        }
    }
}
