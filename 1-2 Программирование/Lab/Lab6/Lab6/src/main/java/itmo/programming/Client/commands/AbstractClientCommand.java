package itmo.programming.Client.commands;

import itmo.programming.Common.exceptions.ArgumentException;

/**
 * 抽象客户端命令类，提供基本实现
 */
public abstract class AbstractClientCommand implements ClientCommand {
    private final String name;
    private final String description;
    
    protected AbstractClientCommand(String name, String description) {
        this.name = name;
        this.description = description;
    }
    
    @Override
    public String getName() {
        return name;
    }
    
    @Override
    public String getDescription() {
        return description;
    }
    
    /**
     * 验证命令参数
     * @param args 命令参数
     * @throws ArgumentException 如果参数无效
     */
    protected abstract void validateArgs(String[] args) throws ArgumentException;
} 