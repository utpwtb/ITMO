package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;

/**
 * Класс команды для вывода элементов, значение поля `name` которых содержит указанную подстроку.
 */
public class FilterContainsName extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public FilterContainsName(CollectionManager collectionManager) {
        super(
                "filter_contains_name",
                "вывести элементы, значение поля name которых содержит заданную подстроку");
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
                "Операция успешна",
                        collectionManager.filterContainsName(args[0]).toString());
        return response;
    }


}
