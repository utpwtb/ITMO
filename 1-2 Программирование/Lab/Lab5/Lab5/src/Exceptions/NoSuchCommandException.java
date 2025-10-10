package Exceptions;

/**
 * Класс исключений для указанной команды не существует.
 */
public class NoSuchCommandException extends RuntimeException{
    /**
     * Конструктор
     */
    public NoSuchCommandException(String message){
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
