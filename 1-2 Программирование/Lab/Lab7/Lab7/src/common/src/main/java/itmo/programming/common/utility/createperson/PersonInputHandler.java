package itmo.programming.common.utility.createperson;

import itmo.programming.common.exceptions.FieldException;
import itmo.programming.common.exceptions.UserExitException;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Coordinates;
import itmo.programming.common.person.EyeColor;
import itmo.programming.common.person.HairColor;
import itmo.programming.common.person.Location;
import itmo.programming.common.person.Person;
import java.time.LocalDateTime;

/**
 * Обработчик ввода данных человеком.
 */
public class PersonInputHandler {
    private final InputHandler inputHandler;

    /**
     * Конструктор.
     */
    public PersonInputHandler(InputHandler inputHandler) {
        this.inputHandler = inputHandler;
    }

    /**
     * Создать человека с введенными данными.
     *
     * @return человек
     */
    public Person createPersonFromInput() {
        try {
            final Person.Builder builder = buildPersonBuilder();
            return builder.build();
        } catch (UserExitException e) {
            final Response response = e.getResponse();
            return null;
        } catch (FieldException e) {
            System.out.println("Ошибка при создании объекта: " + e.getMessage());
            return null;
        }
    }

    /**
     * Создать человека с введенными данными(Использовать указанный идентификатор для обновления).
     *
     * @param id идентификатор
     * @return человек
     */
    public Person createPersonFromInputWithId(long id) {
        try {
            final Person.Builder builder = buildPersonBuilder();
            return builder.buildUpdate(id);
        } catch (UserExitException e) {
            System.out.println(e.getMessage());
            return null;
        } catch (FieldException e) {
            System.out.println("Ошибка при создании объекта: " + e.getMessage());
            return null;
        }
    }

    /**
     * Получить строитель.
     *
     * @return Person.Builder
     * @throws UserExitException UserExitException
     * @throws FieldException    FieldException
     */
    private Person.Builder buildPersonBuilder() throws UserExitException, FieldException {
        final Person.Builder builder = new Person.Builder();

        final String name = inputHandler.readString("Name: ");

        final float coordinatesX = inputHandler.readFloat("Coordinates x(float): ");
        final long coordinatesY = inputHandler.readLong(
                "Coordinates y(long,max=797): ", 797L, Long.MIN_VALUE);
        final Coordinates coordinates = new Coordinates(coordinatesX, coordinatesY);

        final long height = inputHandler.readLong("Height(long,min=0): ", null, 0L);

        final LocalDateTime birthday =
                inputHandler.readDateTime("Birthday(Формат времени:yyyy/MM/dd HH:mm): ");

        final EyeColor eyeColor = inputHandler.readEnum(EyeColor.class, "EyeColor: ");

        final HairColor hairColor = inputHandler.readEnum(HairColor.class, "HairColor: ");

        final double locX = inputHandler.readDouble("Locations x(double): ");
        final int locY = (int) inputHandler.readFloat("Locations y(int): ");
        final int locZ = (int) inputHandler.readFloat("Locations z(int): ");
        final Location location = new Location(locX, locY, locZ);

        return builder.name(name)
                .coordinates(coordinates)
                .height(height)
                .birthday(birthday)
                .eyeColor(eyeColor)
                .hairColor(hairColor)
                .location(location);
    }
}
