package itmo.programming.common.exceptions;

import itmo.programming.common.network.Response;
import java.io.Serial;

/**
 * Класс исключения, возникающего когда указанный цвет не существует.
 */
public class NoSuchColorException extends RuntimeException {
    
    @Serial
    private static final long serialVersionUID = -9204130988630732521L;

    /**
     * Сообщение об ошибке.
     */
    private String message;

    /**
     * Конструктор исключения с указанным сообщением об ошибке.
     *
     * @param message сообщение об ошибке
     */
    public NoSuchColorException(String message) {
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
