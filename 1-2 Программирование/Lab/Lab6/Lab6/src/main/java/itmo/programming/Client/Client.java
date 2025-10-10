package itmo.programming.Client;

import itmo.programming.Client.commands.ClientCommandManager;
import itmo.programming.Client.manager.NetWorkManager;
import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.utility.createperson.PersonFactory;

import java.util.Arrays;
import java.util.Scanner;
import java.util.logging.Logger;

public class Client {
    private static final Logger logger = Logger.getLogger(Client.class.getName());
    private static final Scanner scanner = new Scanner(System.in);
    
    public static void main(String[] args) {
        // 创建PersonFactory，用于创建Person对象
        PersonFactory personFactory = new PersonFactory();
        
        // 使用PersonFactory创建命令管理器
        ClientCommandManager commandManager = new ClientCommandManager(personFactory);
        
        // 创建网络管理器
        NetWorkManager netWorkManager = new NetWorkManager();
        
        // 连接服务器
        boolean init = netWorkManager.init("127.0.0.1", 10000);
        if (!init) {
            System.out.println("Не удалось подключиться к серверу");
            return;
        }
        
        // 接收欢迎消息
        try {
            byte[] welcomeMessage = netWorkManager.receiveWelcomeMessage();
            if (welcomeMessage != null) {
                System.out.println(new String(welcomeMessage, "UTF-8"));
            }
        } catch (Exception e) {
            logger.warning("Ошибка при получении приветственного сообщения: " + e.getMessage());
        }
        
        // 主循环
        while (true) {
            try {
                System.out.print("> ");
                String input = scanner.nextLine().trim();
                if (input.isEmpty()) continue;
                
                // 解析命令和参数
                String[] parts = input.split("\\s+");
                String commandName = parts[0].toLowerCase();
                String[] commandArgs = Arrays.copyOfRange(parts, 1, parts.length);
                
                // 检查命令是否存在
                if (!commandManager.hasCommand(commandName)) {
                    System.out.println("Неизвестная команда: " + commandName);
                    continue;
                }
                
                // 执行客户端命令
                Request request = commandManager.executeCommand(commandName, commandArgs);
                if (request == null) continue;
                
                // 处理exit命令
                if (commandName.equals("exit")) {
                    System.out.println("Завершение работы");
                    System.exit(0);
                }
                
                // 发送请求到服务器
                byte[] serialized = netWorkManager.serializer(request);
                netWorkManager.send(serialized);
                
                // 接收响应
                byte[] responseBytes = netWorkManager.runClientEventLoop();
                if (responseBytes != null) {
                    Response response = netWorkManager.deserialize(responseBytes);
                    if (response != null) {
                        // 打印响应信息
                        if (response.getMessage() != null && !response.getMessage().isEmpty()) {
                            System.out.println(response.getMessage());
                        }
                        if (response.getCollectionToStr() != null && !response.getCollectionToStr().isEmpty()) {
                            System.out.println(response.getCollectionToStr());
                        }
                    } else {
                        System.out.println("Получен некорректный ответ от сервера");
                    }
                } else {
                    System.out.println("Нет ответа от сервера");
                }
            } catch (Exception e) {
                System.out.println("Ошибка: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    /**
     * Прочитайте каждую строку.
     *
     * @param scanner сканер
     * @return Коллекция
     */
    public static Request readLine(Scanner scanner) {
        final String input = scanner.nextLine().trim();
        if (input.isEmpty()) {
            throw new ArgumentException("Ввод не может быть пустым");
        }
        final String[] tokens = input.split("\\s+");

        final String command = tokens[0].toLowerCase();
        final String[] args = Arrays.copyOfRange(tokens, 1, tokens.length);
        Request request = new Request(command, args);
        return request;
    }
}
