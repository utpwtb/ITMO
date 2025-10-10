package utlity;

import Exceptions.UserExitException;
import Exceptions.FieldException;
import person.Coordinates;
import person.EyeColor;
import person.HairColor;
import person.Location;
import person.Person;

import java.time.LocalDateTime;

/**
 * Обработчик ввода данных человеком
 */
public class PersonInputHandler {
    private final InputHandler inputHandler;

    public PersonInputHandler(InputHandler inputHandler) {
        this.inputHandler = inputHandler;
    }

    /**
     * Создать человека с введенными данными
     * @return человек
     */
    public Person createPersonFromInput() {
        try {
            Person.Builder builder = buildPersonBuilder();
            return builder.build();
        } catch (UserExitException e) {
            System.out.println(e.getMessage());
            return null;
        } catch (FieldException e) {
            System.out.println("Ошибка при создании объекта: " + e.getMessage());
            return null;
        }
    }

    /**
     *Создать человека с введенными данными(Использовать указанный идентификатор для обновления)
     * @param id идентификатор
     * @return человек
     */
    public Person createPersonFromInputWithId(long id) {
        try {
            Person.Builder builder = buildPersonBuilder();
            return builder.buildUpdate(id);
        } catch (UserExitException e) {
            System.out.println(e.getMessage());
            return null;
        } catch (FieldException e) {
            System.out.println("Ошибка при создании объекта: " + e.getMessage());
            return null;
        }
    }

    private Person.Builder buildPersonBuilder() throws UserExitException, FieldException {
        Person.Builder builder = new Person.Builder();

        String name = inputHandler.readString("Name: ");

        float x_Coordinates = inputHandler.readFloat("Coordinates x: ");
        long y_Coordinates = inputHandler.readLong("Coordinates y: ", 797L, Long.MIN_VALUE);
        Coordinates coordinates = new Coordinates(x_Coordinates, y_Coordinates);


        long height = inputHandler.readLong("Height: ", null, 0L);

        LocalDateTime birthday = inputHandler.readDateTime("Birthday(Формат времени:yyyy/MM/dd HH:mm): ");

        EyeColor eyeColor = inputHandler.readEnum(EyeColor.class, "EyeColor: ");

        HairColor hairColor = inputHandler.readEnum(HairColor.class, "HairColor: ");

        double x_loc = inputHandler.readFloat("Locations x: ");
        int y_loc = (int) inputHandler.readFloat("Locations y: ");
        int z_loc = (int) inputHandler.readFloat("Locations z: ");
        Location location = new Location(x_loc, y_loc, z_loc);

        return builder
                .name(name)
                .coordinates(coordinates)
                .height(height)
                .birthday(birthday)
                .eyeColor(eyeColor)
                .hairColor(hairColor)
                .location(location);
    }

} 