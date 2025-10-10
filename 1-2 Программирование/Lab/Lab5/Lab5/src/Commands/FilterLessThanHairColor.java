package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.HairColor;
import person.Person;
import utlity.EnumUtils;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/**
 * Класс команды для вывода элементов, у которых значение поля hairColor меньше указанного значения.
 */
public class FilterLessThanHairColor extends Command {
    /**
     * Конструктор
     */
    public FilterLessThanHairColor() {
        super("filter_less_than_hair_color", "вывести элементы, значение поля hairColor которых меньше заданного");
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
                    + " {HairColor}'(Существующие цвета: )" + EnumUtils.showEnum(HairColor.class));
        }
        HairColor hairColor = EnumUtils.fromStringIgnoreCase(HairColor.class, args[0]);
        if (hairColor == null){
            throw new ArgumentException("Указанный цвет не существует.Существующие цвета: " + EnumUtils.showEnum(HairColor.class));
        }
        LinkedHashMap<Long, Person> people = CollectionManager.getInstance().getCollection();
        Set<Map.Entry<Long, Person>> entrySet = people.entrySet();
        if (entrySet.isEmpty()) {
            System.out.println("Коллекция пуста.");
        } else {
            for (Map.Entry<Long, Person> entry : entrySet) {
                Person value = entry.getValue();
                if (hairColor.ordinal() > value.getHairColor().ordinal()) {
                    System.out.println("Успешное удаление элементов, меньших значения " + args[0] + "\n");
                }
            }
        }
    }


}
