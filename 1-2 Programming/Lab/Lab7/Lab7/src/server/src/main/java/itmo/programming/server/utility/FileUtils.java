package itmo.programming.server.utility;

import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.manager.DocumentManager;
import java.io.File;
import java.io.IOException;
import java.nio.file.AccessDeniedException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.logging.Logger;

/**
 * Класс для управления файловыми операциями сервера.
 * Отвечает за чтение, создание и сохранение файлов коллекции.
 */
public class FileUtils {
    
    /**
     * Логгер для записи информации о файловых операциях.
     */
    private static final Logger logger = Logger.getLogger(FileUtils.class.getName());
    
    /**
     * Менеджер документов для работы с XML файлами.
     */
    private final DocumentManager documentManager;
    
    /**
     * Менеджер коллекции для хранения данных.
     */
    private final CollectionManager collectionManager;
    
    /**
     * Путь к файлу с данными коллекции.
     */
    private final String filePath;
    
    /**
     * Конструктор класса FileManager.
     *
     * @param documentManager менеджер документов
     * @param collectionManager менеджер коллекции
     * @param filePath путь к файлу с данными
     */
    public FileUtils(DocumentManager documentManager,
                     CollectionManager collectionManager, String filePath) {
        this.documentManager = documentManager;
        this.collectionManager = collectionManager;
        this.filePath = filePath;
    }
    
    /**
     * Инициализирует файл с данными коллекции.
     * Создает новый файл, если он не существует, или загружает данные из существующего файла.
     */
    public void initializeFile() {
        final File file = new File(filePath);
        if (!file.exists()) {
            createNewFile(file);
        } else {
            loadFromFile();
        }
    }
    
    /**
     * Создает новый пустой файл для хранения данных коллекции.
     *
     * @param file объект File, представляющий файл для создания
     */
    private void createNewFile(File file) {
        try {
            Files.createDirectories(Paths.get(
                    file.getParent() != null ? file.getParent() : ""));
            Files.createFile(file.toPath());
            logger.info("Файл " + filePath
                    + " не существует. Создан новый пустой файл.");
        } catch (IOException e) {
            logger.info("Не удалось создать файл: " + e.getMessage());
            logger.info("Запуск с пустой коллекцией");
        }
    }
    
    /**
     * Загружает данные из существующего файла в коллекцию.
     */
    private void loadFromFile() {
        try {
            documentManager.read(filePath);
            logger.info("Данные загружены из файла " + filePath);
        } catch (AccessDeniedException e) {
            logger.info("Нет доступа к файлу: " + e.getMessage());
            logger.info("Запуск с пустой коллекцией");
        } catch (IOException e) {
            logger.info("Ошибка при чтении файла: " + e.getMessage());
            logger.info("Запуск с пустой коллекцией");
        }
    }
    
    /**
     * Сохраняет данные коллекции в файл.
     */
    public void saveToFile() {
        try {
            documentManager.write(collectionManager.getCollection(), filePath);
            logger.info("Данные сохранены в файл " + filePath);
        } catch (AccessDeniedException e) {
            logger.info("Не удалось сохранить данные: нет доступа к файлу "
                    + filePath);
        } catch (IOException e) {
            logger.info("Ошибка при сохранении данных: " + e.getMessage());
        }
    }
    
    /**
     * Возвращает путь к файлу с данными коллекции.
     *
     * @return путь к файлу
     */
    public String getFilePath() {
        return filePath;
    }
}
