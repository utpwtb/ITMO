package itmo.programming.client.manager;

import itmo.programming.client.commandsclient.CommandClient;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Менеджер клиентских команд, отвечающий за регистрацию и хранение команд.
 * Предоставляет доступ к зарегистрированным командам по их именам.
 */
public class CommandClientManager {
    private final Map<String, CommandClient> commandsClient = new LinkedHashMap<>();

    /**
     * Конструктор.
     */
    public CommandClientManager() {
    }

    /**
     * регистрировать команды.
     *
     * @param commandName название команды
     * @param commandClient     команда
     */
    public void register(String commandName, CommandClient commandClient) {
        commandsClient.put(commandName, commandClient);
    }

    /**
     * Получить команду.
     *
     * @return команда
     */
    public Map<String, CommandClient> getCommands() {
        return this.commandsClient;
    }
}
