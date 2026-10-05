package itmo.programming.server.utility;

import itmo.programming.server.commands.Add;
import itmo.programming.server.commands.Clear;
import itmo.programming.server.commands.ExecuteScript;
import itmo.programming.server.commands.Exit;
import itmo.programming.server.commands.FilterContainsName;
import itmo.programming.server.commands.FilterLessThanHairColor;
import itmo.programming.server.commands.Help;
import itmo.programming.server.commands.Info;
import itmo.programming.server.commands.Insert;
import itmo.programming.server.commands.MinByCreationDate;
import itmo.programming.server.commands.RemoveGreater;
import itmo.programming.server.commands.RemoveGreaterKey;
import itmo.programming.server.commands.RemoveKey;
import itmo.programming.server.commands.RemoveLower;
import itmo.programming.server.commands.Save;
import itmo.programming.server.commands.Show;
import itmo.programming.server.commands.Update;
import itmo.programming.server.manager.CollectionManager;
import itmo.programming.server.manager.CommandManager;
import itmo.programming.server.manager.DocumentManager;

/**
 * Утилитный класс для инициализации и регистрации команд в системе.
 */
public class CommandUtils {

    /**
     * Регистрирует все доступные команды в менеджере команд.
     *
     * @param manager менеджер команд для регистрации
     * @param collectionManager менеджер коллекции для работы с данными
     */
    public static void commandInitialization(CommandManager manager,
                                             CollectionManager collectionManager) {
        final DocumentManager documentManager = new DocumentManager(collectionManager);
        manager.register("help", new Help(manager));
        manager.register("add", new Add(collectionManager));
        manager.register("info", new Info(collectionManager));
        manager.register("show", new Show(collectionManager));
        manager.register("insert", new Insert(collectionManager));
        manager.register("update", new Update(collectionManager));
        manager.register("remove_key", new RemoveKey(collectionManager));
        manager.register("clear", new Clear(collectionManager));
        manager.register("save", new Save(collectionManager, documentManager));
        manager.register("execute_script", new ExecuteScript(manager));
        manager.register("exit", new Exit());
        manager.register("remove_greater", new RemoveGreater(collectionManager));
        manager.register("remove_lower", new RemoveLower(collectionManager));
        manager.register("remove_greater_key",
                new RemoveGreaterKey(collectionManager));
        manager.register("min_by_creation_date", new MinByCreationDate(collectionManager));
        manager.register("filter_contains_name", new FilterContainsName(collectionManager));
        manager.register(
                "filter_less_than_hair_color", new FilterLessThanHairColor(collectionManager)
        );
    }
}
