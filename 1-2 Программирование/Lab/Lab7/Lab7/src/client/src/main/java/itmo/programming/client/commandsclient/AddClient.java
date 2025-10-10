package itmo.programming.client.commandsclient;

import itmo.programming.client.utility.CreatPerson;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.createperson.PersonFactory;

/**
 * Класс команды для добавления нового элемента в коллекцию.
 */
public class AddClient extends CommandClient {

    @Override
    public Request execute(String[] args, CommandMode mode) {
        validateArgs(args, mode);

        final Person person = new CreatPerson(
                new PersonFactory())
                .createPersonAdd(args, mode);
        return new Request("add", new String[0], person);

    }



    /**
     * Получить количество строк для чтения в режиме скрипта.
     *
     * @return количество
     */
    @Override
    public int getFollowUpLines() {
        final int lines = 10;
        return lines;
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
        if (args.length != getFollowUpLines()) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда не имеет параметров."
            );
        }
    }
}
