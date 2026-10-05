package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Server.manager.CollectionManager;

/**
 * Класс команды для вывода любого объекта в коллекции, имеющего наименьшее значение поля
 * `creationDate`.
 */
public class MinByCreationDate extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public MinByCreationDate(CollectionManager collectionManager) {
        super(
                "min_by_creation_date",
                "вывести любой объект из коллекции, "
                        + "значение поля creationDate которого является минимальным", CommandsType.SIMPLE);
        this.collectionManager = collectionManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) {
        validateScriptArgs(args);
        String string = collectionManager.minByCreationDate();
        Response response = new Response(string, "");
        return response;
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
