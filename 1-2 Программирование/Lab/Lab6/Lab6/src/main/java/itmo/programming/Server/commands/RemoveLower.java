package itmo.programming.Server.commands;


import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Server.manager.CollectionManager;


/**
 * Класс команды для удаления элементов, меньших введенного.
 */
public class RemoveLower extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public RemoveLower(CollectionManager collectionManager) {
        super("remove_lower", "удалить из коллекции все элементы, меньшие, чем заданный", CommandsType.SIMPLE);
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

        final long id = Long.parseLong(args[0]);
        final boolean idFlag = collectionManager.containsId(id).isEmpty();
        try {
            if (idFlag) {
                throw new ArgumentException("Указанный идентификатор не существует");
            }
            try {
                String string = collectionManager.removeLower(id);
                Response response = new Response(string, "");
                return response;
            } catch (NumberFormatException e) {
                throw new ArgumentException("Неверный формат идентификатора: " + args[0]);
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
                            + " {id}"
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
