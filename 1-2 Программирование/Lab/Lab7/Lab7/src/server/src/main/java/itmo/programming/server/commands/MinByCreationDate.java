package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;


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
                        + "значение поля creationDate которого является минимальным");
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

        final Response response = new Response(collectionManager.minByCreationDate(),
                "");
        return response;
    }


}
