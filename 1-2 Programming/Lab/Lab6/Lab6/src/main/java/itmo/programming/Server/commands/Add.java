package itmo.programming.Server.commands;

import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Common.utility.OperationSuccessful;
import itmo.programming.Common.utility.createperson.PersonFactory;
import itmo.programming.Server.manager.CollectionManager;

import java.util.ArrayList;

/**
 * 添加元素命令类
 */
public class Add extends Command {
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
    public Add(CollectionManager collectionManager, PersonFactory personFactory) {
        super("add", "добавить новый элемент", CommandsType.UN_SIMPLE);
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
        
        // 在脚本模式下使用工厂创建Person
        final Person person = personFactory.createPerson(args, mode);
        
        // 调用内部方法添加Person
        return addPersonToCollection(person);
    }
    
    /**
     * 执行命令（Person对象版本 - 用于网络模式）
     */
    @Override
    public Response executeWithPerson(Person person, CommandMode mode) {
        // 直接使用传入的Person对象
        return addPersonToCollection(person);
    }
    
    /**
     * 添加Person到集合的内部方法
     */
    private Response addPersonToCollection(Person person) {
        final boolean success = collectionManager.add(person);
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
        return 10;
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 0) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда не имеет параметров."
            );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        if (args.length != getFollowUpLines()) {
            throw new ArgumentException("Неправильное количество аргументов! Эта команда не имеет параметров.");
        }
    }
}
