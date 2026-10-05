package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;

/**
 * Класс команды для выхода из интерактивного режима без сохранения.
 */
public class Exit extends Command {
    /**
     * Конструктор.
     */
    public Exit() {
        super("exit", "завершить программу (без сохранения в файл)");
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) {

        System.exit(1);
        return null;
    }


}
