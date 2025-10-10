package itmo.programming.client.utility;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;


/**
 * Утилиты для выполнения скриптов на стороне клиента.
 */
public class ExecuteScriptUtils {
    // Используем ThreadLocal для хранения путей выполнения скриптов каждого потока
    private static final ThreadLocal<Set<String>> executionPathTracker = 
        ThreadLocal.withInitial(HashSet::new);
    
    /**
     * Проверка существования и доступности файла.
     *
     * @param file объект файла
     * @param filePath путь к файлу
     * @throws FileNotFoundException когда файл не существует
     * @throws SecurityException когда файл недоступен для чтения
     */
    public static void validateFile(File file, String filePath) throws FileNotFoundException {
        if (!file.exists()) {
            throw new FileNotFoundException("Файл " + filePath + " не существует");
        }
        if (!file.canRead()) {
            throw new SecurityException("Файл " + filePath + " недоступен для чтения");
        }
    }

    /**
     * Чтение команд из файла, включая пустые строки.
     *
     * @param filePath путь к файлу
     * @return список команд
     * @throws IOException при ошибке чтения файла
     */
    public static List<String> readCommandsFromFile(String filePath) throws IOException {
        final List<String> commands = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Добавляем все строки, включая пустые и комментарии
                commands.add(line);
            }
        }
        
        return commands;
    }
    
    /**
     * Проверка наличия циклической рекурсии.
     *
     * @param filePath путь к файлу
     * @return true, если скрипт уже находится в пути выполнения
     */
    public static boolean isCircularRecursion(String filePath) {
        try {
            // Нормализуем путь к файлу
            final Path path = Paths.get(filePath).toRealPath();
            return executionPathTracker.get().contains(path.toString());
        } catch (IOException e) {
            // Если не удается разрешить путь, используем исходный путь
            return executionPathTracker.get().contains(filePath);
        }
    }
    
    /**
     * Добавление скрипта в путь выполнения.
     *
     * @param filePath путь к файлу
     * @return нормализованный путь к файлу
     */
    public static String addToExecutionPath(String filePath) {
        try {
            // Нормализуем путь к файлу
            final Path path = Paths.get(filePath).toRealPath();
            final String normalizedPath = path.toString();
            executionPathTracker.get().add(normalizedPath);
            return normalizedPath;
        } catch (IOException e) {
            // Если не удается разрешить путь, используем исходный путь
            executionPathTracker.get().add(filePath);
            return filePath;
        }
    }
    
    /**
     * Удаление скрипта из пути выполнения.
     *
     * @param filePath путь к файлу
     */
    public static void removeFromExecutionPath(String filePath) {
        executionPathTracker.get().remove(filePath);
    }
    
    /**
     * Получение текущего пути выполнения (для отладки).
     *
     * @return копия набора текущего пути выполнения
     */
    public static Set<String> getCurrentExecutionPath() {
        return new HashSet<>(executionPathTracker.get());
    }
}
