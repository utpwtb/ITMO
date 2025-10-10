package itmo.programming.common.exceptions;

import itmo.programming.common.network.Response;
import java.io.Serial;

/**
 * Класс исключения для ошибок в полях объектов.
 */
public class FieldException extends RuntimeException {
    
    @Serial
    private static final long serialVersionUID = 7254085661137486861L;

    /**
     * Сообщение об ошибке.
     */
    private String message;

    /**
     * Конструктор исключения с указанным сообщением об ошибке.
     *
     * @param message сообщение об ошибке
     */
    public FieldException(String message) {
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
