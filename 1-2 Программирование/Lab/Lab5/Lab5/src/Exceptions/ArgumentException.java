package Exceptions;

/**
 * Класс исключения параметра
 */
public class ArgumentException extends RuntimeException{
    /**
     * Конструктор
     */
    public ArgumentException(String message){
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
