package Exceptions;

/**
 * Класс исключений формата данных
 */
public class FormatException extends RuntimeException{
    /**
     * Конструктор
     */
    public FormatException(String message){
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
