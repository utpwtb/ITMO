package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import Manager.DocumentManager;
import person.Person;

import java.util.LinkedHashMap;

/**
 * Класс команды для сохранения коллекции в файл
 */
public class Save extends Command{
    /**
     * Конструктор
     */
    public Save() {
        super("save", "сохранить коллекцию в файл");
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
        LinkedHashMap<Long, Person> collection = CollectionManager.getInstance().getCollection();
        try {
            DocumentManager.getInstance().write(collection,"personCollection.xml");
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
