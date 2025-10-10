package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;

/**
 * Класс команды для очищения коллекции.
 */
public class Clear extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public Clear(CollectionManager collectionManager) {
        super("clear", "очистить коллекцию");
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

        collectionManager.clear();
        final Response response = new Response("Операция успешна", "");
        return response;
    }


}
