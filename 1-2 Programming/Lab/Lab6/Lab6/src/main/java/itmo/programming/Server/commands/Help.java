package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Server.manager.CommandManager;
import itmo.programming.Common.exceptions.ArgumentException;

import java.util.stream.Collectors;

/**
 * Класс команды для вывода справки по всем доступным командам.
 */
public class Help extends Command {
    /**
     * Менеджер команды.
     */
    private final CommandManager commandManager;

    /**
     * Конструктор.
     */
    public Help(CommandManager commandManager) {
        super("help", "вывести справку по доступным командам", CommandsType.SIMPLE);
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
        validateConsoleArgs(args);
        System.out.println(args.length);
        Response response = new Response(commandManager.getCommands().values().stream()
                .map(
                        command ->
                                String.format(
                                        "%-35s%-1s%n",
                                        command.getName(), command.getDescription()))
                .collect(Collectors.joining()), ""
        );
        return response;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 0) {
            if (args.length != 0) {
                throw new ArgumentException(
                        "Неправильное количество аргументов!Эта команда не имеет параметров.");
            }
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
