package itmo.programming.Client.commands;

import itmo.programming.Common.NetWork.Request;
import itmo.programming.Common.exceptions.ArgumentException;

/**
 * 客户端简单命令实现（不需要交互式输入的命令）
 */
public class ClientSimpleCommand extends AbstractClientCommand {
    
    public ClientSimpleCommand(String name, String description) {
        super(name, description);
    }
    
    @Override
    protected void validateArgs(String[] args) throws ArgumentException {
        // 简单命令不需要验证参数，由服务端验证
    }
    
    @Override
    public Request execute(String[] args) {
        // 直接创建请求对象
        return new Request(getName(), args);
    }
} 