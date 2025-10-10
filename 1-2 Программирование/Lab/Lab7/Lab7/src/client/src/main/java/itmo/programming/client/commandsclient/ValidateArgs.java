package itmo.programming.client.commandsclient;

/**
 * Валидация аргументов.
 */
public interface ValidateArgs {
    /**
     * Валидация аргументов в консольном режиме.
     *
     * @param args аргументы команды
     */
    void validateConsoleArgs(String[] args);

    /**
     * Валидация аргументов в режиме скрипта.
     *
     * @param args аргументы команды
     */
    void validateScriptArgs(String[] args);
}
