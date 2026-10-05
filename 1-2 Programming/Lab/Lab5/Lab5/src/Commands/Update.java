package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;
import utlity.*;

import java.util.*;

/**
 * Класс команды для обновления элемента коллекции
 */
public class Update extends Command{
    /**
     * Конструктор
     */
    public Update() {
        super("update", "обновить значение элемента коллекции, id которого равен заданному");
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
        long id = Long.parseLong(args[0]);

        boolean idFlag = IdFlag.isIdExists(id);
        try {
            if (!idFlag) {
                throw new ArgumentException("Указанный идентификатор не существует");
            }else {
                LinkedHashMap<Long, Person> collection = CollectionManager.getInstance().getCollection();
                collection.remove(id);

                Person person;
                if (args.length != 1 && mode.equals(CommandMode.CONSOLE_MODE)) {
                    throw new ArgumentException("Неправильное количество аргументов!Эта команда имеет и только имеет один аргумент.Пожалуйста, введите:'" + this.getName()
                            + " {id}");
                } else if (args.length == 1 && mode.equals(CommandMode.CONSOLE_MODE)) {
                    System.out.println("Введите новую информацию для человека id : " + id);
                    InputHandler inputHandler = new ConsoleInputHandler(new Scanner(System.in));
                    PersonInputHandler personInputHandler = new PersonInputHandler(inputHandler);
                    person = personInputHandler.createPersonFromInputWithId(id);
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
                    person = scriptInputHandler.createPersonFromScriptWithId(id);
                    OperationSuccessful.judge(person);
                }
            }
        }catch (ArgumentException e){
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
