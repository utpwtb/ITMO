package itmo.programming.Common.utility;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.NetWork.Response;
import itmo.programming.Common.person.Person;
import itmo.programming.Server.commands.Command;
import itmo.programming.Server.commands.CommandMode;
import itmo.programming.Server.commands.CommandsType;
import itmo.programming.Server.manager.CommandManager;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 命令执行器
 */
public class Runner {
    private final CommandManager commandManager;
    private static final Logger logger = Logger.getLogger(Runner.class.getName());
    
    public Runner(CommandManager commandManager) {
        this.commandManager = commandManager;
    }
    
    /**
     * 执行命令
     * @param request 请求对象
     * @return 响应对象
     */
    public Response runCommand(Request request) {
        if (request == null) {
            logger.warning("Получен null запрос");
            return new Response("Ошибка: запрос отсутствует", null);
        }
        
        String commandName = request.getCommandName();
        Command command = commandManager.getCommands().get(commandName);
        
        if (command == null) {
            logger.warning("Неизвестная команда: " + commandName);
            return new Response("Неизвестная команда: " + commandName, null);
        }
        
        try {
            logger.info("Выполнение команды: " + commandName);
            
            // 根据命令类型执行不同的处理逻辑
            if (command.getType().equals(CommandsType.SIMPLE)) {
                // 简单命令使用字符串参数执行
                logger.info("Выполняется простая команда: " + commandName);
                return command.execute(request.getStringArgs(), CommandMode.CONSOLE_MODE);
            } else {
                // 复杂命令根据特定模式执行
                return executeComplexCommand(command, request);
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Ошибка при выполнении команды: " + e.getMessage(), e);
            e.printStackTrace();
            return new Response("Ошибка при выполнении команды: " + e.getMessage(), null);
        }
    }
    
    /**
     * 执行复杂命令
     */
    private Response executeComplexCommand(Command command, Request request) throws IOException {
        String commandName = request.getCommandName();
        
        // 检查是否有Person对象
        if (request.hasPersonArg()) {
            Person person = request.getPersonArg();
            
            // 处理特殊的insert命令（需要key和Person）
            if (commandName.equals("insert")) {
                Long key = request.getLongArg();
                if (key == null) {
                    logger.warning("Не указан ключ для команды insert");
                    return new Response("Не указан ключ для команды insert", null);
                }
                
                logger.info("Выполняется команда insert с Person объектом и ключом " + key);
                return command.executeWithPersonAndKey(key, person, CommandMode.CONSOLE_MODE);
            }
            
            // 处理其他带Person对象的命令
            logger.info("Выполняется команда " + commandName + " с Person объектом");
            return command.executeWithPerson(person, CommandMode.CONSOLE_MODE);
        } 
        // 处理带对象数组的命令
        else if (request.getArgs().length > 0 && !(request.getArgs()[0] instanceof String)) {
            logger.info("Выполняется команда " + commandName + " с объектными аргументами");
            return command.executeWithObject(request.getArgs(), CommandMode.CONSOLE_MODE);
        } 
        // 处理带字符串参数的复杂命令
        else {
            logger.info("Выполняется сложная команда " + commandName + " со строковыми аргументами");
            return command.execute(request.getStringArgs(), CommandMode.CONSOLE_MODE);
        }
    }
}
