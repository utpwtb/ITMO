package itmo.programming.Common.exceptions;

/**
 * Класс исключения для области действия поля.
 */
public class FieldException extends RuntimeException {
    /**
     * Конструктор.
     */
    public FieldException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
