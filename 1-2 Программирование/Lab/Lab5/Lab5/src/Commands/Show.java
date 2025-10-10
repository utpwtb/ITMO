package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/**
 * Класс команды для вывода коллекции
 */
public class Show extends Command{
    /**
     * Конструктор
     */
    public Show() {
        super("show", "вывести в стандартный поток вывода все элементы коллекции в строковом представлении");
    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public void execute(String[] args,CommandMode mode) {
        if (args.length != 0) {
            throw new ArgumentException("Неправильное количество аргументов!Пожалуйста, введите:'" + this.getName() + "'");
        }
        LinkedHashMap<Long, Person> people = CollectionManager.getInstance().getCollection();
        Set<Map.Entry<Long,Person>> entrySet = people.entrySet();
        if (entrySet.isEmpty()){
            System.out.println("Коллекция пуста.");
        }else {
            for (Map.Entry<Long, Person> entry : entrySet) {
                Person value = entry.getValue();
                System.out.println(value.toString());
            }
        }
    }
}
