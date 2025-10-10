package itmo.programming.server.commands;

import com.fasterxml.jackson.core.JsonProcessingException;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.OperationSuccessful;
import itmo.programming.common.utility.PersonParse;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.utility.JudgeKey;
import java.io.IOException;
import java.util.ArrayList;
import java.util.logging.Logger;

/**
 * Класс команды для добавления нового элемента с указанным ключом.
 */
public class Insert extends Command {

    private static final Logger logger = Logger.getLogger(Insert.class.getName());

    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public Insert(CollectionManager collectionManager) {
        super("insert", "добавить новый элемент с заданным ключом");
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
            // 第一阶段：检查key是否已存在
            if (args.length < 2 || args[1] == null) {
                logger.info("Первая фаза команды insert: проверка существования key");
                try {
                    final long key = JudgeKey.judgeKey(args);
                    
                    if (JudgeKey.keyExists(key, collectionManager)) {
                        logger.info("Key " + key + " уже существует в коллекции");
                        final Response response = new Response();
                        response.setMessage("T");
                        return response;
                    } else {
                        logger.info("Key " + key + " не существует в коллекции");
                        final Response response = new Response();
                        response.setMessage("F");
                        return response;
                    }
                } catch (ArgumentException e) {
                    logger.warning("Ошибка при проверке key: " + e.getMessage());
                    final Response errorResponse = new Response();
                    errorResponse.setMessage(e.getMessage());
                    return errorResponse;
                }
            }
            
            // 第二阶段：插入对象
            logger.info("Вторая фаза команды insert: добавление объекта");
            try {
                final long key = JudgeKey.judgeKey(args);
                
                // 检查key是否已存在
                if (JudgeKey.keyExists(key, collectionManager)) {
                    logger.warning("Key " + key + " уже существует в коллекции");
                    final Response errorResponse = new Response();
                    errorResponse.setMessage("Указанный ключ уже существует");
                    return errorResponse;
                }
                
                final Person person = PersonParse.strToPerson(args[1]);
                if (person == null) {
                    logger.warning("Десериализация вернула null для Person объекта");
                    final Response errorResponse = new Response();
                    errorResponse.setMessage(
                            "Ошибка: не удалось создать объект Person из полученных данных");
                    return errorResponse;
                }
                
                final boolean success = collectionManager.insert(key, person);
                final ArrayList<String> judge = OperationSuccessful.judge(person, success);
                final Response response = new Response();
                response.setMessage(judge.get(0));
                response.setCollectionToStr(judge.get(1));
                return response;
            } catch (ArgumentException e) {
                logger.warning("Ошибка аргумента: " + e.getMessage());
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка аргумента: " + e.getMessage());
                return errorResponse;
            } catch (JsonProcessingException e) {
                logger.warning("Ошибка обработки JSON: " + e.getMessage());
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка обработки JSON: " + e.getMessage());
                return errorResponse;
            } catch (NumberFormatException e) {
                logger.warning("Ошибка формата числа: " + e.getMessage());
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка формата числа: " + e.getMessage());
                return errorResponse;
            }
        } catch (ArgumentException e) {
            logger.warning("Критическая ошибка аргумента: " + e.getMessage());
            final Response errorResponse = new Response();
            errorResponse.setMessage("Критическая ошибка аргумента: " + e.getMessage());
            return errorResponse;
        } catch (NumberFormatException e) {
            logger.warning("Критическая ошибка формата числа: " + e.getMessage());
            final Response errorResponse = new Response();
            errorResponse.setMessage("Критическая ошибка формата числа: " + e.getMessage());
            return errorResponse;
        }
    }
}
