package utlity;

import Commands.*;
import Manager.CommandManager;

/**
 * команда утилиты
 */
public class CommandUtils {

    /**
     * зарегистрировать все команды
     */
    public static void commandInitialization() {
        CommandManager manager = CommandManager.getInstance();

        manager.register("help", new Help());
        manager.register("add", new Add());
        manager.register("info", new Info());
        manager.register("show", new Show());
        manager.register("insert", new Insert());
        manager.register("update", new Update());
        manager.register("remove_key", new RemoveKey());
        manager.register("clear", new Clear());
        manager.register("save", new Save());
        manager.register("execute_script", new ExecuteScript());
        manager.register("exit", new Exit());
        manager.register("remove_greater", new RemoveGreater());
        manager.register("remove_lower", new RemoveLower());
        manager.register("remove_greater_key", new RemoveGreaterKey());
        manager.register("min_by_creation_date", new MinByCreationDate());
        manager.register("filter_contains_name", new FilterContainsName());
        manager.register("filter_less_than_hair_color", new FilterLessThanHairColor());
    }

}
