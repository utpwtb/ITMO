package itmo.programming.server;

import itmo.programming.common.exceptions.NotInitializationException;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.manager.CommandManager;
import itmo.programming.server.manager.DocumentManager;
import itmo.programming.server.manager.NetWorkManager;
import itmo.programming.server.utility.CommandUtils;
import itmo.programming.server.utility.FileUtils;
import itmo.programming.server.utility.Runner;
import java.io.IOException;
import java.net.Socket;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Основной класс сервера, обрабатывающий подключения клиентов и команды.
 */
public class Server {
    
    /**
     * Логгер для записи информации о работе сервера.
     */
    public static Logger logger = Logger.getLogger(Server.class.getName());

    /**
     * Точка входа в программу сервера.
     *
     * @param args аргументы командной строки (не используются)
     */
    public static void main(String[] args) {
        // Получаем путь к файлу из переменной окружения
        String filePath = System.getenv("MY_FILE_PATH");
        if (filePath == null) {
            logger.info("Ошибка: переменная среды MY_FILE_PATH не задана");
            logger.info("Запуск с пустой коллекцией");
            filePath = "personCollection.xml";
        }

        // Инициализация менеджеров
        final NetWorkManager netWorkManager = new NetWorkManager(10000);
        //final NetWorkManager netWorkManager = new NetWorkManager(3129);
        final CommandManager commandManager = new CommandManager();
        final CollectionManager collectionManager = new CollectionManager();
        final DocumentManager documentManager = new DocumentManager(collectionManager);
        
        // Инициализация команд
        CommandUtils.commandInitialization(commandManager, collectionManager);
        
        // Инициализация файлового менеджера и загрузка данных
        final FileUtils fileUtils = new FileUtils(documentManager, collectionManager, filePath);
        fileUtils.initializeFile();

        // Регистрация хука завершения для сохранения данных при выходе
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("\nПолучен сигнал завершения. Сохранение данных...");
            fileUtils.saveToFile();
        }));

        final Thread ctrldthread = new Thread(() -> {
            try {
                while (true) {
                    final int input = System.in.read();
                    if (input == -1) {
                        System.exit(0);
                    }
                }
            } catch (IOException e) {
                logger.info("\nПолучен сигнал завершения. Сохранение данных...");
            }
        });
        ctrldthread.setDaemon(true);
        ctrldthread.start();

        // Инициализация исполнителя команд
        final Runner runner = new Runner(commandManager);

        try {
            // Инициализация сетевого менеджера
            final boolean init = netWorkManager.init();
            if (!init) {
                logger.severe("Не удалось инициализировать сервер. Завершение работы.");
                return;
            }

            logger.info("Сервер успешно инициализирован и готов к приему подключений.");
            logger.info("Ожидание подключений клиентов ...");

            // Основной цикл сервера
            while (true) {
                try {
                    final NetWorkManager.RequestData requestData
                            = netWorkManager.runServerEventLoop();
                    
                    if (requestData != null && requestData.data != null) {
                        processRequest(requestData, runner, netWorkManager);
                    }
                    
                    Thread.sleep(1);
                } catch (IOException e) {
                    if (e.getMessage() != null && e.getMessage().contains("timed out")) {
                        logger.log(Level.FINE, "Таймаут сетевой операции: " + e.getMessage());
                    } else {
                        logger.log(Level.WARNING, "Ошибка обработки запроса: " + e.getMessage(), e);
                    }
                } catch (InterruptedException e) {
                    logger.log(Level.WARNING, "Прерывание потока сервера: " + e.getMessage(), e);
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        } catch (NotInitializationException e) {
            logger.log(Level.SEVERE, "Критическая ошибка: " + e.getMessage(), e);
        }
    }
    
    /**
     * Обрабатывает запрос клиента, выполняет команду и отправляет ответ.
     *
     * @param requestData данные запроса от клиента
     * @param runner исполнитель команд
     * @param netWorkManager менеджер сетевого взаимодействия
     */
    private static void processRequest(
            NetWorkManager.RequestData requestData, Runner runner, NetWorkManager netWorkManager) {
        try {
            final Request deserialize = netWorkManager.deserialize(requestData.data);
            if (deserialize != null) {
                final Socket clientSocket = netWorkManager.getCurrentClientSocket();
                final String clientInfo = clientSocket != null
                        ?
                    (clientSocket.getInetAddress()
                            +
                            ":" + clientSocket.getPort()) : "неизвестный клиент";
                
                logger.info(
                        "Получена команда от клиента "
                                + clientInfo + ": " + deserialize.getCommandStr());

                try {
                    final Response response = runner.runCommand(deserialize);
                    if (response != null) {
                        final byte[] serialized = netWorkManager.serializer(response);
                        if (serialized != null) {
                            netWorkManager.send(serialized);
                            logger.info(
                                    "Отправлен ответ клиенту " + clientInfo
                                            + " на команду: " + deserialize.getCommandStr());
                        } else {
                            logger.warning(
                                    "Сериализация ответа вернула null для команды: "
                                            + deserialize.getCommandStr());
                        }
                    } else {
                        logger.warning(
                                "Выполнение команды вернуло null: "
                                        + deserialize.getCommandStr());
                    }
                } catch (IllegalArgumentException | IllegalStateException e) {
                    logger.log(Level.WARNING,
                            "Ошибка выполнения команды "
                                    + deserialize.getCommandStr() + ": " + e.getMessage(), e);

                    final Response errorResponse = new Response();
                    errorResponse.setMessage("Ошибка выполнения команды: " + e.getMessage());
                    final byte[] serialized = netWorkManager.serializer(errorResponse);
                    if (serialized != null) {
                        netWorkManager.send(serialized);
                    }
                }
            } else {
                logger.warning("Десериализация запроса вернула null");
            }
        } catch (IOException e) {
            logger.log(Level.WARNING, "Ошибка при обработке запроса: " + e.getMessage(), e);
        }
    }
}
