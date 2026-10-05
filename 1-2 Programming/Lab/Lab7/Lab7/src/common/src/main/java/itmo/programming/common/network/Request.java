package itmo.programming.common.network;

import itmo.programming.common.person.Person;
import java.io.Serial;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Класс запроса, который отправляется от клиента к серверу.
 * Содержит информацию о команде, её аргументах и объекте Person (если требуется).
 */
public class Request implements Serializable {

    @Serial
    private static final long serialVersionUID = -7043984903067118728L;

    /**
     * Строка команды.
     */
    private String commandStr;

    /**
     * Список аргументов команды.
     * Содержит только параметры команды, не включая объект Person.
     */
    private List<String> commandArgs;

    /**
     * Объект Person, который требуется изменить или использовать в команде.
     * Может быть null, если команда не требует操作 с Person.
     */
    private Person person;

    /**
     * Конструктор для создания запроса без Person объекта.
     *
     * @param commandStr  строка команды
     * @param commandArgs аргументы команды
     */
    public Request(String commandStr, String[] commandArgs) {
        this.commandStr = commandStr;
        this.commandArgs = commandArgs != null
                ?
                new ArrayList<>(Arrays.asList(commandArgs)) : new ArrayList<>();
        this.person = null;
    }

    /**
     * Конструктор для создания запроса с Person объектом.
     *
     * @param commandStr  строка команды
     * @param commandArgs аргументы команды
     * @param person      объект Person для操作
     */
    public Request(String commandStr, String[] commandArgs, Person person) {
        this.commandStr = commandStr;
        this.commandArgs = commandArgs != null
                ?
                new ArrayList<>(Arrays.asList(commandArgs)) : new ArrayList<>();
        this.person = person;
    }

    /**
     * Получить строку команды.
     *
     * @return строка команды
     */
    public String getCommandStr() {
        return commandStr;
    }

    /**
     * Получить аргументы команды.
     *
     * @return неизменяемый список аргументов команды
     */
    public List<String> getCommandArgsList() {
        return Collections.unmodifiableList(commandArgs);
    }

    /**
     * Получить аргументы команды в виде массива (для совместимости со старыми методами).
     *
     * @return массив аргументов команды
     */
    public String[] getCommandArgs() {
        return commandArgs.toArray(new String[0]);
    }

    /**
     * Получить объект Person, связанный с запросом.
     *
     * @return объект Person или null, если запрос не связан с Person
     */
    public Person getPerson() {
        return person;
    }

    /**
     * Проверить, есть ли у команды аргументы.
     *
     * @return true, если у команды есть аргументы, иначе false
     */
    public boolean hasArguments() {
        return !commandArgs.isEmpty();
    }

    /**
     * Проверить, содержит ли запрос объект Person.
     *
     * @return true, если запрос содержит объект Person, иначе false
     */
    public boolean hasPerson() {
        return person != null;
    }

    /**
     * Преобразовать объект в строку.
     *
     * @return строковое представление объекта
     */
    @Override
    public String toString() {
        return "Request{command = " + commandStr
                + ", commandArgs = " + commandArgs
                + ", hasPerson = " + (person != null)
                + "}";
    }
}
