package itmo.programming.Common.person;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import itmo.programming.Common.exceptions.FieldException;

import java.io.Serial;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.HashSet;
import java.util.Objects;


/**
 * Класс человека.
 */
public class Person implements Serializable {
    /**
     * Коллекция сохраненных идентификаторов.
     */
    private static final HashSet<Long> idList = new HashSet<>();
    @Serial
    private static final long serialVersionUID = -6816235585509507709L;

    private final long
            id; // Значение поля должно быть больше 0, Значение этого поля должно быть уникальным,
    // Значение этого поля должно генерироваться автоматически
    private final String name; // Поле не может быть null, Строка не может быть пустой
    private final Coordinates coordinates; // Поле не может быть null
    private final Date
            creationDate; // Поле не может быть null, Значение этого поля должно генерироваться
    // автоматически
    private final long height; // Значение поля должно быть больше 0
    private final LocalDateTime birthday; // Поле не может быть null
    private final EyeColor eyeColor; // Поле не может быть null
    private final HairColor hairColor; // Поле не может быть null
    private final Location location; // Поле не может быть null

    /**
     * Конструктор.
     *
     * @param builder строители
     */
    private Person(Builder builder) {
        this.id = generateNextId();
        this.name = builder.name;
        this.coordinates = builder.coordinates;
        this.creationDate = new Date();
        this.height = builder.height;
        this.birthday = builder.birthday;
        this.eyeColor = builder.eyeColor;
        this.hairColor = builder.hairColor;
        this.location = builder.location;
    }

    /**
     * Конструктор - Создать человека через xml.
     *
     * @param builder      строители
     * @param id           идентификатор
     * @param creationDate время создании
     */
    private Person(Builder builder, long id, Date creationDate) {
        this.id = id;
        this.name = builder.name;
        this.coordinates = builder.coordinates;
        this.creationDate = creationDate;
        this.height = builder.height;
        this.birthday = builder.birthday;
        this.eyeColor = builder.eyeColor;
        this.hairColor = builder.hairColor;
        this.location = builder.location;
    }

    /**
     * Конструктор - Обновление.
     *
     * @param builder строители
     * @param id      идентификатор
     */
    private Person(Builder builder, long id) {
        this.id = id;
        this.name = builder.name;
        this.coordinates = builder.coordinates;
        this.creationDate = new Date();
        this.height = builder.height;
        this.birthday = builder.birthday;
        this.eyeColor = builder.eyeColor;
        this.hairColor = builder.hairColor;
        this.location = builder.location;
    }

    /**
     * Получить идентификатор.
     *
     * @return идентификатор
     */
    private static long generateNextId() {
        final int randomNum1 = 200000;
        final int randomNum2 = 300000;
        long id = (long) (Math.random() * randomNum1);
        boolean b = true;
        while (b) {
            if (idList.contains(id)) {
                id = (int) (Math.random() * randomNum2);
            } else {
                b = false;
                idList.add(id);
            }
        }
        return id;
    }

    /**
     * Создать человека через xml.
     *
     * @param id           идентификатор
     * @param name         имя
     * @param coordinates  координат
     * @param creationDate время создании
     * @param height       высота
     * @param birthday     дата рождения
     * @param eyeColor     цвет глаза
     * @param hairColor    цвет волоса
     * @param location     местоположение
     * @return человек
     * @throws FieldException FieldException
     */
    public static Person fromXml(
            long id,
            String name,
            Coordinates coordinates,
            Date creationDate,
            long height,
            LocalDateTime birthday,
            EyeColor eyeColor,
            HairColor hairColor,
            Location location)
            throws FieldException {
        final Builder builder = new Builder();
        builder.name = name;
        builder.coordinates = coordinates;
        builder.height = height;
        builder.birthday = birthday;
        builder.eyeColor = eyeColor;
        builder.hairColor = hairColor;
        builder.location = location;
        return new Person(builder, id, creationDate);
    }

    /**
     * Создание персоны из XML — подготовка к десериализации Джексона.
     */
    @JsonCreator
    public static Person createForJackson(
            @JsonProperty("id") long id,
            @JsonProperty("name") String name,
            @JsonProperty("coordinates") Coordinates coordinates,
            @JsonProperty("creationDate") Date creationDate,
            @JsonProperty("height") long height,
            @JsonProperty("birthday") LocalDateTime birthday,
            @JsonProperty("eyeColor") EyeColor eyeColor,
            @JsonProperty("hairColor") HairColor hairColor,
            @JsonProperty("location") Location location) throws FieldException {
        return fromXml(id, name, coordinates, creationDate,
                height, birthday, eyeColor, hairColor, location);
    }

    /**
     * Получить строку.
     *
     * @return строка
     */
    @Override
    public String toString() {
        return "id : "
                + id
                + "\n"
                + "name : "
                + name
                + "\n"
                + "coordinates : "
                + coordinates
                + "\n"
                + "creationDate : "
                + creationDate
                + "\n"
                + "height : "
                + height
                + "\n"
                + "birthday : "
                + birthday
                + "\n"
                + "eyeColor : "
                + eyeColor
                + "\n"
                + "hairColor : "
                + hairColor
                + "\n"
                + "location : "
                + location
                + "\n";
    }

    /**
     * Сравнивает два элемента на равенство.
     *
     * @param o человек
     * @return boolean
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        final Person person = (Person) o;
        return id == person.id
                && height == person.height
                && Objects.equals(name, person.name)
                && Objects.equals(coordinates, person.coordinates)
                && Objects.equals(creationDate, person.creationDate)
                && Objects.equals(birthday, person.birthday)
                && eyeColor == person.eyeColor
                && hairColor == person.hairColor
                && Objects.equals(location, person.location);
    }

    /**
     * Получить hashcode.
     *
     * @return hashcode
     */
    @Override
    public int hashCode() {
        return Objects.hash(
                id,
                name,
                coordinates,
                creationDate,
                height,
                birthday,
                eyeColor,
                hairColor,
                location);
    }

    /**
     * Получить id.
     *
     * @return идентификатор
     */
    public long getId() {
        return id;
    }

    /**
     * Получить имя.
     *
     * @return имя
     */
    public String getName() {
        return name;
    }

    /**
     * Получить координат.
     *
     * @return координат
     */
    public Coordinates getCoordinates() {
        return coordinates;
    }

    /**
     * Получить время создании.
     *
     * @return время создании
     */
    public Date getCreationDate() {
        return creationDate;
    }

    /**
     * Получить высоту.
     *
     * @return высота
     */
    public long getHeight() {
        return height;
    }

    /**
     * Получить День рождения.
     *
     * @return День рождения
     */
    public LocalDateTime getBirthday() {
        return birthday;
    }

    /**
     * Получить Цвет глаз.
     *
     * @return Цвет глаз
     */
    public EyeColor getEyeColor() {
        return eyeColor;
    }

    /**
     * Получить Цвет волос.
     *
     * @return Цвет волос
     */
    public HairColor getHairColor() {
        return hairColor;
    }

    /**
     * Получить местоположение.
     *
     * @return местоположение
     */
    public Location getLocation() {
        return location;
    }

    /**
     * класс строителя.
     */
    public static class Builder {
        private String name;
        private Coordinates coordinates;
        private long height;
        private LocalDateTime birthday;
        private EyeColor eyeColor;
        private HairColor hairColor;
        private Location location;

        /**
         * Установка имени через строители.
         *
         * @param name имя
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder name(String name) throws FieldException {
            if (name == null || name.isEmpty()) {
                throw new FieldException("Name не может быть null, Строка не может быть пустой");
            }
            this.name = name;
            return this;
        }

        /**
         * Установка координата через строители.
         *
         * @param coordinates координат
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder coordinates(Coordinates coordinates) throws FieldException {
            if (coordinates == null) {
                throw new FieldException("coordinates не может быть null");
            }
            this.coordinates = coordinates;
            return this;
        }

        /**
         * Установка высоты через строители.
         *
         * @param height высота
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder height(long height) throws FieldException {
            if (height <= 0) {
                throw new FieldException("Height должно быть больше 0");
            }
            this.height = height;
            return this;
        }

        /**
         * Установка даты рождения через строители.
         *
         * @param birthday дата рождения
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder birthday(LocalDateTime birthday) throws FieldException {
            if (birthday == null) {
                throw new FieldException("Birthday не может быть null");
            }
            this.birthday = birthday;
            return this;
        }

        /**
         * Установка цвета глаза через строители.
         *
         * @param eyeColor цвет глаза
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder eyeColor(EyeColor eyeColor) throws FieldException {
            if (eyeColor == null) {
                throw new FieldException("EyeColor не может быть null");
            }
            this.eyeColor = eyeColor;
            return this;
        }

        /**
         * Установка цветы волоса через строители.
         *
         * @param hairColor цвет волоса
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder hairColor(HairColor hairColor) throws FieldException {
            if (hairColor == null) {
                throw new FieldException("HairColor не может быть null");
            }
            this.hairColor = hairColor;
            return this;
        }

        /**
         * Установка местоположения через строители.
         *
         * @param location местоположение
         * @return строители
         * @throws FieldException FieldException
         */
        public Builder location(Location location) throws FieldException {
            if (location == null) {
                throw new FieldException("Location не может быть null");
            }
            this.location = location;
            return this;
        }

        /**
         * построить человека.
         *
         * @return человек
         * @throws FieldException FieldException
         */
        public Person build() throws FieldException {
            return new Person(this);
        }

        /**
         * обновить человека.
         *
         * @param id идентификатор
         * @return человек
         * @throws FieldException FieldException
         */
        public Person buildUpdate(long id) throws FieldException {
            return new Person(this, id);
        }
    }
}
