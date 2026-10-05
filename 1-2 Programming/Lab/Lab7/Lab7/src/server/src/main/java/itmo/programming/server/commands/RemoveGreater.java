package itmo.programming.server.commands;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.utility.JudgeId;
import java.io.IOException;
import java.util.logging.Logger;

/**
 * Класс команды для удаления элементов, больших введенного.
 */
public class RemoveGreater extends Command {
    private static final Logger logger = Logger.getLogger(RemoveGreater.class.getName());

    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public RemoveGreater(CollectionManager collectionManager) {
        super("remove_greater", "удалить из коллекции все элементы, превышающие заданный");
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
            // 使用新的JudgeId.judgeId方法
            final long id = JudgeId.judgeId(args, collectionManager);
            
            // 第一阶段：检查是否有参数为null，如果有则是客户端在检查ID是否存在
            if (args.length > 1 && args[1] == null) {
                logger.info("Первый этап: проверка существования ID " + id);
                
                // 检查ID是否存在
                final boolean idExists = JudgeId.idExists(id, collectionManager);

                final Response response = new Response();
                if (idExists) {
                    logger.info("ID " + id + " существует в коллекции");
                    response.setMessage("T"); // 表示ID存在
                } else {
                    logger.info("ID " + id + " не существует в коллекции");
                    response.setMessage("F"); // 表示ID不存在
                }
                return response;
            }
            
            // 第二阶段：执行删除操作
            logger.info("Второй этап: удаление элементов с именем больше элемента с ID " + id);
            
            final String string = collectionManager.removeGreater(id);
            return new Response(string, "");
        } catch (ArgumentException e) {
            return new Response(e.getMessage(), "");
        } catch (NumberFormatException e) {
            return new Response("Неверный формат идентификатора: " + args[0], "");
        }
    }
}
