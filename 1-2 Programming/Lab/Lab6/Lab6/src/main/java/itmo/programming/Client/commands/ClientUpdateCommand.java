package itmo.programming.Client.commands;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.exceptions.ArgumentException;
import itmo.programming.Common.person.Person;
import itmo.programming.Common.utility.createperson.PersonFactory;

/**
 * 客户端Update命令实现
 */
public class ClientUpdateCommand extends AbstractClientCommand {
    private final PersonFactory personFactory;
    
    public ClientUpdateCommand(PersonFactory personFactory) {
        super("update", "обновить значение элемента коллекции, id которого равен заданному");
        this.personFactory = personFactory;
    }
    
    @Override
    protected void validateArgs(String[] args) throws ArgumentException {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов! Эта команда требует один аргумент - ID элемента."
            );
        }
        
        try {
            Long.parseLong(args[0]);
        } catch (NumberFormatException e) {
            throw new ArgumentException("ID должен быть числом");
        }
    }
    
    @Override
    public Request execute(String[] args) {
        try {
            // 验证参数
            validateArgs(args);
            
            // 解析ID
            long id = Long.parseLong(args[0]);
            
            // 使用PersonFactory从控制台创建带ID的Person对象
            System.out.println("Введите новую информацию для человека id: " + id);
            Person person = personFactory.createFromConsoleWithId(id);
            
            if (person == null) {
                System.out.println("Обновление элемента отменено");
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