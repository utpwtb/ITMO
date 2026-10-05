package itmo.programming.server.commands;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CommandManager;
import java.util.stream.Collectors;

/**
 * Класс команды для вывода справки по всем доступным командам.
 */
public class  Help extends Command {
    /**
     * Менеджер команды.
     */
    private final CommandManager commandManager;

    /**
     * Конструктор.
     */
    public Help(CommandManager commandManager) {
        super("help", "вывести справку по доступным командам");
        this.commandManager = commandManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) throws ArgumentException {
        final Response response = new Response(commandManager.getCommands().values().stream()
                .map(
                        command ->
                                String.format(
                                        "%-35s%-1s%n",
                                        command.getName(), command.getDescription()))
                .collect(Collectors.joining()), ""
        );
        return response;
    }


}
