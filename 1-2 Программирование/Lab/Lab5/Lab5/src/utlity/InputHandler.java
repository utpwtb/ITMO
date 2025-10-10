package utlity;



import java.time.LocalDateTime;


/**
 * Обработчик ввода
 */
public interface InputHandler {
    String readString(String prompt);
    float readFloat(String prompt);
    long readLong(String prompt, Long maxValue,Long minValue);
    LocalDateTime readDateTime(String prompt);
    <T extends Enum<T>> T readEnum(Class<T> enumClass, String prompt);
} 