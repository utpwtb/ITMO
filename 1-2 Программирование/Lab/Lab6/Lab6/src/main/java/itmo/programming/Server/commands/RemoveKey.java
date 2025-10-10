package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Server.manager.CollectionManager;

/**
 * Класс команды для удаления элементов из коллекции на основе ключа.
 */
public class RemoveKey extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public RemoveKey(CollectionManager collectionManager) {
        super("remove_key", "удалить элемент из коллекции по его ключу", CommandsType.SIMPLE);
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

        final long key = Long.parseLong(args[0]);

        try {
            if (!collectionManager.containsKey(key)) {
                throw new ArgumentException("Указанный идентификатор не существует");
            }
            final boolean isRemoved = collectionManager.removeByKey(key);
            Response response = new Response();
            if (isRemoved) {
                response.setMessage("Элемент успешно удален");
                response.setCollectionToStr("");
                return response;
            } else {
                response.setMessage("Удаление элемента не удалось");
                response.setCollectionToStr("");
                return response;
            }

        } catch (ArgumentException e) {
            System.out.println(e.getMessage());
        }
        return null;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда имеет "
                            + "и только имеет один аргумент.Пожалуйста, введите:'"
                            + this.getName()
                            + " {key}"
                    );
        }
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("Параметр должен быть числом"
                    );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
