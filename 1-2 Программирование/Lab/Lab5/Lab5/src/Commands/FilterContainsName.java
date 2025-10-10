package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;

import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Класс команды для вывода элементов, значение поля `name` которых содержит указанную подстроку.
 */
public class FilterContainsName extends Command {

    /**
     * Конструктор
     */
    public FilterContainsName() {
        super("filter_contains_name", "вывести элементы, значение поля name которых содержит заданную подстроку");
    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public void execute(String[] args,CommandMode mode) {
        if (args.length != 1) {
            throw new ArgumentException("Неправильное количество аргументов!Эта команда имеет и только имеет один аргумент.Пожалуйста, введите:'" + this.getName()
                    + " {id}");
        }
        CollectionManager collectionManager = CollectionManager.getInstance();
        LinkedHashMap<Long, Person> collection = collectionManager.getCollection();

        Iterator<Map.Entry<Long, Person>> iterator = collection.entrySet().iterator();
        boolean isRemoved = false;
        while (iterator.hasNext()) {
            Map.Entry<Long, Person> entry = iterator.next();
            Person person = entry.getValue();
            if (person.getName().contains(args[0])) {
                iterator.remove();
                isRemoved = true;
            }
        }

        if (isRemoved) {
            System.out.println("Имена, содержащие '" + args[0] + "', успешно удалены.");
        } else {
            System.out.println("Элементы с именем, содержащим '" + args[0] + "', не найдены.");
        }
    }


}
