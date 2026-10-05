package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;

import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/**
 * Класс команды для вывода любого объекта в коллекции, имеющего наименьшее значение поля `creationDate`.
 */
public class MinByCreationDate extends Command{
    /**
     * Конструктор
     */
    public MinByCreationDate() {
        super("min_by_creation_date", "вывести любой объект из коллекции, значение поля creationDate которого является минимальным");
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
        CollectionManager collectionManager = CollectionManager.getInstance();
        LinkedHashMap<Long, Person> collection = collectionManager.getCollection();

        Set<Map.Entry<Long, Person>> entrySet = collection.entrySet();

        long tempId = 0;
        Date temp = new Date();
        for (Map.Entry<Long, Person> entry : entrySet) {
            Person person = entry.getValue();
            if (person.getCreationDate().before(temp)){
                temp = person.getCreationDate();
                tempId = person.getId();
            }
        }
        boolean remove = collection.remove(tempId, collection.get(tempId));
        if (remove){
            System.out.println("Элемент с самым ранним временем создания успешно удален");
        }else {
            System.out.println("Удаление не удалось");
        }
    }
}
