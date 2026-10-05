package itmo.programming.client.commandsclient;

import itmo.programming.client.manager.NetWorkManager;
import itmo.programming.client.utility.CreatPerson;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.createperson.PersonFactory;
import java.io.IOException;

/**
 * Класс команды для обновления элемента коллекции.
 */
public class UpdateClient extends CommandClient {
    private final NetWorkManager netWorkManager;

    /**
     * Конструктор.
     */
    public UpdateClient(NetWorkManager netWorkManager) {
        this.netWorkManager = netWorkManager;
    }

    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);

        // 第一阶段：检查ID是否存在
        final byte[] serialized = netWorkManager.serializer(
                new Request("update", new String[]{args[0]}));
        if (serialized == null) {
            System.out.println("Ошибка сериализации запроса проверки ID");
            return null;
        }
        
        // 发送请求
        netWorkManager.send(serialized);
        
        // 等待响应
        final byte[] responseBytes = netWorkManager.runClientEventLoop();
        if (responseBytes == null) {
            System.out.println("Сервер не отвечает на запрос проверки ID");
            return null;
        }
        
        // 解析响应
        final Response checkResponse = netWorkManager.deserialize(responseBytes);
        if (checkResponse == null) {
            System.out.println("Ошибка при разборе ответа сервера");
            return null;
        }
        
        // 检查getMessage()返回值是否为null
        final String responseMessage = checkResponse.getMessage();
        if (responseMessage == null) {
            System.out.println("Ошибка: сервер вернул пустой ответ");
            return null;
        }

        // 如果响应消息表明ID不存在，则返回null终止操作
        if (responseMessage.equals("F")) {
            System.out.println("Указанный идентификатор не существует");
            return null;
        }

        // 第二阶段：创建Person对象并发送更新请求
        final Person person = new CreatPerson(new PersonFactory())
                .createPersonUpdate(args, mode, Long.parseLong(args[0]));

        if (person == null) {
            System.out.println("Не удалось создать объект Person");
            return null;
        }

        try {
            // 创建更新请求，直接传递Person对象
            final Request updateRequest = new Request("update", new String[]{args[0]}, person);
            
            // 这里不直接发送请求，而是返回给Client.java处理
            // 这样可以保持与其他命令一致的处理流程
            return updateRequest;
            
        } catch (ArgumentException | NumberFormatException e) {
            System.out.println("Ошибка при выполнении команды: " + e.getMessage());
            return null;
        }
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
                            + "update"
                            + " {id}"
            );
        }
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("Параметр должен быть числом");
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        if (args.length != getFollowUpLines()) {
            throw new ArgumentException("Неправильное количество аргументов!");
        }
    }
}
