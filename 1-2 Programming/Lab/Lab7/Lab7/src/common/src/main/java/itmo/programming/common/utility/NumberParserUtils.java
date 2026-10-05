package itmo.programming.common.utility;

/**
 * Класс инструмента числового анализа,
 * обеспечивающий поддержку запятых и точек в качестве десятичных знаков.
 */
public class NumberParserUtils {

    /**
     * Анализ чисел с плавающей точкой,
     * поддержка запятых и точек в качестве десятичных знаков.
     *
     * @param input Входная строка
     * @return Проанализированное число с плавающей точкой
     * @throws NumberFormatException Если введенное число не является допустимым
     */
    public static float parseFloat(String input) throws NumberFormatException {
        if (input == null || input.trim().isEmpty()) {
            throw new NumberFormatException("Ввод не может быть пустым");
        }
        final String normalizedInput = input.replace(',', '.');
        return Float.parseFloat(normalizedInput);
    }

    /**
     * Анализ чисел с плавающей точкой двойной точности,
     * поддержка запятых и точек в качестве десятичных знаков.
     *
     * @param input Входная строка
     * @return Проанализированное число с плавающей точкой двойной точности
     * @throws NumberFormatException Если введенное число не является допустимым
     */
    public static double parseDouble(String input) throws NumberFormatException {
        if (input == null || input.trim().isEmpty()) {
            throw new NumberFormatException("Ввод не может быть пустым");
        }
        final String normalizedInput = input.replace(',', '.');
        return Double.parseDouble(normalizedInput);
    }
}
