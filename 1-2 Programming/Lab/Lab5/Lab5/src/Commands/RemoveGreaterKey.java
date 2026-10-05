package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;

import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Класс команды для удаления всех элементов из коллекции с ключами, превышающими указанное значение.
 */
public class RemoveGreaterKey extends Command {
    /**
     * Конструктор
     */
    public RemoveGreaterKey() {
        super("remove_greater_key", "удалить из коллекции все элементы, ключ которых превышает заданный");
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
                    + " {key}");
        }
        try {
            Long.parseLong(args[0].trim());
        } catch (NumberFormatException e) {
            throw new NumberFormatException();
        }
        long key = Long.parseLong(args[0]);

        CollectionManager collectionManager = CollectionManager.getInstance();
        LinkedHashMap<Long, Person> collection = collectionManager.getCollection();
        Iterator<Map.Entry<Long, Person>> iterator = collection.entrySet().iterator();

        try {
            if (!collection.containsKey(key)) {
                throw new ArgumentException("Указанный идентификатор не существует");
            }

            boolean isRemoved = false;
            while (iterator.hasNext()) {
                Map.Entry<Long, Person> entry = iterator.next();
                long entryId = entry.getKey();
                if (entryId > key) {
                    iterator.remove();
                    isRemoved = true;
                }
            }

            if (isRemoved) {
                System.out.println("Элементы с key больше " + key + " успешно удалены.");
            } else {
                System.out.println("Элементы с key больше " + key + " не найдены.");
            }
        } catch (ArgumentException e) {
            System.out.println(e.getMessage());
        }

    }
}
