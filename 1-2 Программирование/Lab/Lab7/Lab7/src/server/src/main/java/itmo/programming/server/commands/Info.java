package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;

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
        super("info", "вывести в стандартный поток вывода информацию о коллекции");
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

        final Response response = new Response(
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
                        collectionManager.getCollectionType() + "\n",
                ""
        );
        return response;
    }


}
