package Commands;

import Exceptions.ArgumentException;
import Manager.CollectionManager;
import person.Person;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import static utlity.IdFlag.isIdExists;

/**
 * Класс команды для удаления элементов, больших введенного
 */
public class RemoveGreater extends Command{
    /**
     * Конструктор
     */
    public RemoveGreater() {
        super("remove_greater", "удалить из коллекции все элементы, превышающие заданный");
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
                    + " {id}");
        }
        try {
            Long.parseLong(args[0].trim());
        } catch (NumberFormatException e) {
            throw new NumberFormatException();
        }
        long id = Long.parseLong(args[0]);
        try {
            if (!isIdExists(id)) {
                throw new ArgumentException("Указанный идентификатор не существует");
            }

            LinkedHashMap<Long, Person> collection = CollectionManager.getInstance().getCollection();
            Integer targetHashCode = null;

            for (Person person : collection.values()) {
                if (person.getId() == id) {
                   targetHashCode = person.getName().hashCode();
                    break;
                }
            }

            Integer finalTargetHashCode = targetHashCode;
            Set<Long> toRemove = collection.entrySet().stream()
                    .filter(entry -> entry.getValue().getName().hashCode() > finalTargetHashCode)
                    .map(Map.Entry::getKey)
                    .collect(Collectors.toSet());

            toRemove.forEach(collection::remove);

        } catch (NumberFormatException e) {
            throw new ArgumentException("Неверный формат идентификатора: " + args[0]);
        }
    }

}
