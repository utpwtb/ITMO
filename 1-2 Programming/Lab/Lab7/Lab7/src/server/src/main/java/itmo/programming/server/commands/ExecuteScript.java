package itmo.programming.server.commands;

import itmo.programming.common.exceptions.NoSuchCommandException;
import itmo.programming.common.network.Response;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.server.manager.CommandManager;
import itmo.programming.server.utility.Runner;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Класс для выполнения скриптовых команд.
 */
public class ExecuteScript extends Command {
    private static final Logger logger = Logger.getLogger(ExecuteScript.class.getName());
    /**
     * Менеджер команд.
     */
    private final CommandManager commandManager;
    private final Runner runner;

    /**
     * Конструктор.
     */
    public ExecuteScript(CommandManager commandManager) {
        super("execute_script", "выполнить список команд скрипта");
        this.commandManager = commandManager;
        this.runner = new Runner(commandManager);
    }

    /**
     * Выполнение команды.
     *
     * @param args массив аргументов
     * @param mode режим выполнения
     * @return объект ответа
     */
    @Override
    public Response execute(String[] args, CommandMode mode) throws IOException {
        if (args.length != 1) {
            return new Response("Ошибка: отсутствует список команд скрипта", "");
        }

        // Если скрипт пуст, возвращаем успех без операций
        if (args[0] == null || args[0].trim().isEmpty()) {
            return new Response("Скрипт пуст, команды не выполнены", "");
        }

        // Разделяем строку команд на отдельные команды
        final String[] commandLines = args[0].split("\n");

        // Для сохранения результатов выполнения каждой команды
        final List<String> results = new ArrayList<>();
        int successCount = 0;

        // Выполняем каждую команду
        for (String commandLine : commandLines) {
            // Пропускаем пустые строки
            if (commandLine == null || commandLine.trim().isEmpty()) {
                continue;
            }

            try {
                // Разбор строки команды
                final String[] tokens = commandLine.trim().split("\\s+");
                if (tokens.length == 0) {
                    continue;
                }

                final String commandName = tokens[0].toLowerCase();
                final String[] commandArgs = tokens.length > 1
                        ?
                        Arrays.copyOfRange(tokens, 1, tokens.length) : new String[0];

                // Создаем объект запроса
                final itmo.programming.common.network.Request request =
                        new itmo.programming.common.network.Request(commandName, commandArgs);

                // Выполняем команду
                final Response response = runner.runCommand(request);
                successCount++;

                // Сохраняем результаты выполнения
                if (response != null) {
                    String resultMessage = response.getMessage();
                    if (response.getCollectionToStr() != null
                            &&
                            !response.getCollectionToStr().isEmpty()) {
                        resultMessage += "\n" + response.getCollectionToStr();
                    }
                    results.add(commandName + ": " + resultMessage);
                } else {
                    results.add(commandName
                            +
                            ": Выполнение команды не удалось, результат не получен");
                }
            } catch (NoSuchCommandException e) {
                logger.log(Level.WARNING, "Команда не найдена при выполнении скрипта ["
                        +
                        commandLine + "]: " + e.getMessage(), e);
                results.add(commandLine + ": Команда не найдена - " + e.getMessage());
            }
        }

        // Создаем итоговый ответ
        final String finalMessage =
                "Выполнение скрипта завершено, всего выполнено "
                        +
                        successCount + " команд (пропущены пустые строки)";
        final String resultDetails = String.join("\n", results);

        return new Response(finalMessage, resultDetails);
    }
}
