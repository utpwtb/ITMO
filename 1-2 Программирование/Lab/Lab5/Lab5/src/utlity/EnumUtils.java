package utlity;

import java.util.Locale;

/**
 * Класс перечисления класс инструмента
 */
public class EnumUtils {
    /**
     * Отображение полей класса перечисления
     * @param enumClass Указанный класс перечисления
     * @return Строка, указывающая поле класса перечисления
     */
    public static String showEnum(Class<? extends Enum<?>> enumClass) {
        StringBuilder enumList = new StringBuilder();
        for (Enum<?> enumConstant : enumClass.getEnumConstants()) {
            enumList.append(enumConstant.name()).append(" ");
        }
        return enumList.toString();
    }

    /**
     * Преобразует строку в поле указанного класса перечисления.
     * @param enumType Указанный класс перечисления
     * @param value строка
     * @return Укажите поля класса перечисления
     * @param <T> казанный класс перечисления
     */
    public static <T extends Enum<T>> T fromStringIgnoreCase(Class<T> enumType, String value) {
        if (value == null || enumType == null) return null;
        String upperValue = value.trim().toUpperCase(Locale.ENGLISH);

        for (T enumConstant : enumType.getEnumConstants()) {
            if (enumConstant.name().equals(upperValue)) {
                return enumConstant;
            }
        }
        return null;
    }


}
