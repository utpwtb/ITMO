package itmo.programming.client.utility;

import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.createperson.PersonFactory;
import java.util.Arrays;

/**
 * Утилитный класс для создания объектов Person.
 * Предоставляет методы для создания Person в разных режимах и с разными параметрами.
 */
public class CreatPerson {

    /**
     * Фабрика для создания объектов Person.
     */
    private final PersonFactory personFactory;

    /**
     * Коструктор.
     *
     * @param personFactory personFactory
     */
    public CreatPerson(PersonFactory personFactory) {
        this.personFactory = personFactory;
    }

    /**
     * Создание объекта Person в зависимости от режима выполнения.
     *
     * @param args аргументы команды
     * @param mode режим выполнения
     * @param id   идентификатор обновляемого элемента
     * @return созданный объект Person
     */
    public Person createPersonUpdate(String[] args, CommandMode mode, long id) {
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            System.out.println("Введите новую информацию для человека id : " + id);
            return personFactory.createFromConsoleWithId(id);
        } else {
            return personFactory.createFromScriptWithId(
                    Arrays.copyOfRange(args, 1, args.length), id
            );
        }
    }

    /**
     * Создание объекта Person в зависимости от режима выполнения.
     *
     * @param args аргументы команды
     * @param mode режим выполнения
     * @return созданный объект Person
     */
    public Person createPersonInsert(String[] args, CommandMode mode) {
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            return personFactory.createFromConsole();
        } else {
            return personFactory.createFromScript(Arrays.copyOfRange(args, 1, args.length));
        }
    }

    /**
     * Создание объекта Person в зависимости от режима выполнения.
     *
     * @param args аргументы команды
     * @param mode режим выполнения
     * @return созданный объект Person
     */
    public Person createPersonAdd(String[] args, CommandMode mode) {
        return personFactory.createPerson(args, mode);
    }
}
