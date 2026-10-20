package ru.itmo.movie.domain.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import ru.itmo.movie.domain.Movie;

public class BoxOfficeValidator implements ConstraintValidator<ConsistentBoxOffice, Movie> {
    @Override
    public boolean isValid(Movie movie, ConstraintValidatorContext context) {
        // 总票房可未知；格式、正数和有限值由各字段自身的约束处理。
        if (movie == null || movie.totalBoxOffice == null
                || !Double.isFinite(movie.totalBoxOffice) || movie.totalBoxOffice <= 0
                || movie.usaBoxOffice <= 0 || movie.usaBoxOffice <= movie.totalBoxOffice) return true;
        context.disableDefaultConstraintViolation();
        context.buildConstraintViolationWithTemplate(context.getDefaultConstraintMessageTemplate())
                .addPropertyNode("usaBoxOffice").addConstraintViolation();
        return false;
    }
}
