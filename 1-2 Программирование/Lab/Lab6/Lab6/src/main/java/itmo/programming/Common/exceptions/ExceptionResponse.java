package itmo.programming.Common.exceptions;

import java.io.Serial;
import java.io.Serializable;

public class ExceptionResponse extends RuntimeException implements Serializable {
    @Serial
    private static final long serialVersionUID = 5772955605918853689L;
    private String message;

    public ExceptionResponse() {
    }

    public ExceptionResponse(String message) {
        this.message = message;
    }

    /**
     * 获取
     * @return message
     */
    public String getMessage() {
        return message;
    }

    /**
     * 设置
     * @param message
     */
    public void setMessage(String message) {
        this.message = message;
    }

    public String toString() {
        return "ExceptionResponse{message = " + message + "}";
    }
}
