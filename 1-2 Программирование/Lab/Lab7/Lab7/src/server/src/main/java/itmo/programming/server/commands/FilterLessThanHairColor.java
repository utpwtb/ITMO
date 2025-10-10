package itmo.programming.server.commands;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.HairColor;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.EnumUtils;
import itmo.programming.server.manager.CollectionManager;

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
                "вывести элементы, значение поля hairColor которых меньше заданного");
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

        final HairColor hairColor = EnumUtils.fromStringIgnoreCase(HairColor.class, args[0]);
        if (hairColor == null) {
            throw new ArgumentException(
                    "Указанный цвет не существует.Существующие цвета: "
                            + EnumUtils.showEnum(HairColor.class));
        }
        final Response response = new Response("Операция успешна",
                collectionManager.filterLessThanHairColor(hairColor).toString());
        return response;
    }


}
