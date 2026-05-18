package input.util;

import java.util.Scanner;
import java.util.function.Function;

public class InputUtil {
    private final Scanner sc;

    public InputUtil(Scanner sc) {
        this.sc = sc;
    }

    public <T> T getInput(String prompt, Function<String, T> parser, String errorMessage) {
        while (true) {
            try {
                System.out.println(prompt);
                String input = sc.nextLine().trim();

                input = input.replace(',', '.');

                return parser.apply(input);
            } catch (Exception e) {
                System.out.println(errorMessage);
            }
        }
    }
}
