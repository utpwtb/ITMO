package itmo.programming.Server.manager;

import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.HairColor;
import itmo.programming.Common.person.Person;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Класс менеджера коллекции, отвечает за операции с коллекцией.
 */
public class CollectionManager {

    /**
     * Элементы коллекции для хранения.
     */
    private static LinkedHashMap<Long, Person> collection;

    /**
     * Время инициализации коллекции.
     */
    private final LocalDate initializationTime;

    private long key = 1;


    /**
     * Конструктор, инициализирует коллекцию.
     */
    public CollectionManager() {
        this.collection = new LinkedHashMap<>();
        this.initializationTime = LocalDate.now();
    }

    /**
     * Получает коллекции.
     *
     * @return коллекции
     */
    public LinkedHashMap<Long, Person> getCollection() {
        return collection;
    }

    /**
     * Получает время инициализации коллекции.
     *
     * @return время инициализации
     */
    public LocalDate getInitializationTime() {
        return initializationTime;
    }

    /**
     * Получает тип коллекции.
     *
     * @return название типа коллекции
     */
    public String getCollectionType() {
        return collection.getClass().getSimpleName();
    }

    /**
     * Получает размер коллекции.
     *
     * @return количество элементов в коллекции
     */
    public int getSize() {
        return collection.size();
    }

    /**
     * Проверяет пустоту коллекции.
     *
     * @return true если коллекция пуста
     */
    public boolean isEmpty() {
        return collection.isEmpty();
    }

    /**
     * Добавляет новый объект Person в коллекцию.
     * Автоматически генерирует уникальный ключ.
     *
     * @param person объект Person для добавления
     * @return true при успешном добавлении, false если person равен null
     */
    public boolean add(Person person) {
        if (person != null) {
            while (collection.containsKey(key)) {
                key += 1;
            }
            collection.put(key, person);
            sortByKey();
            return true;
        }
        return false;
    }

    /**
     * Вставляет элемент по ключу.
     *
     * @param key    ключ элемента
     * @param person объект Person для вставки
     * @return true при успешной вставке, false если ключ уже существует
     */
    public boolean insert(Long key, Person person) {
        if (collection.containsKey(key)) {
            return false;
        }
        collection.put(key, person);
        sortByKey();
        return true;
    }

    /**
     * Удаляет элемент по ключу.
     *
     * @param key ключ удаляемого элемента
     * @return true при успешном удалении, false если ключ не существует
     */
    public boolean removeByKey(Long key) {
        if (collection.containsKey(key)) {
            collection.remove(key);
            sortByKey();
            return true;
        }
        return false;
    }

    /**
     * Очищает коллекцию.
     */
    public void clear() {
        collection.clear();
        sortByKey();
    }

    /**
     * Обновляет элемент по указанному id.
     *
     * @return true при успешном обновлении, false если id не существует
     */
    public boolean update(long id, Person person) {
        final Optional<Map.Entry<Long, Person>> targetEntry = containsId(id);
        final Long key = targetEntry.get().getKey();
        collection.put(key, person);
        sortByKey();
        return true;
    }

    /**
     * Получает список всех элементов.
     *
     * @return список объектов Person
     */
    private List<Person> getAllElements() {
        return new ArrayList<>(collection.values());
    }

    /**
     * Получает все записи ключ-значение.
     *
     * @return список записей Map.Entry
     */
    public Set<Map.Entry<Long, Person>> getAllEntries() {
        return collection.entrySet();
    }

    /**
     * Проверяет существование ключа.
     *
     * @param key проверяемый ключ
     * @return true если ключ существует
     */
    public boolean containsKey(Long key) {
        return collection.containsKey(key);
    }

    /**
     * Проверяет наличие элемента с указанным id в коллекции.
     *
     * @param id проверяемый id
     * @return Optional с найденной записью Map.Entry, или пустой Optional если элемент не найден
     */
    public Optional<Map.Entry<Long, Person>> containsId(Long id) {
        final Optional<Map.Entry<Long, Person>> targetEntry =
                this.getAllEntries().stream()
                        .filter(entry -> {
                            if (entry.getValue() == null) {
                                throw new ArgumentException(
                                        "Указанный идентификатор не существует");
                            }
                            return entry.getValue().getId() == id;
                        })
                        .findFirst();
        return targetEntry;
    }

    /**
     * Фильтрует коллекцию и возвращает элементы, имена которых содержат указанную строку.
     *
     * @param name строка для поиска
     * @return список объектов Person с подходящими именами
     */
    public List<Person> filterContainsName(String name) {
        return this.getAllEntries().stream()
                .filter(entry ->
                        entry.getValue().getName() != null
                                &&
                                entry.getValue().getName().contains(name)
                )
                .map(Map.Entry::getValue)
                .collect(Collectors.toList());
    }

    /**
     * Фильтрует коллекцию и возвращает элементы, цвет волос которых меньше указанного.
     *
     * @param hairColor цвет волос для сравнения
     * @return список объектов Person с подходящим цветом волос
     */
    public List<Person> filterLessThanHairColor(HairColor hairColor) {
        return this.getAllEntries().stream()
                .filter(entry -> {
                    final HairColor color = entry.getValue().getHairColor();
                    return color != null && color.ordinal() < hairColor.ordinal();
                })
                .map(Map.Entry::getValue)
                .collect(Collectors.toList());
    }

    /**
     * Находит элемент с самой ранней датой создания.
     */
    public String minByCreationDate() {
        final Set<Map.Entry<Long, Person>> entrySet = this.getAllEntries();

        Map.Entry<Long, Person> minEntry = null;
        Date minDate = new Date();
        for (Map.Entry<Long, Person> entry : entrySet) {
            final Person person = entry.getValue();
            if (person != null && person.getCreationDate().before(minDate)) {
                minDate = person.getCreationDate();
                minEntry = entry;
            }
        }
        if (minEntry != null) {
            return (minEntry.getValue().toString());
        }
        return null;
    }

    /**
     * Удаляет все элементы, имя которых лексикографически больше имени элемента с указанным id.
     *
     * @param id id элемента для сравнения
     */
    public String removeGreater(long id) {
        final String targetName = getNameById(id);
        final Set<Long> toRemove = this.getAllEntries().stream()
                .filter(entry -> entry.getValue().getName().compareTo(targetName) > 0)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());

        StringBuilder builder = new StringBuilder();
        if (toRemove.isEmpty()) {
            builder.append("Элементы с именем больше \"")
                    .append(targetName)
                    .append("\" не найдены");
        } else {

            builder.append("Найдено ")
                    .append(toRemove.size())
                    .append(" элементов с именем больше \"")
                    .append(targetName).append("\", удаление...");
            toRemove.forEach(this::removeByKey);
            builder.append("Удаление завершено");

        }
        sortByKey();
        String string = builder.toString();
        return string;
    }

    /**
     * Удаляет все элементы, имя которых лексикографически меньше имени элемента с указанным id.
     *
     * @param id id элемента для сравнения
     */
    public String removeLower(long id) {
        final String targetName = getNameById(id);
        final Set<Long> toRemove = this.getAllEntries().stream()
                .filter(entry -> entry.getValue().getName().compareTo(targetName) < 0)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());

        StringBuilder builder = new StringBuilder();
        if (toRemove.isEmpty()) {
            builder.append("Элементы с именем меньше \"")
                    .append(targetName)
                    .append("\" не найдены");
        } else {
            builder.append("Найдено ")
                    .append(toRemove.size())
                    .append(" элементов с именем меньше \"")
                    .append(targetName).append("\", удаление...");
            toRemove.forEach(this::removeByKey);
            builder.append("Удаление завершено");
        }

        sortByKey();
        String string = builder.toString();
        return string;
    }

    /**
     * Удаляет все элементы, ключ которых превышает текущий ключ.
     *
     * @return true если был удален хотя бы один элемент, false в противном случае
     */
    public boolean removeGreaterKey() {
        final Iterator<Map.Entry<Long, Person>> iterator =
                this.getAllEntries().iterator();
        final boolean isRemoved = false;
        while (iterator.hasNext()) {
            final Map.Entry<Long, Person> entry = iterator.next();
            final long entryId = entry.getKey();
            if (entryId > key) {
                iterator.remove();
                sortByKey();
                return !isRemoved;
            }
        }
        return isRemoved;
    }

    /**
     * Получает имя объекта Person по его id.
     *
     * @param id id искомого объекта Person
     * @return имя соответствующего объекта Person
     * @throws IllegalArgumentException если объект с указанным id не найден
     */
    private String getNameById(long id) {
        return this.getAllElements().stream()
                .filter(person -> person.getId() == id)
                .findFirst()
                .map(Person::getName)
                .orElseThrow(() ->
                        new IllegalArgumentException("Человек с идентификатором " + id
                                +
                                " не найден"));
    }

    /**
     * Получает строковое представление коллекции.
     *
     * @return строковое представление коллекции
     */
    @Override
    public String toString() {
        return "CollectionManager{"
                +
                "collection=" + collection
                +
                ", initializationTime=" + initializationTime
                +
                ", size=" + collection.size()
                +
                '}';
    }

    /**
     * Переупорядочить коллекцию так, чтобы она соответствовала порядку ключей.
     */
    public void sortByKey() {
        final LinkedHashMap<Long, Person> sortedMap = new LinkedHashMap<>();

        // 获取所有key并排序
        final List<Long> sortedKeys = new ArrayList<>(collection.keySet());
        Collections.sort(sortedKeys);

        // 按排序后的key顺序重建集合
        for (Long key : sortedKeys) {
            sortedMap.put(key, collection.get(key));
        }

        // 替换原集合
        collection.clear();
        collection.putAll(sortedMap);
    }
}

