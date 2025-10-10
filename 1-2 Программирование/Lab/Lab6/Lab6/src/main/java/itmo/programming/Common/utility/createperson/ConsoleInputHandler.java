package itmo.programming.Common.utility.createperson;

import itmo.programming.Common.exceptions.NoSuchColorException;
import itmo.programming.Common.utility.EnumUtils;
import itmo.programming.Common.utility.NumberParserUtils;
import itmo.programming.Common.exceptions.UserExitException;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Scanner;

/**
 * Обработчик ввода консоли.
 */
public class ConsoleInputHandler implements InputHandler {
    /**
     * Команда остановки для ввода параметров.
     */
    private static final String EXIT_COMMAND = "exit";

    /**
     * сканер.
     */
    private final Scanner scanner;

    /**
     * Конструктор.
     *
     * @param scanner сканер
     */
    public ConsoleInputHandler(Scanner scanner) {
        this.scanner = scanner;
    }

    /**
     * Чтение строки.
     *
     * @param prompt запрос
     * @return строка
     */
    @Override
    public String readString(String prompt) {
        while (true) {
            System.out.println(prompt);

            final String input = scanner.nextLine().trim();

            if (input.equalsIgnoreCase(EXIT_COMMAND)) {
                throw new UserExitException("Операция отменена пользователем");
            }

            if (!input.isEmpty()) {
                return input;
            }
        }
    }

    /**
     * Чтение числа типа float.
     *
     * @param prompt запрос
     * @return число типа float
     */
    @Override
    public float readFloat(String prompt) {
        while (true) {
            try {
                final String input = readString(prompt);
                return NumberParserUtils.parseFloat(input);
            } catch (NumberFormatException e) {
                System.out.println("Неправильный формат числа. Повторите ввод.");
            }
        }
    }

    @Override
    public double readDouble(String prompt) {
        while (true) {
            try {
                final String input = readString(prompt);
                return NumberParserUtils.parseDouble(input);
            } catch (NumberFormatException e) {
                System.out.println("Неправильный формат числа. Повторите ввод.");
            }
        }
    }

    /**
     * Чтение числа типа long.
     *
     * @param prompt запрос
     * @return число типа long
     */
    @Override
    public long readLong(String prompt, Long maxValue, Long minValue) {
        while (true) {
            try {
                final long value = Long.parseLong(readString(prompt));
                if (maxValue != null && value > maxValue) {
                    System.out.println("Значение не может быть больше " + maxValue);
                    continue;
                }
                if (minValue != null && value < minValue) {
                    System.out.println("Значение должно быть больше " + minValue);
                    continue;
                }
                return value;
            } catch (NumberFormatException e) {
                System.out.println("Неправильный формат числа. Повторите ввод.");
            }
        }
    }

    /**
     * читать Дата Время.
     *
     * @param prompt запрос
     * @return Дата Время
     */
    @Override
    public LocalDateTime readDateTime(String prompt) {
        final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm");
        while (true) {
            try {
                final LocalDateTime dateTime = LocalDateTime.parse(readString(prompt), formatter);
                if (dateTime.isAfter(LocalDateTime.now())) {
                    System.out.println("Дата рождения не может быть в будущем");
                    continue;
                }
                return dateTime;
            } catch (DateTimeParseException e) {
                System.out.println(
                        "Неправильный формат времени. Используйте формат yyyy/MM/dd HH:mm");
            }
        }
    }

    /**
     * Чтение типов перечисления.
     *
     * @param enumClass тип перечисления
     * @param prompt    запрос
     * @param <T>       Указанный тип перечисления
     * @return типов перечисления
     */
    @Override
    public <T extends Enum<T>> T readEnum(Class<T> enumClass, String prompt) {
        while (true) {
            try {
                System.out.println(prompt);
                System.out.print("Доступные варианты: " + EnumUtils.showEnum(enumClass));
                final String input = readString("");

                final T result = EnumUtils.parseEnumInput(enumClass, input);
                if (result == null) {
                    throw new NoSuchColorException("Неверный ввод, попробуйте еще раз.");
                }
                return result;

            } catch (NoSuchColorException e) {
                System.out.println(e.getMessage());
            }
        }
    }

}
