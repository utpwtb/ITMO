package itmo.programming.Common.utility.createperson;

import itmo.programming.Common.exceptions.NoSuchColorException;
import itmo.programming.Common.utility.NumberParserUtils;
import itmo.programming.Common.person.Coordinates;
import itmo.programming.Common.person.EyeColor;
import itmo.programming.Common.person.HairColor;
import itmo.programming.Common.person.Location;
import itmo.programming.Common.person.Person;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;

/**
 * Обработчик входных данных скрипта.
 */
public class ScriptInputHandler {
    /**
     * Очередь для хранения параметров.
     */
    private final Queue<String> inputQueue;

    /**
     * конструктор.
     *
     * @param args массив параметров
     */
    public ScriptInputHandler(String[] args) {
        this.inputQueue = new LinkedList<>(Arrays.asList(args));
    }

    /**
     * создать человека через строитель.
     *
     * @return человек
     */
    public Person createPersonFromScript() {
        try {
            final Person.Builder builder = buildFromScript();
            return builder.build();
        } catch (NumberFormatException e) {
            System.out.println("Ошибка формата числа в скрипте: " + e.getMessage());
            return null;
        } catch (DateTimeParseException e) {
            System.out.println("Ошибка формата даты в скрипте.Используйте формат yyyy/MM/dd HH:mm");
            return null;
        } catch (IllegalArgumentException e) {
            System.out.println("Ошибка в скрипте: " + e.getMessage());
            return null;
        }
    }

    /**
     * создать человека через строитель(Использовать указанный идентификатор для обновления).
     *
     * @param id идентификатор
     * @return человек
     */
    public Person createPersonFromScriptWithId(long id) {
        try {
            final Person.Builder builder = buildFromScript();
            return builder.buildUpdate(id);
        } catch (NumberFormatException e) {
            System.out.println("Ошибка формата числа в скрипте: " + e.getMessage());
            return null;
        } catch (DateTimeParseException e) {
            System.out.println("Ошибка формата даты в скрипте.Используйте формат yyyy/MM/dd HH:mm");
            return null;
        } catch (IllegalArgumentException e) {
            System.out.println("Ошибка в скрипте: " + e.getMessage());
            return null;
        }
    }

    /**
     * получить строителя.
     *
     * @return строители
     */
    public Person.Builder buildFromScript() {
        final String name = inputQueue.poll();

        final float coordinatesX = NumberParserUtils.parseFloat(inputQueue.poll());
        final long coordinatesY = Long.parseLong(inputQueue.poll());

        final long height = Long.parseLong(inputQueue.poll());

        final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm");
        final LocalDateTime birthday = LocalDateTime.parse(inputQueue.poll(), formatter);

        final String eyeColorStr = inputQueue.poll();
        final EyeColor eyeColor;
        try {
            eyeColor = Enum.valueOf(EyeColor.class, eyeColorStr.toUpperCase());
        } catch (NoSuchColorException e) {
            throw new NoSuchColorException("Неверное значение для цвета глаз: " + eyeColorStr);
        }

        final String hairColorStr = inputQueue.poll();
        final HairColor hairColor;
        try {
            hairColor = Enum.valueOf(HairColor.class, hairColorStr.toUpperCase());
        } catch (NoSuchColorException e) {
            throw new NoSuchColorException("Неверное значение для цвета волос: " + hairColorStr);
        }

        final double locationX = NumberParserUtils.parseDouble(inputQueue.poll());
        final int locationY = Integer.parseInt(inputQueue.poll());
        final int locationZ = Integer.parseInt(inputQueue.poll());

        return new Person.Builder()
                .name(name)
                .coordinates(new Coordinates(coordinatesX, coordinatesY))
                .height(height)
                .birthday(birthday)
                .eyeColor(eyeColor)
                .hairColor(hairColor)
                .location(new Location(locationX, locationY, locationZ));
    }
}
