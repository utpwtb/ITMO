package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;
import utlity.*;

import java.util.*;

/**
 * Класс команды для добавления нового элемента с указанным ключом
 */
public class Insert extends Command {
    /**
     * Конструктор
     */
    public Insert() {
        super("insert", "добавить новый элемент с заданным ключом");
    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public void execute(String[] args,CommandMode mode) {
        try {
            Long.parseLong(args[0].trim());
        } catch (NumberFormatException e) {
            throw new NumberFormatException();
        }
        long key = Long.parseLong(args[0]);
        LinkedHashMap<Long, Person> collection = CollectionManager.getInstance().getCollection();

        Person person;

        try {
            if (collection.containsKey(key)) {
                throw new ArgumentException("Указанный идентификатор уже существует");
            } else {
                if (args.length != 1 && mode.equals(CommandMode.CONSOLE_MODE)) {
                    throw new ArgumentException("Неправильное количество аргументов!Эта команда имеет и только имеет один аргумент.Пожалуйста, введите:'" + this.getName()
                            + " {key}");
                } else if (args.length == 1 && mode.equals(CommandMode.CONSOLE_MODE)) {
                    InputHandler inputHandler = new ConsoleInputHandler(new Scanner(System.in));
                    PersonInputHandler personInputHandler = new PersonInputHandler(inputHandler);
                    person = personInputHandler.createPersonFromInput();
                    OperationSuccessful.judge(person);
                    return;
                }

                if (args.length != getFollowUpLines() && mode.equals(CommandMode.SCRIPT_MODE)){
                    throw new ArgumentException("Неправильное количество аргументов!");
                } else if (args.length == getFollowUpLines() && mode.equals(CommandMode.SCRIPT_MODE)) {
                    List<String> list = new ArrayList<>(Arrays.asList(args));
                    list.remove(0);
                    String[] array = list.toArray(new String[0]);
                    ScriptInputHandler scriptInputHandler = new ScriptInputHandler(array);
                    person = scriptInputHandler.createPersonFromScript();
                    OperationSuccessful.judge(person);
                }
            }
        } catch (ArgumentException e) {
            System.out.println(e.getMessage());
        }
    }

    /**
     * Получить количество строк для чтения в режиме скрипта
     *
     * @return количество
     */
    @Override
    public int getFollowUpLines() {
        return 11;
    }
}
