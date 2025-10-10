package utlity;

import person.Person;

import static Manager.CollectionManager.collection;

/**
 * Определить, была ли операция успешной
 */
public class OperationSuccessful {
    /**
     * Определить, была ли операция успешной
     * @param person человек
     */
    public static void judge(Person person){
        if (person != null) {
            System.out.println(person);
            collection.put(person.getId(), person);
            System.out.println("Операция успешна");
        } else {
            System.out.println("Операция неудачна");
        }
    }

}
