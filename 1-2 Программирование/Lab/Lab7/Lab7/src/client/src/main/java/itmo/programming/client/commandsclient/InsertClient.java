package itmo.programming.client.commandsclient;

import itmo.programming.client.manager.NetWorkManager;
import itmo.programming.client.utility.CreatPerson;
import itmo.programming.client.utility.GetResponseUtils;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.createperson.PersonFactory;
import java.io.IOException;

/**
 * Класс команды для добавления нового элемента с указанным ключом.
 */
public class InsertClient extends CommandClient {
    private final NetWorkManager netWorkManager;

    /**
     * Конструктор.
     */
    public InsertClient(NetWorkManager netWorkManager) {
        this.netWorkManager = netWorkManager;
    }

    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);

        // 第一次请求：检查key是否存在
        final Request request = new Request("insert", new String[]{args[0]});
        final Response response = GetResponseUtils.getResponse(request, netWorkManager);
        if (response == null) {
            return null;
        }

        // 如果响应消息表明key存在，则返回null终止操作
        if (response.getMessage().equals("T")) {
            System.out.println("Указанный ключ уже существует");
            return null;
        }

        final Person person = new CreatPerson(
                new PersonFactory())
                .createPersonInsert(args, mode);

        return new Request("insert", new String[]{args[0]}, person);
    }

    /**
     * Получить количество строк для чтения в режиме скрипта.
     *
     * @return количество
     */
    @Override
    public int getFollowUpLines() {
        final int lines = 11;
        return lines;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда имеет "
                            + "и только имеет один аргумент. Пожалуйста, введите:'"
                            + "insert"
                            + " {key}"
            );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        if (args.length != getFollowUpLines()) {
            throw new ArgumentException("Неправильное количество аргументов!"
            );
        }
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("Параметр должен быть числом");
        }
    }
}
