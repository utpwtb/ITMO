package Manager;

import Commands.Command;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Класс менеджера коллекции
 */
public class CommandManager {
    /**
     * Коллекция команд хранения
     */
    private final Map<String, Command> commands = new LinkedHashMap<>();

    /**
     * Экземпляр класса менеджера коллекции
     */
    private static CommandManager instance;

    /**
     * Конструктор
     */
    private CommandManager(){}

    /**
     * Получить экземпляр
     * @return экземпляр
     */
    public static  CommandManager getInstance() {
        if (instance == null) {
            instance = new CommandManager();
        }
        return instance;
    }

    /**
     * регистрировать команды
     * @param commandName название команды
     * @param command команда
     */
    public void register(String commandName, Command command) {
        commands.put(commandName, command);
    }

    /**
     * Получить команду
     * @return команда
     */
    public Map<String, Command> getCommands(){
        return this.commands;
    }


}
