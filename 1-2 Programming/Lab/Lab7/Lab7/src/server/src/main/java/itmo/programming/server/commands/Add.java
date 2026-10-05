package itmo.programming.server.commands;

import com.fasterxml.jackson.core.JsonProcessingException;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.OperationSuccessful;
import itmo.programming.common.utility.PersonParse;
import itmo.programming.server.manager.CollectionManager;
import java.util.ArrayList;


/**
 * Класс команды для добавления нового элемента в коллекцию.
 */
public class Add extends Command {

    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;


    /**
     * Конструктор.
     */
    public Add(CollectionManager collectionManager) {
        super("add", "добавить новый элемент");
        this.collectionManager = collectionManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) throws JsonProcessingException {
        final Person person = PersonParse.strToPerson(args[1]);
        final boolean success = collectionManager.add(person);
        final ArrayList<String> judge = OperationSuccessful.judge(person, success);
        final Response response = new Response();
        response.setMessage(judge.get(0));
        response.setCollectionToStr(judge.get(1));
        return response;
    }


}
