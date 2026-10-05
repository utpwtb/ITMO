package Commands;

import Exceptions.ArgumentException;
import Exceptions.NotInitializationException;
import Manager.CollectionManager;

/**
 * Класс команды для получения информации о коллекции
 */
public class Info extends Command {
    /**
     * Конструктор
     */
    public Info() {
        super("info", "вывести в стандартный поток вывода информацию о коллекции");
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
        try {
            System.out.println("Дата инициализации:" + CollectionManager.getInstance().getInitializationTime());
            System.out.println("Количество элементов в коллекции:" + CollectionManager.getInstance().getCollection().size());
            System.out.println("Тип коллекции:" + CollectionManager.getInstance().getCollection().getClass());
        } catch (NotInitializationException e) {
            String message = e.getMessage();
            System.out.println(message);
        }


    }
}
