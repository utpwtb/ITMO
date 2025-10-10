package itmo.programming.server.commands;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.utility.JudgeKey;
import java.io.IOException;
import java.util.logging.Logger;

/**
 * Класс команды для удаления всех элементов из коллекции с ключами, превышающими указанное
 * значение.
 */
public class RemoveGreaterKey extends Command {
    private static final Logger logger = Logger.getLogger(RemoveGreaterKey.class.getName());

    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public RemoveGreaterKey(CollectionManager collectionManager) {
        super(
                "remove_greater_key",
                "удалить из коллекции все элементы, ключ которых превышает заданный");
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
            final long key = JudgeKey.judgeKey(args);
            
            // 第一阶段：检查是否有参数为null，如果有则是客户端在检查key是否存在
            if (args.length > 1 && args[1] == null) {
                logger.info("Первый этап: проверка наличия элементов с key больше " + key);
                
                // 检查是否有大于该key的元素
                boolean hasGreaterKey = false;
                for (java.util.Map.Entry<Long, ?> entry : collectionManager.getAllEntries()) {
                    if (entry.getKey() > key) {
                        hasGreaterKey = true;
                        break;
                    }
                }

                final Response response = new Response();
                if (hasGreaterKey) {
                    logger.info("Найдены элементы с key больше " + key);
                    response.setMessage("T"); // 表示存在大于key的元素
                } else {
                    logger.info("Не найдены элементы с key больше " + key);
                    response.setMessage("F"); // 表示不存在大于key的元素
                }
                return response;
            }
            
            // 第二阶段：执行删除操作
            logger.info("Второй этап: удаление элементов с key больше " + key);
            final boolean isRemoved = collectionManager.removeGreaterKey(key);
            final Response response = new Response();
            if (isRemoved) {
                logger.info("Элементы с key больше " + key + " успешно удалены");
                response.setMessage("Элементы с key больше " + key + " успешно удалены.");
            } else {
                logger.info("Элементы с key больше " + key + " не найдены");
                response.setMessage("Элементы с key больше " + key + " не найдены.");
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
