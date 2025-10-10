package itmo.programming.server.utility;

import com.fasterxml.jackson.core.JsonProcessingException;
import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.exceptions.NoSuchCommandException;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import itmo.programming.common.person.Person;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.PersonParse;
import itmo.programming.server.commands.Command;
import itmo.programming.server.manager.CommandManager;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.NoSuchElementException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Класс для выполнения команд в серверной части приложения.
 */
public class Runner {

    /**
     * Логгер для записи информации о выполнении команд.
     */
    private static final Logger logger = Logger.getLogger(Runner.class.getName());

    /**
     * Менеджер команд для доступа к зарегистрированным командам.
     */
    private final CommandManager commandManager;

    /**
     * Конструктор класса Runner.
     *
     * @param commandManager менеджер команд
     */
    public Runner(CommandManager commandManager) {
        this.commandManager = commandManager;
    }

    /**
     * Выполняет команду на основе полученного запроса.
     *
     * @param request запрос, содержащий команду и аргументы
     * @return ответ на выполненную команду или null в случае ошибки
     */
    public Response runCommand(Request request) {
        try {
            final String command = request.getCommandStr();
            logger.info("Выполнение команды: " + command);
            
            final Command command1 = commandManager.getCommands().get(command);
            if (command1 == null) {
                throw new NoSuchCommandException("Команда '" + command + "' не найдена.");
            }
            
            try {
                // 根据请求是否包含Person对象来构建参数
                final String[] argsToUse = prepareArgsForCommand(request);
                return command1.execute(argsToUse, CommandMode.CONSOLE_MODE);
            } catch (FileNotFoundException e) {
                logger.log(Level.WARNING, "Файл не существует: " + e.getMessage(), e);
                final Response response = new Response();
                response.setMessage("Ошибка: файл не существует.");
                return response;
            } catch (NumberFormatException e) {
                logger.log(Level.WARNING, "Параметр должен быть числом: " + e.getMessage(), e);
                final Response response = new Response();
                response.setMessage("Ошибка: параметр должен быть числом.");
                return response;
            } catch (ArgumentException e) {
                logger.log(Level.WARNING, "Ошибка в аргументах: " + e.getMessage(), e);
                return e.getResponse();
            } catch (IOException e) {
                logger.log(Level.SEVERE, "Ошибка ввода-вывода: " + e.getMessage(), e);
                throw new RuntimeException("Ошибка при выполнении команды: " + e.getMessage(), e);
            }
        } catch (NoSuchElementException e) {
            logger.log(Level.SEVERE, "Критическая ошибка: " + e.getMessage(), e);
            System.exit(0);
        } catch (NoSuchCommandException e) {
            logger.log(Level.WARNING, "Команда не найдена: " + e.getMessage(), e);
            return e.getResponse();
        }
        return null;
    }
    
    /**
     * Подготавливает параметры для выполнения команды,
     * обрабатывает специальные случаи, содержащие объект Person.
     *
     * @param request объект запроса
     * @return обработанный массив параметров
     * @throws JsonProcessingException если сериализация объекта Person не удалась
     */
    private String[] prepareArgsForCommand(Request request) throws JsonProcessingException {
        final String[] originalArgs = request.getCommandArgs();
        
        if (request.hasPerson()) {
            logger.info("Запрос содержит объект Person, готовим специальную обработку параметров");
            
            final ArrayList<String> argsList = new ArrayList<>(Arrays.asList(originalArgs));
            
            while (argsList.size() < 2) {
                argsList.add("");
            }
            
            final Person person = request.getPerson();
            argsList.set(1, PersonParse.personToStr(person));
            
            logger.info("Параметры подготовлены, количество новых параметров: " + argsList.size());
            return argsList.toArray(new String[0]);
        } else {
            logger.info("Запрос не содержит объекта Person, используем исходные параметры");
            return originalArgs;
        }
    }
}
