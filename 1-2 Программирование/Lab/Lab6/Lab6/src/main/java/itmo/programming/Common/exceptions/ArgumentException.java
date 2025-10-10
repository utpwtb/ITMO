package itmo.programming.Common.exceptions;

import itmo.programming.Common.NetWork.Response;

import java.io.Serial;
import java.io.Serializable;

/**
 * Класс исключения параметра.
 */
public class ArgumentException extends RuntimeException implements Serializable {
    @Serial
    private static final long serialVersionUID = -7613142842607022232L;
    private String message;

    /**
     * Конструктор.
     */
    public ArgumentException(String message) {
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
