package itmo.programming.Common.utility;

import itmo.programming.Common.utility.createperson.PersonFactory;
import itmo.programming.Server.commands.Add;
import itmo.programming.Server.commands.Clear;
import itmo.programming.Server.commands.ExecuteScript;
import itmo.programming.Server.commands.Exit;
import itmo.programming.Server.commands.FilterContainsName;
import itmo.programming.Server.commands.FilterLessThanHairColor;
import itmo.programming.Server.commands.Help;
import itmo.programming.Server.commands.Info;
import itmo.programming.Server.commands.Insert;
import itmo.programming.Server.commands.MinByCreationDate;
import itmo.programming.Server.commands.RemoveGreater;
import itmo.programming.Server.commands.RemoveGreaterKey;
import itmo.programming.Server.commands.RemoveKey;
import itmo.programming.Server.commands.RemoveLower;
import itmo.programming.Server.commands.Save;
import itmo.programming.Server.commands.Show;
import itmo.programming.Server.commands.Update;
import itmo.programming.Server.manager.CollectionManager;
import itmo.programming.Server.manager.CommandManager;
import itmo.programming.Server.manager.DocumentManager;

/**
 * команда утилиты.
 */
public class CommandUtils {

    /**
     * зарегистрировать все команды.
     */
    public static void commandInitialization(
            CommandManager manager, CollectionManager collectionManager) {
        final DocumentManager documentManager = new DocumentManager(collectionManager);
        final PersonFactory personFactory = new PersonFactory();

        manager.register("help", new Help(manager));
        manager.register("add", new Add(collectionManager, personFactory));
        manager.register("info", new Info(collectionManager));
        manager.register("show", new Show(collectionManager));
        manager.register("insert", new Insert(collectionManager, personFactory));
        manager.register("update", new Update(collectionManager, personFactory));
        manager.register("remove_key", new RemoveKey(collectionManager));
        manager.register("clear", new Clear(collectionManager));
        manager.register("save", new Save(collectionManager, documentManager));
        manager.register("execute_script", new ExecuteScript(manager));
        manager.register("exit", new Exit());
        manager.register("remove_greater", new RemoveGreater(collectionManager));
        manager.register("remove_lower", new RemoveLower(collectionManager));
        manager.register("remove_greater_key", new RemoveGreaterKey(collectionManager));
        manager.register("min_by_creation_date", new MinByCreationDate(collectionManager));
        manager.register("filter_contains_name", new FilterContainsName(collectionManager));
        manager.register(
                "filter_less_than_hair_color", new FilterLessThanHairColor(collectionManager)
        );
    }
}
