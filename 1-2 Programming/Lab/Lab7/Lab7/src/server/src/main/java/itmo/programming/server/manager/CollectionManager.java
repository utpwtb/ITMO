package itmo.programming.server.manager;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.person.HairColor;
import itmo.programming.common.person.Person;
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
 * Класс для управления коллекцией объектов Person.
 * Обеспечивает операции добавления, удаления, обновления и поиска элементов.
 */
public class CollectionManager {

    /**
     * Коллекция для хранения объектов Person с ключами типа Long.
     */
    private static LinkedHashMap<Long, Person> collection;

    /**
     * Дата инициализации коллекции.
     */
    private final LocalDate initializationTime;

    /**
     * Текущее значение ключа для добавления новых элементов.
     */
    private long key = 1;

    /**
     * Конструктор, инициализирующий пустую коллекцию.
     */
    public CollectionManager() {
        this.collection = new LinkedHashMap<>();
        this.initializationTime = LocalDate.now();
    }

    /**
     * Возвращает коллекцию объектов Person.
     *
     * @return коллекция объектов Person
     */
    public LinkedHashMap<Long, Person> getCollection() {
        return collection;
    }

    /**
     * Возвращает дату инициализации коллекции.
     *
     * @return дата инициализации
     */
    public LocalDate getInitializationTime() {
        return initializationTime;
    }

    /**
     * Возвращает тип коллекции.
     *
     * @return название типа коллекции
     */
    public String getCollectionType() {
        return collection.getClass().getSimpleName();
    }

    /**
     * Возвращает количество элементов в коллекции.
     *
     * @return размер коллекции
     */
    public int getSize() {
        return collection.size();
    }

    /**
     * Проверяет, пуста ли коллекция.
     *
     * @return true, если коллекция пуста, иначе false
     */
    public boolean isEmpty() {
        return collection.isEmpty();
    }

    /**
     * Добавляет новый объект Person в коллекцию с автоматически генерируемым ключом.
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
     * Вставляет объект Person в коллекцию по указанному ключу.
     *
     * @param key ключ для вставки
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
     * Удаляет элемент из коллекции по ключу.
     *
     * @param key ключ элемента для удаления
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
     * Очищает коллекцию, удаляя все элементы.
     */
    public void clear() {
        collection.clear();
        sortByKey();
    }

    /**
     * Обновляет элемент коллекции с указанным идентификатором.
     *
     * @param id идентификатор элемента для обновления
     * @param person новый объект Person
     * @return true при успешном обновлении
     */
    public boolean update(long id, Person person) {
        final Optional<Map.Entry<Long, Person>> targetEntry = containsId(id);
        final Long key = targetEntry.get().getKey();
        collection.put(key, person);
        sortByKey();
        return true;
    }

    /**
     * Возвращает список всех элементов коллекции.
     *
     * @return список объектов Person
     */
    private List<Person> getAllElements() {
        return new ArrayList<>(collection.values());
    }

    /**
     * Возвращает все записи ключ-значение из коллекции.
     *
     * @return набор записей Map.Entry
     */
    public Set<Map.Entry<Long, Person>> getAllEntries() {
        return collection.entrySet();
    }

    /**
     * Проверяет наличие ключа в коллекции.
     *
     * @param key проверяемый ключ
     * @return true, если ключ существует, иначе false
     */
    public boolean containsKey(Long key) {
        return collection.containsKey(key);
    }

    /**
     * Ищет элемент с указанным идентификатором в коллекции.
     *
     * @param id идентификатор для поиска
     * @return Optional с найденной записью Map.Entry или пустой Optional, если элемент не найден
     * @throws ArgumentException если указанный идентификатор не существует
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
     *
     * @return строковое представление найденного элемента или null, если коллекция пуста
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
     * @param id идентификатор элемента для сравнения
     * @return строка с результатом операции
     */
    public String removeGreater(long id) {
        final String targetName = getNameById(id);
        final Set<Long> toRemove = this.getAllEntries().stream()
                .filter(entry -> entry.getValue().getName().compareTo(targetName) > 0)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());

        final StringBuilder builder = new StringBuilder();
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
        final String string = builder.toString();
        return string;
    }

    /**
     * Удаляет все элементы, имя которых лексикографически меньше имени элемента с указанным id.
     *
     * @param id идентификатор элемента для сравнения
     * @return строка с результатом операции
     */
    public String removeLower(long id) {
        final String targetName = getNameById(id);
        final Set<Long> toRemove = this.getAllEntries().stream()
                .filter(entry -> entry.getValue().getName().compareTo(targetName) < 0)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());

        final StringBuilder builder = new StringBuilder();
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
        final String string = builder.toString();
        return string;
    }

    /**
     * Удаляет все элементы, ключ которых превышает заданный ключ.
     *
     * @param keyToCompare ключ для сравнения
     * @return true, если был удален хотя бы один элемент, иначе false
     */
    public boolean removeGreaterKey(long keyToCompare) {
        final Iterator<Map.Entry<Long, Person>> iterator =
                this.getAllEntries().iterator();
        boolean isRemoved = false;
        
        while (iterator.hasNext()) {
            final Map.Entry<Long, Person> entry = iterator.next();
            final long entryKey = entry.getKey();
            if (entryKey > keyToCompare) {
                iterator.remove();
                isRemoved = true;
            }

        }
        
        if (isRemoved) {
            sortByKey();
        }
        
        return isRemoved;
    }

    /**
     * Получает имя объекта Person по его идентификатору.
     *
     * @param id идентификатор объекта Person
     * @return имя объекта Person
     * @throws IllegalArgumentException если объект с указанным идентификатором не найден
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
     * Возвращает строковое представление коллекции.
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
     * Сортирует коллекцию по ключам.
     */
    public void sortByKey() {
        final LinkedHashMap<Long, Person> sortedMap = new LinkedHashMap<>();

        // Получаем все ключи и сортируем их
        final List<Long> sortedKeys = new ArrayList<>(collection.keySet());
        Collections.sort(sortedKeys);

        // Перестраиваем коллекцию в соответствии с отсортированными ключами
        for (Long key : sortedKeys) {
            sortedMap.put(key, collection.get(key));
        }

        // Заменяем исходную коллекцию
        collection.clear();
        collection.putAll(sortedMap);
    }
}


