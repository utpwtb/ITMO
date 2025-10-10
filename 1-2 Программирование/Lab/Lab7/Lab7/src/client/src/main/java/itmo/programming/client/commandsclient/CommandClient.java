package itmo.programming.client.commandsclient;

import itmo.programming.client.commandsclient.ValidateArgs;
import itmo.programming.common.network.Request;
import itmo.programming.common.utility.CommandMode;
import java.io.IOException;

/**
 * Абстрактный класс, представляющий команду в системе.
 * Все конкретные команды должны наследоваться от этого класса.
 */
public abstract class CommandClient implements ValidateArgs {
    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    public Request execute(String[] args, CommandMode mode) throws IOException {
        return null;
    }

    /**
     * Функция для получения количества строк, необходимых для входных параметров составного типа
     * данных.
     *
     * @return количество
     */
    public int getFollowUpLines() {
        return 0;
    }

    void validateArgs(String[] args, CommandMode mode) {
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            validateConsoleArgs(args);
        } else {
            validateScriptArgs(args);
        }
    }
}
