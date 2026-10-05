package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import java.io.IOException;

/**
 * Абстрактный класс, представляющий команду в системе.
 * Все конкретные команды должны наследоваться от этого класса.
 */
public abstract class Command {
    /**
     * Название команды, используемое для её вызова.
     */
    private final String name;

    /**
     * Описание команды, отображаемое в справке.
     */
    private final String description;

    /**
     * Конструктор для создания команды с указанным названием и описанием.
     *
     * @param name название команды
     * @param description описание команды
     */
    public Command(String name, String description) {
        this.name = name;
        this.description = description;
    }

    /**
     * Возвращает название команды.
     *
     * @return название команды
     */
    public String getName() {
        return name;
    }

    /**
     * Возвращает описание команды.
     *
     * @return описание команды
     */
    public String getDescription() {
        return description;
    }

    /**
     * Выполняет команду с указанными аргументами в заданном режиме.
     * Этот метод должен быть переопределен в конкретных командах.
     *
     * @param args массив аргументов команды
     * @param mode режим выполнения команды
     * @return объект ответа, содержащий результат выполнения команды
     * @throws IOException в случае ошибок ввода-вывода при выполнении команды
     */
    public Response execute(String[] args, CommandMode mode) throws IOException {
        return null;
    }

    /**
     * Возвращает строковое представление команды.
     *
     * @return строковое представление команды
     */
    @Override
    public String toString() {
        return "Command{name = " + name + ", description = " + description + "}";
    }
}
