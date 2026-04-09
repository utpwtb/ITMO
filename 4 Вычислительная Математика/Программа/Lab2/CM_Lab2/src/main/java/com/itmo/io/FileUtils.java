package com.itmo.io;

import java.io.*;
import java.nio.charset.StandardCharsets;

public final class FileUtils {
    private FileUtils() {}

    public static String[] readData(File file, int count) throws IOException {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
            String[] data = new String[count];
            String line;
            int lineNum = 0;
            while ((line = reader.readLine()) != null && lineNum < count) {
                line = line.trim();
                if (!line.isEmpty()) {
                    data[lineNum++] = line;
                }
            }
            return data;
        }
    }

    public static void writeContent(File file, String content) throws IOException {
        try (PrintWriter writer = new PrintWriter(
                new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8))) {
            writer.print(content);
        }
    }
}