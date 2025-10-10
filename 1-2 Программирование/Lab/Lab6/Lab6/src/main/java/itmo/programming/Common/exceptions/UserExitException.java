package itmo.programming.Common.exceptions;

import itmo.programming.Common.NetWork.Response;

import java.io.Serial;

/**
 * Класс исключения, который прекращает ввод составных параметров.
 */
public class UserExitException extends RuntimeException {
    @Serial
    private static final long serialVersionUID = -1098521026254666554L;
    private String message;
    /**
     * Конструктор.
     */
    public UserExitException(String message) {
        this.message = message;
    }

    public Response getResponse() {
        return new Response(message, "");
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
