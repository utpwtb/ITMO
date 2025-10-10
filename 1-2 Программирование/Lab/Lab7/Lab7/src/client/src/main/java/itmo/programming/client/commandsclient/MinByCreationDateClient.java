package itmo.programming.client.commandsclient;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.utility.CommandMode;
import java.io.IOException;

/**
 * Класс команды для вывода любого объекта в коллекции, имеющего наименьшее значение поля
 * `creationDate`.
 */
public class MinByCreationDateClient extends CommandClient {
    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);
        return new Request("min_by_creation_date", args);
    }

    @Override
    public void validateScriptArgs(String[] args) {
        if (args.length != 0) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда не имеет параметров."
            );
        }
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        validateScriptArgs(args);
    }
}
