package itmo.programming.server.utility;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.server.manager.CollectionManager;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Утилитный класс для проверки и обработки ключей в коллекции.
 */
public class JudgeKey {
    private static final Logger logger = Logger.getLogger(JudgeKey.class.getName());
    
    /**
     * Проверяет существование ключа в коллекции.
     *
     * @param key ключ для проверки
     * @param collectionManager менеджер коллекции
     * @return true, если ключ существует, иначе false
     */
    public static boolean keyExists(long key, CollectionManager collectionManager) {
        return collectionManager.containsKey(key);
    }
    
    /**
     * Разбирает ключ из массива аргументов.
     * Примечание: этот метод больше не отправляет ответ, а только возвращает разобранный ключ.
     *
     * @param args массив аргументов
     * @return разобранный ключ
     * @throws ArgumentException если формат ключа неверный
     */
    public static long judgeKey(String[] args) throws ArgumentException {
        try {
            if (args == null || args.length == 0) {
                logger.warning("Получены пустые аргументы при проверке Key");
                throw new ArgumentException("Не указан Key для проверки");
            }
            
            try {
                return Long.parseLong(args[0]);
            } catch (NumberFormatException e) {
                logger.warning("Некорректный формат Key: " + args[0]);
                throw new ArgumentException("Key должен быть числом");
            }
        } catch (ArgumentException e) {
            throw e;
        } catch (IllegalArgumentException e) {
            logger.log(Level.SEVERE, "Ошибка формата при проверке Key: " + e.getMessage(), e);
            throw new ArgumentException("Ошибка формата при проверке Key: " + e.getMessage());
        } catch (NullPointerException e) {
            logger.log(Level.SEVERE, "Ошибка null-ссылки при проверке Key: " + e.getMessage(), e);
            throw new ArgumentException("Ошибка null-ссылки при проверке Key: " + e.getMessage());
        }
    }
}
