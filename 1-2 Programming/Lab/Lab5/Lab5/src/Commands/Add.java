package Commands;

import Exceptions.ArgumentException;
import person.*;
import utlity.*;

import java.util.Scanner;

/**
 * Класс команды для добавления нового элемента в коллекцию
 */
public class Add extends Command {

    /**
     * Конструктор
     */
    public Add() {
        super("add", "добавить новый элемент");
    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public void execute(String[] args, CommandMode mode) {
        Person person;

        if (args.length != 0 && mode.equals(CommandMode.CONSOLE_MODE)) {
            throw new ArgumentException("Неправильное количество аргументов!");
        } else if (args.length == 0 && mode.equals(CommandMode.CONSOLE_MODE)) {
            InputHandler inputHandler = new ConsoleInputHandler(new Scanner(System.in));
            PersonInputHandler personInputHandler = new PersonInputHandler(inputHandler);
            person = personInputHandler.createPersonFromInput();
            OperationSuccessful.judge(person);
            return;
        }

        if (args.length != getFollowUpLines() && mode.equals(CommandMode.SCRIPT_MODE)) {
            throw new ArgumentException("Неправильное количество аргументов!");
        } else if (args.length == getFollowUpLines() && mode.equals(CommandMode.SCRIPT_MODE)){
            ScriptInputHandler scriptInputHandler = new ScriptInputHandler(args);
            person = scriptInputHandler.createPersonFromScript();
            OperationSuccessful.judge(person);
        }
    }

    /**
     * Получить количество строк для чтения в режиме скрипта
     *
     * @return количество
     */
    @Override
    public int getFollowUpLines() {
        return 10;
    }
}
