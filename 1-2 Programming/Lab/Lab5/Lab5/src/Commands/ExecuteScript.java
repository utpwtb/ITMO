package Commands;

import Exceptions.ArgumentException;
import Exceptions.NoSuchCommandException;
import Manager.CommandManager;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Класс команды для выполнения скрипта из файла
 */
public class ExecuteScript extends Command {

    /**
     * Конструктор
     */
    public ExecuteScript() {
        super("execute_script", "считать и исполнить скрипт из указанного файла. В скрипте");
    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public void execute(String[] args,CommandMode mode) throws IOException {
        if (args.length != 1) {
            throw new ArgumentException("Неправильное количество аргументов!Эта команда имеет и только имеет один аргумент.Пожалуйста, введите:'" + this.getName()
                    + " {абсолютный путь к файлу}");
        }

        File file = new File(args[0]);
        if (!file.exists()) {
            throw new FileNotFoundException("файл " + args[0] + " не найден");
        }
        if (!file.canRead()) {
            throw new SecurityException("файл " + args[0] + " нечитаемый");
        }

        BufferedReader bufferedReader = new BufferedReader(new FileReader(args[0]));

        String commandLine;
        while ((commandLine = bufferedReader.readLine()) != null) {
            if (commandLine.isEmpty()) continue;
            String[] tokens = commandLine.split("\\s+");
            String command = tokens[0];
            String[] argsFile = Arrays.copyOfRange(tokens, 1, tokens.length);
            try {
                Command command1 = CommandManager.getInstance().getCommands().get(command);
                if (command1 == null) {
                    throw new NoSuchCommandException("Указанная команда не существует");
                }
                List<String> allArgs = new ArrayList<>();
                int followUpLines = command1.getFollowUpLines();
                if (followUpLines == 10) {
                    for (int i = 0; i < followUpLines; i++) {
                        String line = bufferedReader.readLine();
                        if (line == null) break;
                        allArgs.add(line.trim());
                    }
                    String[] finalArgs = allArgs.toArray(new String[0]);
                    command1.execute(finalArgs,CommandMode.SCRIPT_MODE);
                } else if (followUpLines == 11) {
                    allArgs.add(argsFile[0]);
                    for (int i = 0; i < followUpLines-1; i++) {
                        String line = bufferedReader.readLine();
                        if (line == null) break;
                        allArgs.add(line.trim());
                    }
                    String[] finalArgs = allArgs.toArray(new String[0]);
                    command1.execute(finalArgs,CommandMode.SCRIPT_MODE);
                } else {
                    try {
                        command1.execute(argsFile,CommandMode.SCRIPT_MODE);
                    } catch (ArgumentException | IOException e) {
                        System.out.println(e.getMessage());
                    }
                }
            } catch (NoSuchCommandException e) {
                System.out.println(e.getMessage());
            }
        }
        bufferedReader.close();
    }

}
