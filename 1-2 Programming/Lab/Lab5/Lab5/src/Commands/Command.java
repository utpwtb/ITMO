package Commands;

import java.io.IOException;

/**
 * Абстрактный класс команды
 */
public abstract class Command {
    /**
     * Название команды
     */
    private final String name;

    /**
     * Описание команды
     */
    private final String description;

    /**
     * Конструктор
     *
     * @param name        название команды
     * @param description описание команды
     */
    public Command(String name, String description) {
        this.name = name;
        this.description = description;
    }

    /**
     * Функция для получения названия команды
     *
     * @return возвращает название команды
     */
    public String getName() {
        return name;
    }

    /**
     * Функция для получения описания команды
     *
     * @return возвращает описание команды
     */
    public String getDescription() {
        return description;
    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    public void execute(String[] args, CommandMode mode) throws IOException {}

    /**
     * Функция для получения количества строк, необходимых для входных параметров составного типа данных
     * @return количество
     */
    public int getFollowUpLines(){return 0;}

    /**
     * @return возвращает объект, переведенный в строковое представление
     */
    public String toString() {
        return "Command{name = " + name + ", description = " + description + "}";
    }
}
