package itmo.programming.Common.utility;

import itmo.programming.Common.person.Person;

import java.util.ArrayList;


/**
 * Определить, была ли операция успешной.
 */
public class OperationSuccessful {
    /**
     * Определить, была ли операция успешной.
     *
     * @param person человек
     */
    public static ArrayList<String> judge(Person person, Boolean flag) {
        ArrayList<String> list = new ArrayList<>();
        if (person != null && flag) {
            list.add("Операция успешна");
            list.add(person.toString());
        } else {
            list.add("Операция неудачна");
            list.add("");
        }
        return list;
    }
}
