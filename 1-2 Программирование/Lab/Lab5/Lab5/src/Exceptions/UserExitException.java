package Exceptions;

/**
 * Класс исключения, который прекращает ввод составных параметров
 */
public class UserExitException extends RuntimeException {
    /**
     * Конструктор
     */
    public UserExitException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}