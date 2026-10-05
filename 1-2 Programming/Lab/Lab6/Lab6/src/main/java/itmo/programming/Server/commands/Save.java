package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Server.manager.CollectionManager;
import itmo.programming.Server.manager.DocumentManager;

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
        super("save", "сохранить коллекцию в файл", CommandsType.SIMPLE);
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
        validateConsoleArgs(args);
        final LinkedHashMap<Long, Person> collection = collectionManager.getCollection();

        try {
            documentManager.write(
                    collection, "personCollection.xml");
            Response response = new Response("Сохранено успешно", "");
            return response;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
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
