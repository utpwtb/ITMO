public static class ConsoleUtils
{
    public static void Logger(string log, ConsoleColor color)
    {
        Console.ForegroundColor = color;
        Console.WriteLine(log);
        Console.ResetColor();
    }

    public static void Beep()
    {
        Console.Beep();
    }
}