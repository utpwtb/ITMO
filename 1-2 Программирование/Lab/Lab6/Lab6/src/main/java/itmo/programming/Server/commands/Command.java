package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.person.Person;

import java.io.IOException;

/**
 * Абстрактный класс команды.
 */
public abstract class Command implements ValidateArgs {
    /**
     * Название команды.
     */
    private final String name;

    /**
     * Описание команды.
     */
    private final String description;

    private final CommandsType type;

    /**
     * Конструктор.
     *
     * @param name        название команды
     * @param description описание команды
     * @param type
     */
    public Command(String name, String description, CommandsType type) {
        this.name = name;
        this.description = description;
        this.type = type;
    }

    /**
     * Функция для получения названия команды.
     *
     * @return возвращает название команды
     */
    public String getName() {
        return name;
    }

    /**
     * Функция для получения описания команды.
     *
     * @return возвращает описание команды
     */
    public String getDescription() {
        return description;
    }

    public CommandsType getType(){
        return type;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    public Response execute(String[] args, CommandMode mode) throws IOException {
        return null;
    }

    /**
     * Исполнение команды с объектом.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    public Response executeWithObject(Object[] args, CommandMode mode) throws IOException {
        return null;
    }

    /**
     * Исполнение команды с Person объектом.
     *
     * @param person Person объект
     * @param mode   Режим исполнения
     */
    public Response executeWithPerson(Person person, CommandMode mode) throws IOException {
        return null;
    }

    /**
     * Исполнение команды с Person объектом и ключом.
     *
     * @param key   Ключ
     * @param person Person объект
     * @param mode   Режим исполнения
     */
    public Response executeWithPersonAndKey(Long key, Person person, CommandMode mode) throws IOException {
        return null;
    }

    /**
     * Функция для получения количества строк, необходимых для входных параметров составного типа
     * данных.
     *
     * @return количество
     */
    public int getFollowUpLines() {
        return 0;
    }

    /**
     * Получить строку команды.
     *
     * @return возвращает объект, переведенный в строковое представление
     */
    public String toString() {
        return "Command{name = " + name + ", description = " + description + "}";
    }
}
