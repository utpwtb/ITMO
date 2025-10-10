package itmo.programming.Common.utility.createperson;

import java.time.LocalDateTime;

/**
 * Обработчик ввода.
 */
public interface InputHandler {

    /**
     * Читать строку.
     *
     * @param prompt запрос
     * @return строка
     */
    String readString(String prompt);

    /**
     * Читать число типа float.
     *
     * @param prompt запрос
     * @return число типа float
     */
    float readFloat(String prompt);

    /**
     * Читать число типа double.
     *
     * @param prompt запрос
     * @return число типа double
     */
    double readDouble(String prompt);

    /**
     * Читать число типа long.
     *
     * @param prompt запрос
     * @return число типа long
     */
    long readLong(String prompt, Long maxValue, Long minValue);

    /**
     * Читать DateTime.
     *
     * @param prompt запрос
     * @return DateTime
     */
    LocalDateTime readDateTime(String prompt);

    /**
     * Читать Enum.
     *
     * @param prompt запрос
     * @return Enum
     */
    <T extends Enum<T>> T readEnum(Class<T> enumClass, String prompt);

}
