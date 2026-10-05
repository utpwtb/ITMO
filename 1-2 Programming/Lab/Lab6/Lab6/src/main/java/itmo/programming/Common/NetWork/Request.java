package itmo.programming.Common.NetWork;

import java.io.Serial;
import java.io.Serializable;
import java.util.Arrays;
import itmo.programming.Common.person.Person;

/**
 * 请求对象，用于客户端和服务端之间的通信
 */
public class Request implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;
    private final String commandName;
    private final Object[] args;

    /**
     * 创建包含Object参数的请求
     */
    public Request(String commandName, Object[] args) {
        this.commandName = commandName;
        this.args = args != null ? args : new Object[0];
    }

    /**
     * 创建包含String参数的请求（向后兼容）
     */
    public Request(String commandName, String[] args) {
        this.commandName = commandName;
        if (args != null) {
            this.args = new Object[args.length];
            System.arraycopy(args, 0, this.args, 0, args.length);
        } else {
            this.args = new Object[0];
        }
    }

    /**
     * 获取命令名称
     */
    public String getCommandName() {
        return commandName;
    }

    /**
     * 获取所有参数
     */
    public Object[] getArgs() {
        return args;
    }

    /**
     * 获取Person对象（如果存在）
     */
    public Person getPersonArg() {
        for (Object arg : args) {
            if (arg instanceof Person) {
                return (Person) arg;
            }
        }
        return null;
    }

    /**
     * 检查是否包含Person对象
     */
    public boolean hasPersonArg() {
        return getPersonArg() != null;
    }

    /**
     * 获取字符串参数数组（向后兼容）
     */
    public String[] getStringArgs() {
        String[] result = new String[args.length];
        for (int i = 0; i < args.length; i++) {
            if (args[i] != null && !(args[i] instanceof Person)) {
                result[i] = args[i].toString();
            }
        }
        return result;
    }

    /**
     * 获取Long参数（如果存在）
     */
    public Long getLongArg() {
        for (Object arg : args) {
            if (arg instanceof Long) {
                return (Long) arg;
            } else if (arg instanceof String) {
                try {
                    return Long.parseLong((String) arg);
                } catch (NumberFormatException e) {
                    return null;
                }
            }
        }
        return null;
    }

    @Override
    public String toString() {
        return "Request{commandName='" + commandName + "', args=" + Arrays.toString(args) + "}";
    }
}
