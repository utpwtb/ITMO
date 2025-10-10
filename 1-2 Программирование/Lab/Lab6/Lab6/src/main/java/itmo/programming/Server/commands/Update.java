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
 * 更新元素命令类
 */
public class Update extends Command implements ValidateArgs {
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
    public Update(CollectionManager collectionManager, PersonFactory personFactory) {
        super("update", "обновить значение элемента коллекции, id которого равен заданному", CommandsType.UN_SIMPLE);
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

        final long id = Long.parseLong(args[0]);

        if (collectionManager.containsId(id).isEmpty()) {
            throw new ArgumentException("Указанный идентификатор не существует");
        }

        // 在脚本模式下使用工厂创建Person
        final Person person;
        if (mode.equals(CommandMode.CONSOLE_MODE)) {
            System.out.println("Введите новую информацию для человека id: " + id);
            person = personFactory.createFromConsoleWithId(id);
        } else {
            person = personFactory.createFromScriptWithId(Arrays.copyOfRange(args, 1, args.length), id);
        }
        
        // 调用内部方法更新Person
        return updatePersonInCollection(id, person);
    }
    
    /**
     * 执行命令（Person对象版本 - 用于网络模式）
     */
    @Override
    public Response executeWithPerson(Person person, CommandMode mode) {
        // 直接使用传入的Person对象，从其ID获取更新的ID
        long id = person.getId();
        
        if (collectionManager.containsId(id).isEmpty()) {
            return new Response("Указанный идентификатор не существует", null);
        }
        
        return updatePersonInCollection(id, person);
    }
    
    /**
     * 更新集合中Person的内部方法
     */
    private Response updatePersonInCollection(long id, Person person) {
        final boolean success = collectionManager.update(id, person);
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
                    "Неправильное количество аргументов! Эта команда требует один аргумент - ID элемента."
            );
        }
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("Параметр должен быть числом");
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
