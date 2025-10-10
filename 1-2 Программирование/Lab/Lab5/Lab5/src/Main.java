import Exceptions.NotInitializationException;
import Manager.CollectionManager;
import Manager.DocumentManager;
import org.xml.sax.SAXException;
import utlity.CommandUtils;
import utlity.Runner;

import javax.xml.parsers.ParserConfigurationException;
import java.io.File;
import java.io.IOException;


public class Main {
    public static void main(String[] args) throws ParserConfigurationException, IOException, SAXException {
        String filePath = System.getenv("MY_FILE_PATH");
        if (filePath == null) {
            System.err.println("Ошибка: переменная среды MY_FILE_PATH не задана");
            System.exit(1);
        }

        File file = new File(filePath);
        if (!file.exists()) {
            System.err.println("Ошибка: Файл " + filePath + " не существует");
            System.exit(1);
        }

        CommandUtils.commandInitialization();
        CollectionManager collectionManager = CollectionManager.getInstance();
        collectionManager.doInitialization();

        DocumentManager instance = DocumentManager.getInstance();
        instance.read(filePath);

        try {
            while (true){
                Runner.runCommand();
            }
        }catch (NotInitializationException e){
            System.out.println(e.getMessage());
        }


    }
}
