package itmo.programming.Client.commands;

import itmo.programming.Common.NetWork.Request;

/**
 * 客户端命令接口
 */
public interface ClientCommand {
    /**
     * 获取命令名称
     */
    String getName();
    
    /**
     * 获取命令描述
     */
    String getDescription();
    
    /**
     * 执行命令，包括参数验证和数据收集
     * @param args 命令参数
     * @return 封装了命令和数据的请求对象
     */
    Request execute(String[] args);
} 