package itmo.programming.server.manager;

import itmo.programming.server.commands.Command;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Класс для управления командами в приложении.
 */
public class CommandManager {
    
    /**
     * Коллекция для хранения зарегистрированных команд.
     */
    private final Map<String, Command> commands = new LinkedHashMap<>();

    /**
     * Конструктор по умолчанию.
     */
    public CommandManager() {
    }

    /**
     * Регистрирует команду в менеджере.
     *
     * @param commandName название команды
     * @param command объект команды
     */
    public void register(String commandName, Command command) {
        commands.put(commandName, command);
    }

    /**
     * Получает все зарегистрированные команды.
     *
     * @return карта с командами
     */
    public Map<String, Command> getCommands() {
        return this.commands;
    }
}
