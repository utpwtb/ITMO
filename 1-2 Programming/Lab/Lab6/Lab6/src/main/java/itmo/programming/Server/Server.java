package itmo.programming.Server;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.NotInitializationException;
import itmo.programming.Common.utility.CommandUtils;
import itmo.programming.Common.utility.Runner;
import itmo.programming.Server.manager.CollectionManager;
import itmo.programming.Server.manager.CommandManager;
import itmo.programming.Server.manager.DocumentManager;
import itmo.programming.Server.manager.NetWorkManager;

import java.io.File;
import java.io.IOException;
import java.nio.file.AccessDeniedException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Server {
    public static Logger logger = Logger.getLogger(Server.class.getName());

    public static void main(String[] args) {
        String filePath = System.getenv("MY_FILE_PATH");
        NetWorkManager netWorkManager = new NetWorkManager(10000);
        if (filePath == null) {
            logger.info("Ошибка: переменная среды MY_FILE_PATH не задана");
            logger.info("Запуск с пустой коллекцией");
            filePath = "personCollection.xml"; // 默认文件名
        }

        final CommandManager commandManager = new CommandManager();
        final CollectionManager collectionManager = new CollectionManager();

        CommandUtils.commandInitialization(commandManager, collectionManager);

        final DocumentManager documentManager = new DocumentManager(collectionManager);

        final File file = new File(filePath);
        if (!file.exists()) {
            try {
                Files.createDirectories(Paths.get(
                        file.getParent() != null ? file.getParent() : ""));
                Files.createFile(file.toPath());
                logger.info("Файл " + filePath
                        +
                        " не существует. Создан новый пустой файл.");
            } catch (IOException e) {
                logger.info("Не удалось создать файл: " + e.getMessage());
                logger.info("Запуск с пустой коллекцией");
            }
        } else {
            try {
                // 尝试加载文件
                documentManager.read(filePath);
                logger.info("Данные загружены из файла " + filePath);
            } catch (AccessDeniedException e) {
                logger.info("Нет доступа к файлу: " + e.getMessage());
                logger.info("Запуск с пустой коллекцией");
            } catch (IOException e) {
                logger.info("Ошибка при чтении файла: " + e.getMessage());
                logger.info("Запуск с пустой коллекцией");
            }
        }

        // 最终文件路径保存到final变量以供ShutdownHook使用
        final String finalFilePath = filePath;

        // 注册关闭钩子
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("\nПолучен сигнал завершения. Сохранение данных...");
            try {
                documentManager.write(collectionManager.getCollection(), finalFilePath);
                logger.info("Данные сохранены в файл " + finalFilePath);
            } catch (AccessDeniedException e) {
                logger.info("Не удалось сохранить данные: нет доступа к файлу "
                        +
                        finalFilePath);
            } catch (IOException e) {
                logger.info("Ошибка при сохранении данных: " + e.getMessage());
            }
        }));

        final Runner runner = new Runner(commandManager);

        try {
            boolean init = netWorkManager.init();
            if (!init) {
                logger.severe("Не удалось инициализировать сервер. Завершение работы.");
                return;
            }

            logger.info("Сервер успешно инициализирован и готов к приему подключений.");

            while (true) {
                try {
                    NetWorkManager.RequestData requestData = netWorkManager.runServerEventLoop();
                    if (requestData != null && requestData.data != null) {
                        Request deserialize = netWorkManager.deserialize(requestData.data);
                        if (deserialize != null) {
                            logger.info("Получена команда: " + deserialize.getCommandName());
                            System.out.println(deserialize);
                            Response response = runner.runCommand(deserialize);
                            byte[] serialized = netWorkManager.serializer(response);
                            if (serialized != null) {
                                netWorkManager.send(requestData.key, serialized);
                            } else {
                                logger.warning("Сериализация ответа вернула null");
                            }
                        } else {
                            logger.warning("Десериализация запроса вернула null");
                        }
                    }
                } catch (IOException e) {
                    logger.log(Level.WARNING, "Ошибка обработки запроса: " + e.getMessage(), e);
                }
            }
        } catch (NotInitializationException e) {
            logger.log(Level.SEVERE, "Критическая ошибка: " + e.getMessage(), e);
        }
    }
}
