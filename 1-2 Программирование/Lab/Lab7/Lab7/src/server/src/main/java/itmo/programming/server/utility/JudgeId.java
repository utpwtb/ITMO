package itmo.programming.server.utility;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.server.manager.CollectionManager;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Утилитный класс для проверки и обработки идентификаторов в коллекции.
 */
public class JudgeId {
    private static final Logger logger = Logger.getLogger(JudgeId.class.getName());
    
    /**
     * Проверяет существование идентификатора в коллекции.
     *
     * @param id идентификатор для проверки
     * @param collectionManager менеджер коллекции
     * @return true, если идентификатор существует, иначе false
     */
    public static boolean idExists(long id, CollectionManager collectionManager) {
        return !collectionManager.containsId(id).isEmpty();
    }
    
    /**
     * Разбирает идентификатор из массива аргументов и проверяет его.
     * Примечание: этот метод больше не отправляет ответ,
     * а только возвращает разобранный идентификатор.
     *
     * @param args массив аргументов
     * @param collectionManager менеджер коллекции
     * @return разобранный идентификатор
     * @throws ArgumentException если формат идентификатора неверный или он не существует
     */
    public static long judgeId(String[] args,
                               CollectionManager collectionManager) throws ArgumentException {
        try {
            if (args == null || args.length == 0) {
                logger.warning("Получены пустые аргументы при проверке ID");
                throw new ArgumentException("Не указан ID для проверки");
            }
            
            final long id;
            try {
                id = Long.parseLong(args[0]);
            } catch (NumberFormatException e) {
                logger.warning("Некорректный формат ID: " + args[0]);
                throw new ArgumentException("ID должен быть числом");
            }
            
            return id;
        } catch (ArgumentException e) {
            throw e;
        } catch (IllegalArgumentException e) {
            logger.log(Level.SEVERE, "Ошибка формата при проверке ID: " + e.getMessage(), e);
            throw new ArgumentException("Ошибка формата при проверке ID: " + e.getMessage());
        } catch (NullPointerException e) {
            logger.log(Level.SEVERE, "Ошибка null-ссылки при проверке ID: " + e.getMessage(), e);
            throw new ArgumentException("Ошибка null-ссылки при проверке ID: " + e.getMessage());
        }
    }
}
