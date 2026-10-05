package itmo.programming.Server.manager;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import itmo.programming.Common.person.Person;

import java.io.File;
import java.io.IOException;
import java.nio.file.AccessDeniedException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;


/**
 * Класс файлового менеджера.
 */
public class DocumentManager {

    private final CollectionManager collectionManager;
    private final XmlMapper xmlMapper;

    /**
     * Конструктор.
     */
    public DocumentManager(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;

        this.xmlMapper = new XmlMapper();
        xmlMapper.registerModule(new JavaTimeModule());
        final SimpleModule module = new SimpleModule();
        xmlMapper.registerModule(module);

        xmlMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        xmlMapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
        xmlMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }

    /**
     * Запись в файл.
     *
     * @param map  Коллекция
     * @param path Путь к файлу
     * @return Файл
     * @throws IOException IOException
     */
    public File write(LinkedHashMap<Long, Person> map, String path) throws IOException {
        final File file = new File(path);

        if (!file.exists()) {
            try {
                Files.createDirectories(Paths.get(
                        file.getParent() != null ? file.getParent() : ""));
                Files.createFile(file.toPath());
            } catch (IOException e) {
                System.err.println("Не удалось создать файл: " + e.getMessage());
                throw e;
            }
        }

        if (!file.canWrite()) {
            throw new AccessDeniedException("Нет прав на запись в файл: " + file.getAbsolutePath());
        }

        final LinkedHashMap<Long, Person> sortedMap = new LinkedHashMap<>();
        map.keySet().stream().sorted().forEach(key -> sortedMap.put(key, map.get(key)));

        final PersonsWrapper wrapper = new PersonsWrapper();
        final List<PersonEntry> entries = new ArrayList<>();

        for (Map.Entry<Long, Person> entry : sortedMap.entrySet()) {
            entries.add(new PersonEntry(entry.getKey(), entry.getValue()));
        }

        wrapper.setEntries(entries);

        try {
            xmlMapper.writerWithDefaultPrettyPrinter().writeValue(file, wrapper);
            return file;
        } catch (AccessDeniedException e) {
            System.err.println("Нет прав на запись в файл: " + file.getAbsolutePath());
            throw e;
        } catch (IOException e) {
            System.err.println("Ошибка при записи в файл: " + e.getMessage());
            throw e;
        }
    }

    /**
     * Чтение файла.
     *
     * @param filePath Путь к файлу
     * @return Коллекция
     * @throws IOException IOException
     */
    public LinkedHashMap<Long, Person> read(String filePath) throws IOException {
        final File file = new File(filePath);
        final LinkedHashMap<Long, Person> collection = collectionManager.getCollection();
        collection.clear();

        if (!file.exists()) {
            System.out.println("Файл не существует. Создана пустая коллекция.");
            return collection;
        }

        if (file.length() == 0) {
            System.out.println("Файл пуст. Создана пустая коллекция.");
            return collection;
        }

        try {
            final PersonsWrapper wrapper = xmlMapper.readValue(file, PersonsWrapper.class);

            if (wrapper.getEntries() == null || wrapper.getEntries().isEmpty()) {
                System.out.println("Файл не содержит данных. Создана пустая коллекция.");
                return collection;
            }

            final List<PersonEntry> sortedEntries = wrapper.getEntries();
            sortedEntries.sort(Comparator.comparing(PersonEntry::getKey));

            for (PersonEntry entry : sortedEntries) {
                collection.put(entry.getKey(), entry.getPerson());
            }

            collectionManager.sortByKey();
            return collection;
        } catch (AccessDeniedException e) {
            System.err.println("Нет доступа к файлу: " + file.getAbsolutePath());
            throw e;
        } catch (IOException e) {
            System.err.println("Ошибка при чтении файла: " + e.getMessage());
            throw e;
        }
    }

    /**
     * Класс для хранения пары ключ-значение при сериализации.
     */
    @JsonPropertyOrder({"key", "person"})
    public static class PersonEntry {
        /**
         * Числовой идентификатор (ключ) для доступа к объекту Person.
         * Отображается в XML как элемент <code>&lt;key&gt;</code>.
         */
        @JacksonXmlProperty(localName = "key")
        private Long key;

        /**
         * Объект персона, ассоциированный с ключом.
         * Отображается в XML как элемент <code>&lt;person&gt;</code>.
         */
        @JacksonXmlProperty(localName = "person")
        private Person person;

        /**
         * Конструктор по умолчанию, требуемый для корректной работы
         * десериализации Jackson.
         */
        public PersonEntry() {
        }

        /**
         * Создает связку ключ-значение.
         *
         * @param key    идентификатор объекта
         * @param person объект персона
         */
        public PersonEntry(Long key, Person person) {
            this.key = key;
            this.person = person;
        }

        /**
         * текущее значение ключа.
         *
         * @return текущее значение ключа
         */
        public Long getKey() {
            return key;
        }

        /**
         * Устанавливает новое значение ключа.
         *
         * @param key новое числовое значение идентификатора
         */
        public void setKey(Long key) {
            this.key = key;
        }

        /**
         * связанный объект персона.
         *
         * @return связанный объект персона
         */
        public Person getPerson() {
            return person;
        }

        /**
         * Заменяет объект персона, ассоциированный с ключом.
         *
         * @param person новый объект персона
         */
        public void setPerson(Person person) {
            this.person = person;
        }
    }

    /**
     * Класс обертки XML.
     */
    @JacksonXmlRootElement(localName = "Persons")
    private static class PersonsWrapper {
        @JacksonXmlElementWrapper(useWrapping = false)
        @JacksonXmlProperty(localName = "Entry")
        private List<PersonEntry> entries = new ArrayList<>();

        public List<PersonEntry> getEntries() {
            return entries;
        }

        public void setEntries(List<PersonEntry> entries) {
            this.entries = entries;
        }
    }
}
