package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Server.manager.CollectionManager;

import java.util.Map;
import java.util.Set;

/**
 * Класс команды для вывода коллекции.
 */
public class Show extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public Show(CollectionManager collectionManager) {
        super(
                "show",
                "вывести в стандартный поток вывода все элементы коллекции "
                        + "в строковом представлении", CommandsType.SIMPLE);
        this.collectionManager = collectionManager;
    }

    /**
     * Исполнение команды.
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public Response execute(String[] args, CommandMode mode) {
        validateConsoleArgs(args);
        final Set<Map.Entry<Long, Person>> entrySet = collectionManager.getAllEntries();
        Response response = new Response();

        if (entrySet.isEmpty()) {
            response.setMessage("Коллекция пуста.");
            response.setCollectionToStr("");
        } else {
            // 创建一个StringBuilder来收集所有元素信息
            StringBuilder allElements = new StringBuilder();
            for (Map.Entry<Long, Person> entry : entrySet) {
                allElements.append("key : ").append(entry.getKey()).append("\n");
                allElements.append(entry.getValue().toString()).append("\n\n");
            }

            response.setMessage("Элементы коллекции:"); // 可以设置适当的消息
            response.setCollectionToStr(allElements.toString());
        }

        return response; // 循环结束后再返回完整结果
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 0) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда не имеет параметров."
                    );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
