package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Server.manager.CollectionManager;

/**
 * Класс команды для получения информации о коллекции.
 */
public class Info extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public Info(CollectionManager collectionManager) {
        super("info", "вывести в стандартный поток вывода информацию о коллекции", CommandsType.SIMPLE);
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
        validateConsoleArgs(args);
        Response response = new Response(
                "Дата инициализации: "
                        +
                        collectionManager.getInitializationTime() + "\n"
                        +
                        "Количество элементов в коллекции:"
                        +
                        collectionManager.getSize() + "\n"
                        +
                        "Тип коллекции:"
                        +
                        collectionManager.getCollectionType() + "\n"
                , ""
        );
        return response;
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
