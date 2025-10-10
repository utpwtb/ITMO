package itmo.programming.common.utility.createperson;

import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import java.util.Scanner;

/**
 * Фабрика для создания объектов Person.
 */
public class PersonFactory {

    /**
     * Создает Person из консольного ввода.
     *
     * @return созданный объект Person
     */
    public Person createFromConsole() {
        final InputHandler inputHandler = new ConsoleInputHandler(new Scanner(System.in));
        final PersonInputHandler personInputHandler = new PersonInputHandler(inputHandler);
        return personInputHandler.createPersonFromInput();
    }

    /**
     * Создает Person из скриптовых данных.
     *
     * @param scriptArgs аргументы из скрипта
     * @return созданный объект Person
     */
    public Person createFromScript(String[] scriptArgs) {
        final ScriptInputHandler scriptInputHandler = new ScriptInputHandler(scriptArgs);
        return scriptInputHandler.createPersonFromScript();
    }

    /**
     * Создает Person из консольного ввода id.
     *
     * @return созданный объект Person
     */
    public Person createFromConsoleWithId(long id) {
        final InputHandler inputHandler = new ConsoleInputHandler(new Scanner(System.in));
        final PersonInputHandler personInputHandler = new PersonInputHandler(inputHandler);
        return personInputHandler.createPersonFromInputWithId(id);
    }

    /**
     * Создает Person из скриптовых данных с id.
     *
     * @param scriptArgs аргументы из скрипта
     * @return созданный объект Person
     */
    public Person createFromScriptWithId(String[] scriptArgs, long id) {
        final ScriptInputHandler scriptInputHandler = new ScriptInputHandler(scriptArgs);
        return scriptInputHandler.createPersonFromScriptWithId(id);
    }

    /**
     * Создает Person в зависимости от режима выполнения команды.
     *
     * @param args аргументы команды
     * @param mode режим выполнения команды
     * @return созданный объект Person
     */
    public Person createPerson(String[] args, CommandMode mode) {
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            return createFromConsole();
        } else {
            return createFromScript(args);
        }
    }
}
