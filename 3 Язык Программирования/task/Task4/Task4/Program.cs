using System.Globalization;
using Microsoft.VisualBasic.FileIO;

class Program
{
    static List<string[]> ReadAllCsvLines(string filePath)
    {
        var result = new List<string[]>();

        using (var parser = new TextFieldParser(filePath))
        {
            parser.TextFieldType = FieldType.Delimited;
            parser.SetDelimiters(",");
            parser.HasFieldsEnclosedInQuotes = true;

            while (!parser.EndOfData)
            {
                string[] fields = parser.ReadFields();
                result.Add(fields);
            }
        }

        return result;
    }

    static void Main()
    {
        var csvData = ReadAllCsvLines("C:\\develop\\NOTE_UTP\\StudyNote\\3 Язык Программирования\\task\\Task4\\Task4\\IMDb movies.csv");

        var movies = csvData.Skip(1)
            .Select(x => new Movie
            {
                ImdbTitleId = x[0],
                Title = x[1],
                OriginalTitle = x[2],
                Year = int.TryParse(x[3], out var year) ? year : null,
                DatePubished = x[4],
                Genre = x[5].Split(",").ToList(),
                Duration = int.TryParse(x[6], out var duration) ? duration : 0,
                Country = x[7],
                Language = x[8],
                Director = x[9],
                Writer = x[10].Split(",").ToList(),
                Composer = x[11],
                Casts = x[12].Split(",").ToList(),
                Description = x[13],
                AvgVote = float.TryParse(x[14], CultureInfo.InvariantCulture, out var avgVote) ? avgVote : 0f,
                Votes = int.TryParse(x[15], out var votes) ? votes : 0,
                Budget = x[16],
                UsaGrossIncome = x[17],
                WorldwideIncome = x[18],
                Metascore = float.TryParse(x[19], CultureInfo.InvariantCulture, out var metascore) ? metascore : 0f,
                ReviewsFromUsers = float.TryParse(x[20], out var reviewsFromUsers) ? reviewsFromUsers : 0f,
                ReviewsFromCritics = float.TryParse(x[21], out var reviewsFromCritics) ? reviewsFromCritics : 0f

            }
        ).ToList();

        // Над списком из Movie 
        // 2. Найти все фильмы режисёра (на выбор, например Nolan) - Where
        // 3. 5 самый высокооценённых фильма выпущенных после 2010 
        // 4. Получить список фильмов (их количество и средний рейтинг) жанра (на выбор, например Drama) 
        // 5. Режисёр у которого больше всего фильмов
        // Не учитывать регистр
        
        //1.
        Console.WriteLine("Найти все фильмы режисёра Nolan:");
        var nolanMovies = movies.Where(x => x.Director.ToLower().Contains("nolan"));
        nolanMovies.ToList().ForEach(x => Console.WriteLine(x.Title));

        //2.
        Console.WriteLine("\n5 самый высокооценённых фильма выпущенных после 2010:");
        var highRatedMovies = movies.Where(x => x.Year > 2010).OrderByDescending(x => x.AvgVote).Take(5);
        highRatedMovies.ToList().ForEach(x => Console.WriteLine(x.Title));

        //3.
        Console.WriteLine("\nПолучить список фильмов (их и средний рейтинг) жанра Drama:");
        var dramaMovies = movies.Where(x => x.Genre.Any(y => y.ToLower().Contains("drama"))).Select(x => new { Movie = x.Title, AverageVote = x.AvgVote });
        Console.WriteLine(dramaMovies.Count());
        //dramaMovies.ToList().ForEach(x => Console.WriteLine($"{x.Movie} - {x.AverageVote}"));

        //4.
        Console.WriteLine("\nРежисёр у которого больше всего фильмов:");
        var allDirectors = movies
            .Where(x => x != null && !string.IsNullOrWhiteSpace(x.Director))
            .SelectMany(x =>
                x.Director
                    .Split(',', StringSplitOptions.RemoveEmptyEntries)
                    .Select(name => name.Trim())
                    .Where(name => !string.IsNullOrEmpty(name))
            );

        var topDirectorGroup = allDirectors
            .GroupBy(name => name, StringComparer.OrdinalIgnoreCase)
            .OrderByDescending(g => g.Count())
            .FirstOrDefault();

        if (topDirectorGroup != null)
        {
            Console.WriteLine($"Режиссёр с наибольшим числом фильмов: {topDirectorGroup.Key} ({topDirectorGroup.Count()} фильмов)");
        }
    }
}