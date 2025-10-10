package itmo.programming.Common.utility;

import java.util.Locale;

/**
 * Класс перечисления класс инструмента.
 */
public class EnumUtils {
    /**
     * Отображение полей класса перечисления.
     *
     * @param enumClass Указанный класс перечисления
     * @return Строка, указывающая поле класса перечисления
     */
    public static String showEnum(Class<? extends Enum<?>> enumClass) {
        final StringBuilder enumList = new StringBuilder();
        for (Enum<?> enumConstant : enumClass.getEnumConstants()) {
            enumList.append((
                            enumConstant.ordinal() + 1))
                    .append(".").append(enumConstant.name()).append(" ");
        }
        return enumList.toString();
    }

    /**
     * Преобразует строку в поле указанного класса перечисления.
     *
     * @param enumType Указанный класс перечисления
     * @param value    строка
     * @param <T>      указанный класс перечисления
     * @return Укажите поля класса перечисления
     */
    public static <T extends Enum<T>> T fromStringIgnoreCase(Class<T> enumType, String value) {
        if (value == null || enumType == null) {
            return null;
        }
        final String upperValue = value.trim().toUpperCase(Locale.ENGLISH);

        for (T enumConstant : enumType.getEnumConstants()) {
            if (enumConstant.name().equals(upperValue)) {
                return enumConstant;
            }
        }
        return null;
    }

    /**
     * Получить значение перечисления по его индексу.
     *
     * @param enumType Указанный класс перечисления
     * @param index    индекс
     * @param <T>      указанный класс перечисления
     * @return элемент класса перечисления
     */
    public static <T extends Enum<T>> T getById(Class<T> enumType, int index) {
        final T[] arr = enumType.getEnumConstants();
        if (index <= 0 || index > arr.length) {
            throw new IllegalArgumentException("Неверный индекс");
        }
        return arr[index];
    }

    /**
     * Получает значение перечисления по строке или номеру.
     *
     * @param enumType класс перечисления
     * @param input    входная строка (может быть именем или номером элемента перечисления)
     * @param <T>      тип перечисления
     * @return соответствующее значение перечисления, возвращает null если ввод некорректен
     */
    public static <T extends Enum<T>> T parseEnumInput(Class<T> enumType, String input) {
        if (input == null || input.trim().isEmpty()) {
            return null;
        }
        input = input.trim();
        try {
            final int index = Integer.parseInt(input);
            return getById(enumType, index);
        } catch (IllegalArgumentException e) {
            return fromStringIgnoreCase(enumType, input);
        }
    }

}
