package ru.itmo.movie;

import jakarta.validation.Validation;
import org.junit.jupiter.api.Test;
import ru.itmo.movie.domain.Movie;
import ru.itmo.movie.domain.validation.ConsistentBoxOffice;

import static org.junit.jupiter.api.Assertions.*;

class BoxOfficeValidatorTest {
    @Test
    void classConstraintMapsErrorToEditableFieldAndAllowsUnknownTotal() {
        try (var factory = Validation.buildDefaultValidatorFactory()) {
            var validator = factory.getValidator();
            Movie movie = new Movie();
            movie.usaBoxOffice = 200;
            movie.totalBoxOffice = 199.5;
            var errors = validator.validate(movie).stream()
                    .filter(v -> v.getConstraintDescriptor().getAnnotation() instanceof ConsistentBoxOffice).toList();
            assertEquals(1, errors.size());
            assertEquals("usaBoxOffice", errors.get(0).getPropertyPath().toString());
            assertTrue(errors.get(0).getMessage().contains("Сборы в США"));
            for (Double total : new Double[]{null, 200.0, 200.5}) {
                movie.totalBoxOffice = total;
                assertTrue(validator.validate(movie).stream()
                        .noneMatch(v -> v.getConstraintDescriptor().getAnnotation() instanceof ConsistentBoxOffice));
            }
        }
    }
}
