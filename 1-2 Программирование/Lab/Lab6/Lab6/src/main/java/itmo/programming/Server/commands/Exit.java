package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;

/**
 * Класс команды для выхода из интерактивного режима без сохранения.
 */
public class Exit extends Command {
    /**
     * Конструктор.
     */
    public Exit() {
        super("exit", "завершить программу (без сохранения в файл)", CommandsType.SIMPLE);
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) {
        validateConsoleArgs(args);
        System.exit(1);
        return null;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 0) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда не имеет параметров."
                    );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
