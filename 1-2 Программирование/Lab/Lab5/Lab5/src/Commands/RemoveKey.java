package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;

import java.util.LinkedHashMap;

/**
 * Класс команды для удаления элементов из коллекции на основе ключа
 */
public class RemoveKey extends Command{
    /**
     * Конструктор
     */
    public RemoveKey() {
        super("remove_key", "удалить элемент из коллекции по его ключу");
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
        LinkedHashMap<Long, Person> collection = CollectionManager.getInstance().getCollection();
        try {
            if (!collection.containsKey(key)) {
                throw new ArgumentException("Указанный идентификатор не существует");
            }
            collection.remove(key);
            if (!collection.containsKey(key)){
                System.out.println("Элемент успешно удален");
            }else {
                System.out.println("Удаление элемента не удалось");
            }

        }catch (ArgumentException e){
            System.out.println(e.getMessage());
        }
    }
}
