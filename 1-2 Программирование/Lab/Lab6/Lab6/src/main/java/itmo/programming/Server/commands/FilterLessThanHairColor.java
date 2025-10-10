package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.HairColor;
import itmo.programming.Common.utility.EnumUtils;
import itmo.programming.Server.manager.CollectionManager;

/**
 * Класс команды для вывода элементов, у которых значение поля hairColor меньше указанного значения.
 */
public class FilterLessThanHairColor extends Command {
    /**
     * Менеджер коллекции.
     */
    private final CollectionManager collectionManager;

    /**
     * Конструктор.
     */
    public FilterLessThanHairColor(CollectionManager collectionManager) {
        super(
                "filter_less_than_hair_color",
                "вывести элементы, значение поля hairColor которых меньше заданного", CommandsType.SIMPLE);
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
        final HairColor hairColor = EnumUtils.fromStringIgnoreCase(HairColor.class, args[0]);
        if (hairColor == null) {
            throw new ArgumentException(
                    "Указанный цвет не существует.Существующие цвета: "
                            + EnumUtils.showEnum(HairColor.class));
        }
        Response response = new Response("Операция успешна"
                , collectionManager.filterLessThanHairColor(hairColor).toString());
        return response;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда имеет "
                            + "и только имеет один аргумент.Пожалуйста, введите:'"
                            + this.getName()
                            + " {HairColor}'(Существующие цвета: )"
                            + EnumUtils.showEnum(HairColor.class)
                    );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
