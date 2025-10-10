package itmo.programming.server.commands;

import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.manager.DocumentManager;
import java.io.IOException;
import java.util.LinkedHashMap;


/**
 * Класс команды для сохранения коллекции в файл.
 */
public class Save extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    private final DocumentManager documentManager;

    /**
     * Конструктор.
     */
    public Save(CollectionManager collectionManager, DocumentManager documentManager) {
        super("save", "сохранить коллекцию в файл");
        this.collectionManager = collectionManager;
        this.documentManager = documentManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) {

        final LinkedHashMap<Long, Person> collection = collectionManager.getCollection();

        try {
            documentManager.write(
                    collection, "personCollection.xml");
            final Response response = new Response("Сохранено успешно", "");
            return response;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }


}
