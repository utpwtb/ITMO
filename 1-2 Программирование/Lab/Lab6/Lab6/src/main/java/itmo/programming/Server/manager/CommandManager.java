package itmo.programming.Server.manager;

import itmo.programming.Server.commands.Command;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Класс менеджера коллекции.
 */
public class CommandManager {
    /**
     * Коллекция команд хранения.
     */
    private final Map<String, Command> commands = new LinkedHashMap<>();

    /**
     * Конструктор.
     */
    public CommandManager() {
    }

    /**
     * регистрировать команды.
     *
     * @param commandName название команды
     * @param command     команда
     */
    public void register(String commandName, Command command) {
        commands.put(commandName, command);
    }

    /**
     * Получить команду.
     *
     * @return команда
     */
    public Map<String, Command> getCommands() {
        return this.commands;
    }
}
