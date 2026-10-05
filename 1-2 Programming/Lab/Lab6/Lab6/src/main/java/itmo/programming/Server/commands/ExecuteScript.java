package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Server.manager.CommandManager;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.exceptions.NoSuchCommandException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Класс команды для выполнения скрипта из файла.
 */
public class ExecuteScript extends Command implements ValidateArgs {

    /**
     * Менеджер команды.
     */
    private final CommandManager commandManager;

    /**
     * Конструктор.
     */
    public ExecuteScript(CommandManager commandManager) {
        super("execute_script", "считать и исполнить скрипт из указанного файла. В скрипте", CommandsType.SIMPLE);
        this.commandManager = commandManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) throws IOException {
        validateConsoleArgs(args);

        final File file = new File(args[0]);
        validateFile(file, args[0]);

        executeScriptFromFile(args[0]);

        Response response = new Response("Операция успешна", "");
        return response;
    }

    /**
     * Проверка аргументов в консольном режиме.
     *
     * @param args аргументы команды
     */
    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда имеет "
                            + "и только имеет один аргумент."
                            + "Пожалуйста, введите:'"
                            + this.getName()
                            + " {абсолютный путь к файлу}"
                    );
        }
    }

    /**
     * Проверка аргументов в режиме скрипта.
     *
     * @param args аргументы команды
     */
    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }

    /**
     * Проверка файла на существование и доступность для чтения.
     *
     * @param file     файл для проверки
     * @param filePath путь к файлу
     */
    private void validateFile(File file, String filePath) throws FileNotFoundException {
        if (!file.exists()) {
            throw new FileNotFoundException("файл " + filePath + " не найден");
        }
        if (!file.canRead()) {
            throw new SecurityException("файл " + filePath + " нечитаемый");
        }
    }

    /**
     * Выполнение скрипта из файла.
     *
     * @param filePath путь к файлу
     * @throws IOException при ошибке ввода-вывода
     */
    private void executeScriptFromFile(String filePath) throws IOException {
        final BufferedReader bufferedReader = new BufferedReader(new FileReader(filePath));

        try {
            String commandLine;
            while ((commandLine = bufferedReader.readLine()) != null) {
                if (commandLine.isEmpty()) {
                    continue;
                }

                executeCommandLine(commandLine, bufferedReader);
            }
        } finally {
            bufferedReader.close();
        }
    }

    /**
     * Выполнение одной строки команды из скрипта.
     *
     * @param commandLine    строка с командой
     * @param bufferedReader буфер для чтения дополнительных строк
     * @throws IOException при ошибке ввода-вывода
     */
    private void executeCommandLine(
            String commandLine, BufferedReader bufferedReader
    ) throws IOException {
        final String[] tokens = commandLine.split("\\s+");
        final String commandName = tokens[0];
        final String[] argsFile = Arrays.copyOfRange(tokens, 1, tokens.length);

        try {
            final Command command = commandManager.getCommands().get(commandName);
            if (command == null) {
                throw new NoSuchCommandException("Указанная команда не существует");
            }

            executeCommand(command, argsFile, bufferedReader);
        } catch (NoSuchCommandException e) {
            System.out.println(e.getMessage());
        }
    }

    /**
     * Выполнение команды с учетом количества строк для чтения.
     *
     * @param command        команда для выполнения
     * @param argsFile       аргументы команды
     * @param bufferedReader буфер для чтения дополнительных строк
     * @throws IOException при ошибке ввода-вывода
     */
    private void executeCommand(
            Command command, String[] argsFile, BufferedReader bufferedReader
    ) throws IOException {
        final int followUpLines = command.getFollowUpLines();
        final int lines1 = 10;
        final int lines2 = 11;

        if (followUpLines == lines1) {
            executeCommandWithFollowUpLines(command, new String[0], followUpLines, bufferedReader);
        } else if (followUpLines == lines2) {
            final List<String> allArgs = new ArrayList<>();
            allArgs.add(argsFile[0]);
            executeCommandWithFollowUpLines(
                    command, allArgs.toArray(new String[0]), followUpLines - 1, bufferedReader);
        } else {
            try {
                command.execute(argsFile, CommandMode.SCRIPT_MODE);
            } catch (ArgumentException | IOException e) {
                System.out.println(e.getMessage());
            }
        }
    }

    /**
     * Выполнение команды с чтением дополнительных строк.
     *
     * @param command        команда для выполнения
     * @param initialArgs    начальные аргументы
     * @param linesToRead    количество строк для чтения
     * @param bufferedReader буфер для чтения
     * @throws IOException при ошибке ввода-вывода
     */
    private void executeCommandWithFollowUpLines(
            Command command, String[] initialArgs, int linesToRead,
            BufferedReader bufferedReader) throws IOException {
        final List<String> allArgs = new ArrayList<>(Arrays.asList(initialArgs));

        for (int i = 0; i < linesToRead; i++) {
            final String line = bufferedReader.readLine();
            if (line == null) {
                break;
            }
            allArgs.add(line.trim());
        }

        final String[] finalArgs = allArgs.toArray(new String[0]);
        try {
            command.execute(finalArgs, CommandMode.SCRIPT_MODE);
        } catch (ArgumentException | IOException e) {
            System.out.println(e.getMessage());
        }
    }
}
