package itmo.programming.client.commandsclient;

import itmo.programming.client.manager.NetWorkManager;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import java.io.IOException;

/**
 * Класс команды для удаления всех элементов из коллекции с ключами, превышающими указанное
 * значение.
 */
public class RemoveGreaterKeyClient extends CommandClient {
    private final NetWorkManager netWorkManager;

    /**
     * Конструктор.
     */
    public RemoveGreaterKeyClient(NetWorkManager netWorkManager) {
        this.netWorkManager = netWorkManager;
    }

    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);

        // 第一阶段：检查是否有大于指定key的元素
        final byte[] serialized = netWorkManager.serializer(
                new Request("remove_greater_key", new String[]{args[0], null}));
        if (serialized == null) {
            System.out.println("Ошибка сериализации запроса проверки key");
            return null;
        }
        
        // 发送请求
        netWorkManager.send(serialized);
        
        // 等待响应
        final byte[] responseBytes = netWorkManager.runClientEventLoop();
        if (responseBytes == null) {
            System.out.println("Сервер не отвечает на запрос проверки key");
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

        // 如果响应消息表明没有大于该key的元素，则返回null终止操作
        if (responseMessage.equals("F")) {
            System.out.println("Элементы с key больше " + args[0] + " не найдены");
            return null;
        }

        // 第二阶段：执行删除操作
        return new Request("remove_greater_key", args);
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда имеет "
                            + "и только имеет один аргумент.Пожалуйста, введите:'"
                            + "remove_greater_key"
                            + " {key}"
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
        validateConsoleArgs(args);
    }
}
