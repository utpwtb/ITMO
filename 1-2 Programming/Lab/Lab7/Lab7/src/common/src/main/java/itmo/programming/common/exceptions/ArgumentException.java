package itmo.programming.common.exceptions;

import itmo.programming.common.network.Response;
import java.io.Serial;

/**
 * Класс исключения для ошибок в аргументах команды.
 */
public class ArgumentException extends RuntimeException {

    @Serial
    private static final long serialVersionUID = -8674710892259493092L;
    
    /**
     * Сообщение об ошибке.
     */
    private String message;

    /**
     * Конструктор исключения с указанным сообщением об ошибке.
     *
     * @param message сообщение об ошибке
     */
    public ArgumentException(String message) {
        super(message);
        this.message = message;
    }

    /**
     * Получить сообщение об ошибке.
     *
     * @return сообщение об ошибке
     */
    @Override
    public String getMessage() {
        return super.getMessage();
    }

    /**
     * Получить объект ответа с сообщением об ошибке.
     *
     * @return объект ответа
     */
    public Response getResponse() {
        return new Response(message, "");
    }
}
