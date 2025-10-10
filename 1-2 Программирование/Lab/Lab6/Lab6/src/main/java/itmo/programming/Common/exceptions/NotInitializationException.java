package itmo.programming.Common.exceptions;

/**
 * Класс исключения, неинициализированный.
 */
public class NotInitializationException extends RuntimeException {
    /**
     * Конструктор.
     */
    public NotInitializationException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
