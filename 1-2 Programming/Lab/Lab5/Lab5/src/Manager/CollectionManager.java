package Manager;

import java.time.LocalDate;
import java.util.*;

import Exceptions.NotInitializationException;
import person.Person;

/**
 * Класс менеджера коллекции
 */
public class CollectionManager {

    /**
     * Экземпляр класса менеджера коллекций
     */
    private static CollectionManager instance;
    /**
     * Коллекция сохраненных элементов
     */
    public static LinkedHashMap<Long, Person> collection;
    /**
     * Время инициализации
     */
    private static LocalDate InitializationTime;
    /**
     * Флаг инициализации
     */
    public static boolean Initialization = false;
    /**
     * начальное значение ключа
     */
    private long key = 1;

    /**
     * Конструктор
     */
    private CollectionManager() {}

    /**
     * Получить экземпляр
     * @return экземпляр
     */
    public static  CollectionManager getInstance() {
        if (instance == null) {
            instance = new CollectionManager();
        }
        return instance;
    }

    /**
     * Добавить элементы в коллекцию
     * @param person элемент
     */
    public void setCollection(Person person) {
        if (!Initialization) {
            throw new NotInitializationException("Коллекция не инициализирована");
        }
        while (collection.containsKey(key)){
            key += 1;
        }
        collection.put(key, person);
    }

    /**
     * Инициализация коллекции
     */
    public void doInitialization() {
        if (!Initialization) {
            collection = new LinkedHashMap<>();
            InitializationTime = LocalDate.now();
            Initialization = true;
        }
    }

    /**
     * Получить время инициализации
     * @return время инициализации
     */
    public LocalDate getInitializationTime() {
        if (!Initialization) {
            throw new NotInitializationException("Коллекция не инициализирована");
        }
        return InitializationTime;

    }

    /**
     * Получить коллекцию
     * @return коллекция
     * @throws NotInitializationException NotInitializationException
     */
    public LinkedHashMap<Long, Person> getCollection() throws NotInitializationException {
        if (!Initialization) {
            throw new NotInitializationException("Коллекция не инициализирована");
        }
        return collection;

    }

    @Override
    public String toString() {
        return "CollectionManager{" +
                "collection=" + collection +
                '}';
    }
}
