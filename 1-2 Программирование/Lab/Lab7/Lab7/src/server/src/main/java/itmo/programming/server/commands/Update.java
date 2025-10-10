package itmo.programming.server.commands;

import com.fasterxml.jackson.core.JsonProcessingException;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.OperationSuccessful;
import itmo.programming.common.utility.PersonParse;
import itmo.programming.server.manager.CollectionManager;
import java.io.IOException;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Класс команды для обновления элемента коллекции.
 */
public class Update extends Command {

    private static final Logger logger = Logger.getLogger(Update.class.getName());

    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public Update(CollectionManager collectionManager) {
        super("update",
                "обновить значение элемента коллекции, id которого равен заданному");
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
            if (args == null || args.length == 0) {
                logger.warning("Получены пустые аргументы для команды update");
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка: не указан ID для обновления");
                return errorResponse;
            }
            if (args.length < 2 || args[1] == null) {
                logger.info("Первая фаза команды update: проверка существования ID");
                try {
                    final long id = Long.parseLong(args[0]);
                    if (collectionManager.containsId(id).isEmpty()) {
                        logger.info("ID " + id + " не найден в коллекции");
                        final Response response = new Response();
                        response.setMessage("F");
                        return response;
                    } else {
                        logger.info("ID " + id + " найден в коллекции");
                        final Response response = new Response();
                        response.setMessage("T");
                        return response;
                    }
                } catch (NumberFormatException e) {
                    logger.warning("Некорректный формат ID: " + args[0]);
                    final Response errorResponse = new Response();
                    errorResponse.setMessage("Ошибка: ID должен быть числом");
                    return errorResponse;
                } catch (ArgumentException e) {
                    logger.warning("Ошибка аргумента: " + e.getMessage());
                    final Response errorResponse = new Response();
                    errorResponse.setMessage("Ошибка: " + e.getMessage());
                    return errorResponse;
                }
            }
            logger.info("Вторая фаза команды update: обновление объекта");
            try {
                final long id = Long.parseLong(args[0]);
                if (collectionManager.containsId(id).isEmpty()) {
                    logger.warning("ID " + id + " не найден в коллекции");
                    final Response errorResponse = new Response();
                    errorResponse.setMessage("Ошибка: указанный идентификатор не существует");
                    return errorResponse;
                }
                logger.info("Начало десериализации Person объекта");
                final Person person = PersonParse.strToPerson(args[1]);
                if (person == null) {
                    logger.warning("Десериализация вернула null для Person объекта");
                    final Response errorResponse = new Response();
                    errorResponse.setMessage(
                            "Ошибка: не удалось создать объект Person из полученных данных");
                    return errorResponse;
                }
                logger.info("Обновление объекта с ID " + id);
                final boolean success = collectionManager.update(id, person);
                final ArrayList<String> judge = OperationSuccessful.judge(person, success);
                final Response response = new Response();
                response.setMessage(judge.get(0));
                response.setCollectionToStr(judge.get(1));
                logger.info("Объект с ID " + id + " успешно обновлен");
                return response;
            } catch (NumberFormatException e) {
                logger.warning("Некорректный формат ID: " + args[0]);
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка: ID должен быть числом");
                return errorResponse;
            } catch (JsonProcessingException e) {
                logger.log(Level.WARNING,
                        "Ошибка при обработке JSON данных: " + e.getMessage(), e);
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка обработки JSON данных: " + e.getMessage());
                return errorResponse;
            } catch (ArgumentException e) {
                logger.log(Level.WARNING,
                        "Ошибка аргумента: " + e.getMessage(), e);
                final Response errorResponse = new Response();
                errorResponse.setMessage("Ошибка аргумента: " + e.getMessage());
                return errorResponse;
            }
        } catch (NumberFormatException e) {
            logger.log(Level.SEVERE,
                    "Критическая ошибка формата числа: " + e.getMessage(), e);
            final Response errorResponse = new Response();
            errorResponse.setMessage("Критическая ошибка формата числа: " + e.getMessage());
            return errorResponse;
        } catch (ArgumentException e) {
            logger.log(Level.SEVERE,
                    "Критическая ошибка аргумента: " + e.getMessage(), e);
            final Response errorResponse = new Response();
            errorResponse.setMessage("Критическая ошибка аргумента: " + e.getMessage());
            return errorResponse;
        }
    }
}
