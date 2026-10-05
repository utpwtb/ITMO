package itmo.programming.Client.commands;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Common.utility.createperson.PersonFactory;

/**
 * 客户端Insert命令实现
 */
public class ClientInsertCommand extends AbstractClientCommand {
    private final PersonFactory personFactory;
    
    public ClientInsertCommand(PersonFactory personFactory) {
        super("insert", "добавить новый элемент с заданным ключом");
        this.personFactory = personFactory;
    }
    
    @Override
    protected void validateArgs(String[] args) throws ArgumentException {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда требует один аргумент - ключ."
            );
        }
        
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("Ключ должен быть числом");
        }
    }
    
    @Override
    public Request execute(String[] args) {
        try {
            // 验证参数
            validateArgs(args);
            
            // 解析键
            long key = Long.parseLong(args[0]);
            
            // 使用PersonFactory从控制台创建Person对象
            System.out.println("Создание нового элемента с ключом " + key + ":");
            Person person = personFactory.createFromConsole();
            
            if (person == null) {
                System.out.println("Создание элемента отменено");
                return null;
            }
            
            // 创建请求，包含命令名、键和Person对象
            return new Request(getName(), new Object[]{key, person});
            
        } catch (ArgumentException e) {
            System.out.println(e.getMessage());
            return null;
        }
    }
} 