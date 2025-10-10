package itmo.programming.Common.exceptions;

/**
 * Класс исключения, где указанный цвет не существует.
 */
public class NoSuchColorException extends RuntimeException {
    /**
     * Конструктор.
     */
    public NoSuchColorException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
