package itmo.programming.Client.commands;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Common.utility.createperson.PersonFactory;

/**
 * 客户端Add命令实现
 */
public class ClientAddCommand extends AbstractClientCommand {
    private final PersonFactory personFactory;
    
    public ClientAddCommand(PersonFactory personFactory) {
        super("add", "добавить новый элемент");
        this.personFactory = personFactory;
    }
    
    @Override
    protected void validateArgs(String[] args) throws ArgumentException {
        if (args.length != 0) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда не имеет параметров."
            );
        }
    }
    
    @Override
    public Request execute(String[] args) {
        try {
            // 验证参数
            validateArgs(args);
            
            // 使用PersonFactory从控制台创建Person对象
            System.out.println("Создание нового элемента:");
            Person person = personFactory.createFromConsole();
            
            if (person == null) {
                System.out.println("Создание элемента отменено");
                return null;
            }
            
            // 创建请求，包含命令名和Person对象
            return new Request(getName(), new Object[]{person});
            
        } catch (ArgumentException e) {
            System.out.println(e.getMessage());
            return null;
        }
    }
} 