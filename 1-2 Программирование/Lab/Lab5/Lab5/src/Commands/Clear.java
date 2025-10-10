package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;

/**
 * Класс команды для очищения коллекции
 */
public class Clear extends Command{

    /**
     * Конструктор
     */
    public Clear() {
        super("clear", "очистить коллекцию");
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
        CollectionManager.getInstance().getCollection().clear();
    }


}
