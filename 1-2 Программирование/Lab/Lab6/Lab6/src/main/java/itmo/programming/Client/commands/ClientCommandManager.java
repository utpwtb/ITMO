package itmo.programming.Client.commands;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.utility.createperson.PersonFactory;

import java.util.HashMap;
import java.util.Map;

/**
 * 客户端命令管理器
 */
public class ClientCommandManager {
    private final Map<String, ClientCommand> commands = new HashMap<>();
    
    /**
     * 初始化命令管理器
     * @param personFactory Person对象工厂
     */
    public ClientCommandManager(PersonFactory personFactory) {
        // 注册交互式命令，使用PersonFactory
        registerCommand(new ClientAddCommand(personFactory));
        registerCommand(new ClientUpdateCommand(personFactory));
        registerCommand(new ClientInsertCommand(personFactory));
        
        // 注册其他简单命令
        registerCommand(new ClientSimpleCommand("help", "вывести справку по доступным командам"));
        registerCommand(new ClientSimpleCommand("info", "вывести информацию о коллекции"));
        registerCommand(new ClientSimpleCommand("show", "вывести все элементы коллекции"));
        registerCommand(new ClientSimpleCommand("clear", "очистить коллекцию"));
        registerCommand(new ClientSimpleCommand("exit", "завершить программу"));
        registerCommand(new ClientSimpleCommand("save", "сохранить коллекцию в файл"));
        registerCommand(new ClientSimpleCommand("remove_key", "удалить элемент по ключу"));
        registerCommand(new ClientSimpleCommand("remove_greater", "удалить элементы больше заданного"));
        registerCommand(new ClientSimpleCommand("remove_lower", "удалить элементы меньше заданного"));
        registerCommand(new ClientSimpleCommand("remove_greater_key", "удалить элементы с ключом больше заданного"));
        registerCommand(new ClientSimpleCommand("min_by_creation_date", "вывести элемент с минимальной датой создания"));
        registerCommand(new ClientSimpleCommand("filter_contains_name", "вывести элементы, значение поля name которых содержит заданную подстроку"));
        registerCommand(new ClientSimpleCommand("filter_less_than_hair_color", "вывести элементы, значение поля hairColor которых меньше заданного"));
        registerCommand(new ClientSimpleCommand("execute_script", "считать и исполнить скрипт из указанного файла"));
    }
    
    /**
     * 注册命令
     */
    private void registerCommand(ClientCommand command) {
        commands.put(command.getName(), command);
    }
    
    /**
     * 获取命令
     */
    public ClientCommand getCommand(String name) {
        return commands.get(name);
    }
    
    /**
     * 执行命令
     */
    public Request executeCommand(String name, String[] args) {
        ClientCommand command = getCommand(name);
        if (command == null) {
            System.out.println("Неизвестная команда: " + name);
            return null;
        }
        return command.execute(args);
    }
    
    /**
     * 检查命令是否存在
     */
    public boolean hasCommand(String name) {
        return commands.containsKey(name);
    }
    
    /**
     * 获取所有命令
     */
    public Map<String, ClientCommand> getCommands() {
        return new HashMap<>(commands);
    }
} 