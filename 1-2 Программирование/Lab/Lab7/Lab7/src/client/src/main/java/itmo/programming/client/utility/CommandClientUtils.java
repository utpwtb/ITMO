package itmo.programming.client.utility;

import itmo.programming.client.commandsclient.AddClient;
import itmo.programming.client.commandsclient.ClearClient;
import itmo.programming.client.commandsclient.ExecuteScriptClient;
import itmo.programming.client.commandsclient.ExitClient;
import itmo.programming.client.commandsclient.FilterContainsNameClient;
import itmo.programming.client.commandsclient.FilterLessThanHairColorClient;
import itmo.programming.client.commandsclient.HelpClient;
import itmo.programming.client.commandsclient.InfoClient;
import itmo.programming.client.commandsclient.InsertClient;
import itmo.programming.client.commandsclient.MinByCreationDateClient;
import itmo.programming.client.commandsclient.RemoveGreaterClient;
import itmo.programming.client.commandsclient.RemoveGreaterKeyClient;
import itmo.programming.client.commandsclient.RemoveKeyClient;
import itmo.programming.client.commandsclient.RemoveLowerClient;
import itmo.programming.client.commandsclient.SaveClient;
import itmo.programming.client.commandsclient.ShowClient;
import itmo.programming.client.commandsclient.UpdateClient;
import itmo.programming.client.manager.CommandClientManager;
import itmo.programming.client.manager.NetWorkManager;

/**
 * CommandClientUtils.
 */
public class CommandClientUtils {

    /**
     * зарегистрировать все команды.
     */
    public static void commandClientInt(
            CommandClientManager manager,
            NetWorkManager netWorkManager) {
        manager.register("help", new HelpClient());
        manager.register("add", new AddClient());
        manager.register("info", new InfoClient());
        manager.register("show", new ShowClient());
        manager.register("insert", new InsertClient(netWorkManager));
        manager.register("update", new UpdateClient(netWorkManager));
        manager.register("remove_key", new RemoveKeyClient(netWorkManager));
        manager.register("clear", new ClearClient());
        manager.register("save", new SaveClient());
        manager.register("execute_script", new ExecuteScriptClient());
        manager.register("exit", new ExitClient());
        manager.register("remove_greater", new RemoveGreaterClient(netWorkManager));
        manager.register("remove_lower", new RemoveLowerClient(netWorkManager));
        manager.register("remove_greater_key", new RemoveGreaterKeyClient(netWorkManager));
        manager.register("min_by_creation_date", new MinByCreationDateClient());
        manager.register("filter_contains_name", new FilterContainsNameClient());
        manager.register(
                "filter_less_than_hair_color", new FilterLessThanHairColorClient());

    }
}
