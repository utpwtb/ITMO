package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Common.utility.OperationSuccessful;
import itmo.programming.Common.utility.createperson.PersonFactory;
import itmo.programming.Server.manager.CollectionManager;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * 插入元素命令类
 */
public class Insert extends Command implements ValidateArgs {
    /**
     * 集合管理器
     */
    private final CollectionManager collectionManager;

    /**
     * Person对象工厂（用于脚本模式）
     */
    private final PersonFactory personFactory;

    /**
     * 构造函数
     */
    public Insert(CollectionManager collectionManager, PersonFactory personFactory) {
        super("insert", "добавить новый элемент с заданным ключом", CommandsType.UN_SIMPLE);
        this.collectionManager = collectionManager;
        this.personFactory = personFactory;
    }

    /**
     * 执行命令（字符串参数版本 - 向后兼容）
     */
    @Override
    public Response execute(String[] args, CommandMode mode) {
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            validateConsoleArgs(args);
        } else {
            validateScriptArgs(args);
        }
        
        final long key = Long.parseLong(args[0]);

        if (collectionManager.containsKey(key)) {
            throw new ArgumentException("Указанный идентификатор уже существует");
        }

        // 在控制台或脚本模式下使用工厂创建Person
        final Person person;
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            person = personFactory.createFromConsole();
        } else {
            person = personFactory.createFromScript(Arrays.copyOfRange(args, 1, args.length));
        }
        
        // 调用内部方法插入Person
        return insertPersonToCollection(key, person);
    }
    
    /**
     * 执行命令（带键和Person对象版本 - 用于网络模式）
     */
    @Override
    public Response executeWithPersonAndKey(Long key, Person person, CommandMode mode) {
        if (collectionManager.containsKey(key)) {
            return new Response("Указанный идентификатор уже существует", null);
        }
        
        return insertPersonToCollection(key, person);
    }
    
    /**
     * 执行命令（对象参数版本 - 用于处理网络请求）
     */
    @Override
    public Response executeWithObject(Object[] args, CommandMode mode) {
        if (args.length != 2 || !(args[0] instanceof Long) || !(args[1] instanceof Person)) {
            return new Response("Неверные аргументы для команды insert", null);
        }
        
        Long key = (Long) args[0];
        Person person = (Person) args[1];
        
        return executeWithPersonAndKey(key, person, mode);
    }
    
    /**
     * 插入Person到集合的内部方法
     */
    private Response insertPersonToCollection(long key, Person person) {
        final boolean success = collectionManager.insert(key, person);
        ArrayList<String> judge = OperationSuccessful.judge(person, success);
        Response response = new Response();
        response.setMessage(judge.get(0));
        response.setCollectionToStr(judge.get(1));
        return response;
    }

    /**
     * 获取脚本模式下需要的行数
     */
    @Override
    public int getFollowUpLines() {
        return 11;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда требует один аргумент - ключ."
            );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        if (args.length != getFollowUpLines()) {
            throw new ArgumentException("Неправильное количество аргументов!");
        }
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("Параметр должен быть числом");
        }
    }
}
