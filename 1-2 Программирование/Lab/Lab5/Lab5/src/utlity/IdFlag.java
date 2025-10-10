package utlity;

import Manager.CollectionManager;

/**
 * Определить, существует ли идентификатор
 */
public class IdFlag {
    /**
     * Определить, существует ли идентификатор
     * @param id идентификатор
     * @return boolean
     */
    public static boolean isIdExists(long id) {
        return CollectionManager.getInstance().getCollection().values().stream()
                .anyMatch(person -> person.getId() == id);
    }
}
