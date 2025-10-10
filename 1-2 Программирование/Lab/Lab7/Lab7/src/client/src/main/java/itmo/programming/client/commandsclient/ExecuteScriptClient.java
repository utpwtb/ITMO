package itmo.programming.client.commandsclient;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.utility.CommandMode;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Класс для выполнения скриптовых команд.
 */
public class ExecuteScriptClient extends CommandClient {

    
    // Используем ThreadLocal для хранения пути вызова скрипта для каждого потока
    private static final ThreadLocal<Set<String>> callPathTracker = 
        ThreadLocal.withInitial(HashSet::new);

    /**
     * Конструктор.
     */
    public ExecuteScriptClient() {

    }

    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);
        
        String filePath = args[0];
        try {
            // Нормализуем путь к файлу
            final Path path = Paths.get(filePath).toRealPath();
            filePath = path.toString();
        } catch (IOException e) {
            // Если не удается разрешить путь, продолжаем с исходным путем
        }

        // Проверяем существование и доступность файла
        final File scriptFile = new File(filePath);
        validateFile(scriptFile, filePath);

        // Получаем набор путей вызовов для текущего потока
        final Set<String> currentCallPath = callPathTracker.get();
        
        // Проверка на рекурсивный вызов
        if (currentCallPath.contains(filePath)) {
            System.out.println(
                    "Предупреждение: обнаружен циклический рекурсивный вызов " + filePath);
            System.out.println("Текущий путь вызова: " + currentCallPath);
            // Обнаружена циклическая рекурсия, пропускаем текущий скрипт
            return null;
        }

        try {
            // Добавляем текущий скрипт в путь вызова
            currentCallPath.add(filePath);
            
            // Читаем содержимое скрипта
            final List<String> scriptCommands = readScriptCommands(scriptFile);
            
            // Создаем запрос с командами скрипта
            return new Request("execute_script", new String[]{String.join("\n", scriptCommands)});
        } finally {
            // После обработки удаляем текущий скрипт из пути вызова
            currentCallPath.remove(filePath);
        }
    }

    /**
     * Проверка существования и доступности файла.
     */
    private void validateFile(File file, String filePath) {
        if (!file.exists()) {
            throw new RuntimeException("Файл " + filePath + " не существует");
        }
        if (!file.canRead()) {
            throw new RuntimeException("Файл " + filePath + " не доступен для чтения");
        }
    }

    /**
     * Чтение команд из файла скрипта.
     */
    private List<String> readScriptCommands(File file) throws IOException {
        final List<String> commands = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                // Добавляем все строки, включая пустые
                commands.add(line); 
            }
        }
        return commands;
    }

    /**
     * Проверка аргументов в консольном режиме.
     */
    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда требует "
                    + "и только требует один аргумент. "
                    + "Пожалуйста, введите: 'execute_script {абсолютный путь к файлу}'"
            );
        }
    }

    /**
     * Проверка аргументов в режиме скрипта.
     */
    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
