package itmo.programming.client;

import itmo.programming.client.commandsclient.CommandClient;
import itmo.programming.client.manager.CommandClientManager;
import itmo.programming.client.manager.NetWorkManager;
import itmo.programming.client.utility.CommandClientUtils;
import itmo.programming.client.utility.GetResponseUtils;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import java.io.IOException;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.NoSuchElementException;
import java.util.Scanner;

/**
 * Главный клиентский класс,
 * отвечающий за взаимодействие с сервером и обработку команд пользователя.
 */
public class Client {
    /**
     * Точка входа клиента. Инициализирует соединение и запускает основной цикл команд.
     *
     * @param args аргументы командной строки
     */
    public static void main(String[] args) {
        final NetWorkManager netWorkManager = new NetWorkManager();
        final boolean init = netWorkManager.init("127.0.0.1", 10000);
        //final boolean init = netWorkManager.init("helios.cs.ifmo.ru", 3129);
        final CommandClientManager commandClientManager = new CommandClientManager();
        CommandClientUtils.commandClientInt(
                commandClientManager, netWorkManager);

        if (init) {
            printWelcomeMessage(netWorkManager);
        }

        // Регистрация хука завершения для обработки Ctrl+C
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\nПолучен сигнал завершения. Выход из программы...");
            if (netWorkManager != null) {
                try {
                    netWorkManager.close();
                } catch (IOException e) {
                    System.out.println("Ошибка при закрытии сетевого соединения: "
                            +
                            e.getMessage());
                }
            }
        }));

        final Scanner scanner = new Scanner(System.in);
        if (init) {
            runCommandLoop(scanner, commandClientManager, netWorkManager);
            // 当runCommandLoop退出时，关闭网络连接
            try {
                netWorkManager.close();
            } catch (IOException e) {
                System.out.println("Ошибка при закрытии сетевого соединения: " + e.getMessage());
            }
        }
    }

    /**
     * Выводит приветственное сообщение от сервера.
     *
     * @param netWorkManager менеджер сетевого взаимодействия
     */
    private static void printWelcomeMessage(NetWorkManager netWorkManager) {
        try {
            final byte[] welcomeMessage = netWorkManager.receiveWelcomeMessage();
            if (welcomeMessage != null) {
                System.out.println(new String(welcomeMessage, "UTF-8"));
            }
        } catch (IOException e) {
            System.out.println(
                    "Ошибка при получении приветственного сообщения: " + e.getMessage());
        }
    }

    /**
     * Основной цикл обработки команд пользователя.
     *
     * @param scanner сканер для ввода команд
     * @param commandClientManager менеджер клиентских команд
     * @param netWorkManager менеджер сетевого взаимодействия
     */
    private static void runCommandLoop(
            Scanner scanner,
            CommandClientManager commandClientManager,
            NetWorkManager netWorkManager) {
        while (true) {
            try {
                System.out.print("> ");
                final LinkedHashMap<String, String[]> line = readLine(scanner);
                if (line == null) {
                    continue;
                }
                final String command = line.keySet().iterator().next();
                final String[] commandArgs = line.get(command);
                final CommandClient commandClient = commandClientManager.getCommands().get(command);
                if (commandClient == null) {
                    System.out.println("Команда не существует: " + command);
                    continue;
                }
                try {
                    commandClient.validateConsoleArgs(commandArgs);
                } catch (ArgumentException e) {
                    System.out.println(e.getMessage());
                    continue;
                }
                if (processCommand(command, commandArgs, commandClient, netWorkManager)) {
                    // exit команда, завершение работы клиента
                    System.out.println("Завершение работы клиента...");
                    return;
                }
            } catch (IOException e) {
                System.out.println("Ошибка сети: " + e.getMessage());
            } 
        }
    }

    /**
     * Обрабатывает одну команду пользователя.
     *
     * @param command имя команды
     * @param commandArgs аргументы команды
     * @param commandClient обработчик команды
     * @param netWorkManager менеджер сетевого взаимодействия
     * @return true, если команда exit, иначе false
     * @throws IOException если возникает ошибка сети
     */
    private static boolean processCommand(
            String command, String[] commandArgs,
            CommandClient commandClient, NetWorkManager netWorkManager) throws IOException {
        final Request request = commandClient.execute(
                commandArgs, CommandMode.CONSOLE_MODE);
        if ("exit".equals(command)) {
            return true;
        }
        if (request == null) {
            return false;
        }
        if ("execute_script".equals(command)) {
            System.out.println("Начало выполнения скрипта: " + commandArgs[0]);
            final Response response = GetResponseUtils.getResponse(request, netWorkManager);
            if (response != null) {
                GetResponseUtils.displayScriptExecutionResponse(response);
            }
        } else {
            final byte[] serialized = netWorkManager.serializer(request);
            if (serialized == null) {
                System.out.println("Ошибка сериализации запроса");
                return false;
            }
            // 检查发送是否成功
            if (!netWorkManager.send(serialized)) {
                System.out.println("Не удалось отправить запрос на сервер");
                return false;
            }
            final byte[] responseBytes = netWorkManager.runClientEventLoop();
            if (responseBytes == null) {
                System.out.println("Сервер не отвечает");
                return false;
            }
            final Response response = netWorkManager.deserialize(responseBytes);
            if (response != null) {
                System.out.println(response.getMessage());
                if (response.getCollectionToStr() != null
                        && !response.getCollectionToStr().isEmpty()) {
                    System.out.println(response.getCollectionToStr());
                }
            } else {
                System.out.println("Невозможно разобрать ответ сервера");
            }
        }
        return false;
    }

    /**
     * Считывает строку команды пользователя и разбивает её на команду и аргументы.
     *
     * @param scanner сканер для ввода
     * @return отображение команды и её аргументов, либо null для пустой строки
     */
    public static LinkedHashMap<String, String[]> readLine(Scanner scanner) {
        try {
            if (!scanner.hasNextLine()) {
                System.out.println("\nПолучен сигнал завершения. Выход из программы...");
                System.exit(0);
                return null;
            }
            final String input = scanner.nextLine().trim();
            if (input.isEmpty()) {
                return null;
            }
            final String[] tokens = input.split("\\s+");
            if (tokens.length == 0) {
                return null;
            }
            final String command = tokens[0].toLowerCase();
            final String[] args = tokens.length > 1
                    ?
                    Arrays.copyOfRange(tokens, 1, tokens.length) : new String[0];
            final LinkedHashMap<String, String[]> result = new LinkedHashMap<>();
            result.put(command, args);
            return result;
        } catch (NoSuchElementException e) {
            System.out.println("Ошибка при чтении команды: " + e.getMessage());
            return null;
        }
    }
}
