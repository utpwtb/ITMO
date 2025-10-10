package utlity;

import Commands.Command;
import Commands.CommandMode;
import Exceptions.ArgumentException;
import Exceptions.NoSuchCommandException;
import Manager.CommandManager;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Scanner;
import java.util.Arrays;

/**
 * Выполнение команд в основной программе
 */
public class Runner {
    /**
     * Выполнение команд
     */
    public static void runCommand() {
        try {
            LinkedHashMap<String, String[]> line = readLine(new Scanner(System.in));
            String command = line.keySet().iterator().next();
            String[] arg = line.get(command);

            Command command1 = CommandManager.getInstance().getCommands().get(command);
            if (command1 == null) {
                throw new NoSuchCommandException("Указанная команда не существует");
            }
            try {
                command1.execute(arg, CommandMode.CONSOLE_MODE);
            } catch (ArgumentException e) {
                System.out.println(e.getMessage());
            } catch (FileNotFoundException e) {
                System.out.println("Файл не существует");
            } catch (NumberFormatException e) {
                System.out.println("Параметр должен быть числом");
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        } catch (NoSuchCommandException e) {
            System.out.println(e.getMessage());
        }catch (ArgumentException e) {
            System.out.println(e.getMessage());
        }


    }

    /**
     *Прочитайте каждую строку
     * @param scanner сканер
     * @return Коллекция
     */
    public static LinkedHashMap<String, String[]> readLine(Scanner scanner) {
        String input = scanner.nextLine().trim();
        if (input.isEmpty()) {
            throw new ArgumentException("Ввод не может быть пустым");
        }
        String[] tokens = input.split("\\s+");

        String command = tokens[0].toLowerCase();
        String[] args = Arrays.copyOfRange(tokens, 1, tokens.length);
        LinkedHashMap<String, String[]> result = new LinkedHashMap<>();
        result.put(command, args);
        return result;
    }
}
