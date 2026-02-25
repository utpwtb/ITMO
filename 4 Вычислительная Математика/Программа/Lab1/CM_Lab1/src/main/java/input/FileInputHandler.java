package input;

import model.MatrixData;

import java.io.*;
import java.util.Scanner;

public class FileInputHandler {
    private final Scanner sc;
    private static final int MAX_DIMENSION = 20;

    public FileInputHandler(Scanner sc) {
        this.sc = sc;
    }

    public MatrixData readMatrix() {
        String filename = readFilename();

        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            Integer n = readDimension(br);
            if (n == null) return retryOrExit();

            Double[][] coefficients = readCoefficients(br, n);
            if (coefficients == null) return retryOrExit();

            Double[] constants = readConstants(br, n);
            if (constants == null) return retryOrExit();

            System.out.println("\nФайл успешно прочитан. Размерность матрицы: " + n);

            return new MatrixData(n, coefficients, constants);

        } catch (FileNotFoundException e) {
            System.out.println("\nФайл не найден: " + filename);
            return retryOrExit();
        } catch (IOException e) {
            System.out.println("\nОшибка при чтении файла: " + e.getMessage());
            return retryOrExit();
        }
    }

    private String readFilename() {
        System.out.println("\nПожалуйста, введите имя файла: ");
        return sc.nextLine();
    }

    private Integer readDimension(BufferedReader br) throws IOException {
        String line = br.readLine();
        if (line == null) {
            System.out.println("\nФайл пуст.");
            return null;
        }

        try {
            int n = Integer.parseInt(line.trim().replace(",", "."));

            if (n <= 0) {
                System.out.println("\nРазмерность матрицы должна быть положительным числом.");
                return null;
            }

            if (n > MAX_DIMENSION) {
                System.out.println("\nПредупреждение: Размерность матрицы в файле (" + n +
                        ") превышает максимально допустимую " + MAX_DIMENSION);
                return null;
            }

            return n;

        } catch (NumberFormatException e) {
            System.out.println("\nНеверный формат размерности матрицы: " + line);
            return null;
        }
    }

    private Double[][] readCoefficients(BufferedReader br, Integer n) throws IOException {
        Double[][] coefficients = new Double[n][n];

        System.out.println("\nЧтение матрицы коэффициентов A.");

        for (int i = 0; i < n; i++) {
            String line = br.readLine();
            if (line == null) {
                System.out.println("\nНедостаточно строк в файле для матрицы коэффициентов.");
                return null;
            }

            String[] values = line.trim().replace(",", ".").split("\\s+");

            if (values.length < n) {
                System.out.println("\nНеверное количество параметров.");
                return null;
            }

            for (int j = 0; j < n; j++) {
                try {
                    coefficients[i][j] = Double.parseDouble(values[j]);
                } catch (NumberFormatException e) {
                    System.out.println("\nНеверный формат числа в строке " + (i + 1) +
                            ", столбец " + (j + 1) + ": " + values[j]);
                    return null;
                }
            }
        }

        return coefficients;
    }

    private Double[] readConstants(BufferedReader br, Integer n) throws IOException {
        Double[] constants = new Double[n];

        String line = br.readLine();
        if (line == null) {
            System.out.println("\nНедостаточно строк в файле для вектора параметров.");
            return null;
        }

        String[] values = line.trim().replace(",", ".").split("\\s+");

        if (values.length < n) {
            System.out.println("\nВектор параметров содержит только " + values.length +
                    " элементов, ожидалось " + n);
            return null;
        }

        for (int i = 0; i < n; i++) {
            try {
                constants[i] = Double.parseDouble(values[i]);
            } catch (NumberFormatException e) {
                System.out.println("\nНеверный формат числа в векторе параметров, позиция " +
                        (i + 1) + ": " + values[i]);
                return null;
            }
        }

        return constants;
    }

    private MatrixData retryOrExit() {
        while (true) {
            System.out.println("\nХотите попробовать другой файл? (y/n): ");
            String choice = sc.nextLine();

            if (choice.equalsIgnoreCase("y") ||
                    choice.equalsIgnoreCase("yes") ||
                    choice.equalsIgnoreCase("да") ||
                    choice.equalsIgnoreCase("д")) {

                return readMatrix();

            } else if (choice.equalsIgnoreCase("n") ||
                    choice.equalsIgnoreCase("no") ||
                    choice.equalsIgnoreCase("нет") ||
                    choice.equalsIgnoreCase("н")) {

                System.out.println("\nВыход из программы.");
                System.exit(1);

                return null;
            } else {

                System.out.println("\nНеверный ввод.");

            }
        }
    }

}