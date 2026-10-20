package ru.itmo.movie.domain.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.*;

@Documented
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = BoxOfficeValidator.class)
public @interface ConsistentBoxOffice {
    String message() default "Сборы в США не могут превышать общие сборы.";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
