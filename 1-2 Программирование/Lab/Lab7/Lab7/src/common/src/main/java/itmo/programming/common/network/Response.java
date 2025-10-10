package itmo.programming.common.network;

import java.io.Serial;
import java.io.Serializable;

/**
 * Класс ответа, который отправляется от сервера к клиенту.
 * Содержит сообщение и строковое представление коллекции.
 */
public class Response implements Serializable {
    @Serial
    private static final long serialVersionUID = 6371468372929910569L;
    
    /**
     * Сообщение ответа.
     */
    private String message;
    
    /**
     * Строковое представление коллекции.
     */
    private String collectionToStr;

    /**
     * Конструктор для создания ответа с сообщением и строковым представлением коллекции.
     *
     * @param message сообщение ответа
     * @param collectionToStr строковое представление коллекции
     */
    public Response(String message, String collectionToStr) {
        this.message = message;
        this.collectionToStr = collectionToStr != null ? collectionToStr : "";
    }

    /**
     * Конструктор по умолчанию для создания пустого ответа.
     */
    public Response() {
    }

    /**
     * Получить сообщение ответа.
     *
     * @return сообщение ответа
     */
    public String getMessage() {
        return message;
    }

    /**
     * Установить сообщение ответа.
     *
     * @param message сообщение ответа
     */
    public void setMessage(String message) {
        this.message = message;
    }

    /**
     * Получить строковое представление коллекции.
     *
     * @return строковое представление коллекции
     */
    public String getCollectionToStr() {
        return collectionToStr;
    }

    /**
     * Установить строковое представление коллекции.
     *
     * @param collectionToStr строковое представление коллекции
     */
    public void setCollectionToStr(String collectionToStr) {
        this.collectionToStr = collectionToStr;
    }

    /**
     * Преобразовать объект в строку.
     *
     * @return строковое представление объекта
     */
    @Override
    public String toString() {
        return "Response{message = " + message + ", collectionToStr = " + collectionToStr + "}";
    }
}
