using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace InteropPoints
{
    [StructLayout(LayoutKind.Sequential)]
    public struct Point
    {
        public int X;
        public int Y;

        public override string ToString() => $"({X}, {Y})";
    }

    [UnmanagedFunctionPointerAttribute(CallingConvention.Cdecl)]
    public delegate bool FilterDelegate(Point p);

    public static class PointFileReader
    {
        public static Point[] ReadPoints(string path)
        {
            var list = new List<Point>();

            foreach (var line in File.ReadLines(path))
            {
                var tokens = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);

                foreach (var token in tokens)
                {
                    var coords = token.Split(',', StringSplitOptions.RemoveEmptyEntries);
                    if (coords.Length != 2)
                        continue;

                    if (int.TryParse(coords[0], out int x) &&
                        int.TryParse(coords[1], out int y))
                    {
                        list.Add(new Point { X = x, Y = y });
                    }
                }
            }

            return list.ToArray();
        }
    }

    public static class PointFileGenerator
    {
        public static void CreatePointFile(string filename, int numPairs)
        {
            Random random = new Random();

            using (StreamWriter writer = new StreamWriter(filename))
            {
                for (int i = 0; i < numPairs; i++)
                {
                    int x1 = random.Next(-100, 101);
                    int y1 = random.Next(-100, 101);

                    int x2 = random.Next(-100, 101);
                    int y2 = random.Next(-100, 101);

                    writer.WriteLine($"{x1},{y1} {x2},{y2}");
                }
            }
        }
    }

    class Program
    {
        [DllImport("native_points.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int filter([In] Point[] src, int count,[Out] Point[] dst , FilterDelegate filter);
        static bool IsInQuadrant1(Point p) => (p.X > 0 && p.Y > 0);

        static bool IsInQuadrant2(Point p) => (p.X < 0 && p.Y > 0) ;

        static bool IsInQuadrant3(Point p) => (p.X < 0 && p.Y < 0) ;

        static bool IsInQuadrant4(Point p) => (p.X > 0 && p.Y < 0);

        static void Main(string[] args)
        {
            PointFileGenerator.CreatePointFile("points.txt", 500);

            string path = "C:\\develop\\NOTE_UTP\\StudyNote\\3 Язык Программирования\\task\\Task7\\points.txt";

            if (!File.Exists(path))
            {
                Console.WriteLine($"Файл не найден: {path}");
                return;
            }

            Point[] allPoints = PointFileReader.ReadPoints(path);
            Console.WriteLine($"Всего точек: {allPoints.Length}");

            Point[] buffer = new Point[allPoints.Length];

            PrintQuadrant("Первый квадрант", allPoints, buffer, IsInQuadrant1);
            PrintQuadrant("Второй квадрант", allPoints, buffer, IsInQuadrant2);
            PrintQuadrant("Третий квадрант", allPoints, buffer, IsInQuadrant3);
            PrintQuadrant("Четвертый квадрант", allPoints, buffer, IsInQuadrant4);

        }

        static void PrintQuadrant(string name, Point[] allPoints, Point[] buffer, FilterDelegate predicate)
        {
            int count = filter(allPoints, allPoints.Length, buffer, predicate);

            Console.WriteLine($"{name}: {count} точек:");

            for (int i = 0; i < count; i++)
            {
                Console.WriteLine($"  {buffer[i]}");
            }

            Console.WriteLine();
        }
    }
}