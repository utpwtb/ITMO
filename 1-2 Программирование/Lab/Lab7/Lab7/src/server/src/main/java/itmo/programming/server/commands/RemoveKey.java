package itmo.programming.server.commands;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.utility.JudgeKey;
import java.io.IOException;
import java.util.logging.Logger;

/**
 * Класс команды для удаления элементов из коллекции на основе ключа.
 */
public class RemoveKey extends Command {

    private static final Logger logger = Logger.getLogger(RemoveKey.class.getName());

    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public RemoveKey(CollectionManager collectionManager) {
        super("remove_key", "удалить элемент из коллекции по его ключу");
        this.collectionManager = collectionManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) throws IOException {
        try {
            // 使用新的JudgeKey.judgeKey方法
            final long key = JudgeKey.judgeKey(args);
            
            // 第一阶段：检查是否有参数为null，如果有则是客户端在检查key是否存在
            if (args.length > 1 && args[1] == null) {
                logger.info("Первый этап: проверка существования key " + key);
                
                // 检查Key是否存在
                final boolean keyExists = JudgeKey.keyExists(key, collectionManager);

                final Response response = new Response();
                if (keyExists) {
                    logger.info("Key " + key + " существует в коллекции");
                    response.setMessage("T"); // 表示key存在
                } else {
                    logger.info("Key " + key + " не существует в коллекции");
                    response.setMessage("F"); // 表示key不存在
                }
                return response;
            }
            
            // 第二阶段：执行删除操作
            logger.info("Второй этап: удаление элемента с key " + key);
            
            // 这里不再需要检查key是否存在，因为第一阶段已经检查过了
            final boolean isRemoved = collectionManager.removeByKey(key);
            final Response response = new Response();
            if (isRemoved) {
                logger.info("Элемент с ключом " + key + " успешно удален");
                response.setMessage("Элемент успешно удален");
            } else {
                logger.warning("Не удалось удалить элемент с ключом " + key);
                response.setMessage("Удаление элемента не удалось");
            }
            response.setCollectionToStr("");
            return response;
        } catch (ArgumentException e) {
            return new Response(e.getMessage(), "");
        } catch (NumberFormatException e) {
            logger.warning("Ошибка формата числа: " + e.getMessage());
            return new Response("Ошибка формата числа: " + e.getMessage(), "");
        }
    }
}
