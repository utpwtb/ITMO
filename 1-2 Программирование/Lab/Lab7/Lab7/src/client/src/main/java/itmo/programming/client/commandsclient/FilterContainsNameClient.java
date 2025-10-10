package itmo.programming.client.commandsclient;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.utility.CommandMode;
import java.io.IOException;

/**
 * Класс команды для вывода элементов, значение поля `name` которых содержит указанную подстроку.
 */
public class FilterContainsNameClient extends CommandClient {
    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);
        return new Request("filter_contains_name", args);
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда имеет "
                            + "и только имеет один аргумент.Пожалуйста, введите:'"
                            + "filter_contains_name"
                            + " {name}"
            );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
