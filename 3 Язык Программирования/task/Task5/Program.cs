using System.Diagnostics;

class Program
{
    static async Task Main()
    {
        var stopwatch = Stopwatch.StartNew();

        Console.WriteLine($"Главный поток: {Environment.CurrentManagedThreadId}");

        string file1 = "C:\\develop\\NOTE_UTP\\StudyNote\\3 Язык Программирования\\task\\Task5\\file\\file1.txt";
        string file2 = "C:\\develop\\NOTE_UTP\\StudyNote\\3 Язык Программирования\\task\\Task5\\file\\file2.txt";
        string file3 = "C:\\develop\\NOTE_UTP\\StudyNote\\3 Язык Программирования\\task\\Task5\\file\\file3.txt";

        var task1 = CountWordsAsync(file1);
        var task2 = CountWordsAsync(file2);
        var task3 = CountWordsAsync(file3);

        await Task.WhenAll(task1, task2, task3);

        stopwatch.Stop();
        Console.WriteLine($"\nОбщее время выполнения: {stopwatch.ElapsedMilliseconds} мс");
    }

    static async Task CountWordsAsync(string filePath)
    {
        var sw = Stopwatch.StartNew();

        Console.WriteLine($"Начало обработки файла: {filePath}");
        string text = await File.ReadAllTextAsync(filePath);
        int wordCount = text.Split([' ', '\n', '\r', '\t'], StringSplitOptions.RemoveEmptyEntries).Length;

        sw.Stop();
        Console.WriteLine($"Файл: {Path.GetFileName(filePath)}, слов: {wordCount}, поток: {Environment.CurrentManagedThreadId}, время: {sw.ElapsedMilliseconds} мс");
    }
}
