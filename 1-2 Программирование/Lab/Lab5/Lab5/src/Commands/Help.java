package Commands;

import Exceptions.ArgumentException;
import Manager.CommandManager;

import java.util.stream.Collectors;

/**
 * Класс команды для вывода справки по всем доступным командам
 */
public class Help extends Command {

    /**
     * Конструктор
     */
    public Help() {
        super("help", "вывести справку по доступным командам");

    }

    /**
     * Исполнение команды
     *
     * @param args массив с аргументами
     * @param mode Режим исполнения
     */
    @Override
    public void execute(String[] args,CommandMode mode) throws ArgumentException {
        if (args.length != 0) {
            throw new ArgumentException("Неправильное количество аргументов!Пожалуйста, введите:'" + this.getName() + "'");
        }
        System.out.println(CommandManager.getInstance().getCommands().values().stream()
                .map(command -> String.format("%-35s%-1s%n", command.getName(), command.getDescription()))
                .collect(Collectors.joining()));
    }

}
