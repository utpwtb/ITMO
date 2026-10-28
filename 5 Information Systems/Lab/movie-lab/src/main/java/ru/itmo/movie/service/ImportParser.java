package ru.itmo.movie.service;

import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import jakarta.validation.constraints.NotNull;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.charset.*;
import java.time.*;
import java.util.*;
import ru.itmo.movie.domain.*;
import ru.itmo.movie.persistence.Database;

/** Strict UTF-8, duplicate detection and exact integer conversion before domain validation. */
public class ImportParser {
    private static final ObjectMapper JSON = new ObjectMapper(JsonFactory.builder()
            .enable(StreamReadFeature.STRICT_DUPLICATE_DETECTION).build())
            .enable(DeserializationFeature.USE_BIG_INTEGER_FOR_INTS)
            .enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS);
    public record ImportDocument(int formatVersion, List<Movie> movies) {}
    public static int maxBytes() { return Integer.parseInt(Database.config("MOVIE_IMPORT_MAX_BYTES", "5242880")); }
    public static int maxMovies() { return Integer.parseInt(Database.config("MOVIE_IMPORT_MAX_MOVIES", "1000")); }

    public ImportDocument parse(byte[] bytes) {
        if (bytes.length > maxBytes()) throw new Problem(413, "FILE_TOO_LARGE", "Файл превышает допустимый размер");
        JsonNode root;
        try {
            String text = StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString();
            if (text.startsWith("\uFEFF")) text = text.substring(1);
            root = JSON.readTree(text);
        } catch (Exception e) { throw new Problem(400, "INVALID_JSON", "Требуется корректный UTF-8 JSON без повторных свойств"); }
        if (root == null || !root.isObject()) throw new Problem(400, "INVALID_JSON", "Корень должен быть объектом");
        root.fieldNames().forEachRemaining(k -> { if (!Set.of("formatVersion", "movies").contains(k)) throw field(0, k); });
        if (!root.path("formatVersion").isIntegralNumber() || !root.path("formatVersion").bigIntegerValue().equals(java.math.BigInteger.ONE))
            throw field(0, "formatVersion");
        JsonNode rows = root.path("movies");
        if (!rows.isArray() || rows.isEmpty() || rows.size() > maxMovies()) throw field(0, "movies");
        List<Movie> movies = new ArrayList<>();
        for (int i = 0; i < rows.size(); i++) movies.add(object(rows.get(i), Movie.class, i + 1, "movies[" + i + "]"));
        return new ImportDocument(1, List.copyOf(movies));
    }

    private static Problem field(int row, String path) {
        var p = new Problem(400, "INVALID_FIELD", "Некорректное поле: " + path);
        if (row > 0) p.recordNumber = row;
        p.path = path;
        return p;
    }

    private <T> T object(JsonNode node, Class<T> type, int row, String path) {
        if (!node.isObject()) throw field(row, path);
        try {
            T result = type.getDeclaredConstructor().newInstance();
            Set<String> allowed = new HashSet<>();
            for (Field f : type.getFields()) {
                String key = f.getName();
                if (Modifier.isStatic(f.getModifiers()) || Set.of("id", "version", "creationDate").contains(key)) continue;
                allowed.add(key);
                JsonNode value = node.get(key);
                String full = path + "." + key;
                if (value == null || value.isNull()) {
                    if (f.getType().isPrimitive() || f.isAnnotationPresent(NotNull.class)) throw field(row, full);
                    f.set(result, null);
                } else f.set(result, value(value, f.getType(), row, full));
            }
            node.fieldNames().forEachRemaining(k -> { if (!allowed.contains(k)) throw field(row, path + "." + k); });
            if (result instanceof Movie m) m.creationDate = LocalDate.now();
            try { MovieService.validate(result); }
            catch (Problem p) { throw p.at(row, path + "." + p.path); }
            return result;
        } catch (ReflectiveOperationException e) { throw new IllegalStateException(e); }
    }

    private Object value(JsonNode node, Class<?> type, int row, String path) {
        try {
            if (type == String.class) { if (!node.isTextual()) throw field(row,path); return node.textValue(); }
            if (type == int.class || type == Integer.class) {
                if (!node.isIntegralNumber()) throw field(row,path);
                return node.bigIntegerValue().intValueExact();
            }
            if (type == long.class || type == Long.class) {
                if (node.isIntegralNumber()) return node.bigIntegerValue().longValueExact();
                if (node.isTextual() && node.textValue().matches("-?(0|[1-9][0-9]*)")) return Long.valueOf(node.textValue());
                throw field(row,path);
            }
            if (type == Float.class || type == Double.class) {
                if (!node.isNumber()) throw field(row,path);
                double d = node.doubleValue();
                if (!Double.isFinite(d)) throw field(row,path);
                if (type == Double.class) return d;
                float f = (float)d;
                if (!Float.isFinite(f) || f <= 0) throw field(row,path);
                return f;
            }
            if (type == ZonedDateTime.class) { if (!node.isTextual()) throw field(row,path); return ZonedDateTime.parse(node.textValue()); }
            if (type.isEnum()) { if (!node.isTextual()) throw field(row,path); return Enum.valueOf(type.asSubclass(Enum.class), node.textValue()); }
            return object(node,type,row,path);
        } catch (ArithmeticException | IllegalArgumentException | DateTimeException e) { throw field(row,path); }
    }
}
