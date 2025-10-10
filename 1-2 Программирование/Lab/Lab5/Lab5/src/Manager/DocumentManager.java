package Manager;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;
import person.*;
import Exceptions.FieldException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Класс файлового менеджера
 */
public class DocumentManager {

    /**
     * Экземпляр класса файлового менеджера
     */
    private static DocumentManager instance;

    /**
     * Конструктор
     */
    private DocumentManager(){}

    /**
     * Получить экземпляр
     * @return экземпляр
     */
    public static  DocumentManager getInstance() {
        if (instance == null) {
            instance = new DocumentManager();
        }
        return instance;
    }

    /**
     * Создать файл
     * @param map Коллекция сохраненных элементов
     * @return файл
     * @throws Exception Exception
     */
    private Document createDocument(LinkedHashMap<Long, Person> map) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.newDocument();

        Element root = doc.createElement("Persons");
        doc.appendChild(root);

        for (Map.Entry<Long, Person> entry : map.entrySet()) {
            Person person = entry.getValue();

            Element personElement = doc.createElement("Person");
            personElement.setAttribute("id", String.valueOf(person.getId()));
            root.appendChild(personElement);

            addChild(doc, personElement, "name", person.getName());
            addChild(doc, personElement, "coordinates", person.getCoordinates().toString());
            addChild(doc, personElement, "creationDate", person.getCreationDate().toString());
            addChild(doc, personElement, "height", String.valueOf(person.getHeight()));
            addChild(doc, personElement, "birthday", person.getBirthday().toString());
            addChild(doc, personElement, "eyeColor", person.getEyeColor().toString());
            addChild(doc, personElement, "hairColor", person.getHairColor().toString());
            addChild(doc, personElement, "location", person.getLocation().toString());
        }

        return doc;
    }


    private void addChild(Document doc, Element parent, String tagName, String text) {
        Element child = doc.createElement(tagName);
        child.setTextContent(text);
        parent.appendChild(child);
    }

    /**
     * Запись в файл
     * @param map Коллекция сохраненных элементов
     * @param path Путь к файлу
     * @throws Exception Exception
     */
    public void write(LinkedHashMap<Long, Person> map, String path) throws Exception {
        try (BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(path))) {
            Document doc = createDocument(map);

            TransformerFactory transformerFactory = TransformerFactory.newInstance();
            Transformer transformer = transformerFactory.newTransformer();
            transformer.setOutputProperty(OutputKeys.INDENT, "yes");

            DOMSource source = new DOMSource(doc);
            StreamResult result = new StreamResult(bos);
            transformer.transform(source, result);
        }
    }

    /**
     * Чтение файла
     * @param filePath Путь к файлу
     * @return Коллекция сохраненных элементов
     * @throws ParserConfigurationException ParserConfigurationException
     * @throws IOException IOException
     * @throws SAXException SAXException
     */
    public LinkedHashMap<Long, Person> read(String filePath) throws ParserConfigurationException, IOException, SAXException {
        LinkedHashMap<Long, Person> collection = CollectionManager.getInstance().getCollection();

        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new File(filePath));

        Element root = doc.getDocumentElement();
        NodeList personNodes = root.getElementsByTagName("Person");

        for (int i = 0; i < personNodes.getLength(); i++) {
            Element personElement = (Element) personNodes.item(i);

            try {
                long id = Long.parseLong(personElement.getAttribute("id"));
                String name = getElementText(personElement, "name");
                Coordinates coordinates = parseCoordinates(getElementText(personElement, "coordinates"));
                Date creationDate = parseDate(getElementText(personElement, "creationDate"));
                long height = Integer.parseInt(getElementText(personElement, "height"));
                LocalDateTime birthday = parseLocalDateTime(getElementText(personElement, "birthday"));
                EyeColor eyeColor = EyeColor.valueOf(getElementText(personElement, "eyeColor"));
                HairColor hairColor = HairColor.valueOf(getElementText(personElement, "hairColor"));
                Location location = parseLocation(getElementText(personElement, "location"));

                Person person = Person.fromXml(id, name, coordinates, creationDate, height, 
                                             birthday, eyeColor, hairColor, location);
                collection.put(id, person);
            } catch (FieldException e) {
                System.out.println("Ошибка при чтении Person: " + e.getMessage());
            }
        }
        return collection;
    }

    /**
     * Получить текст элемента
     * @param parent элемент
     * @param tagName Название тега
     * @return текст элемента
     */
    private String getElementText(Element parent, String tagName) {
        return parent.getElementsByTagName(tagName).item(0).getTextContent();
    }

    /**
     * анализ координат
     * @param text Текст Координаты
     * @return координат
     */
    private Coordinates parseCoordinates(String text) {
        String cleanText = text.replaceAll("[{} ]", "");
        String[] parts = cleanText.split(",");
        float x = Float.parseFloat(parts[0].split("=")[1]);
        long y = Long.parseLong(parts[1].split("=")[1]);
        return new Coordinates(x, y);
    }

    /**
     * Разбор местоположения
     * @param text Текст местоположения
     * @return местоположения
     */
    private Location parseLocation(String text) {
        String cleanText = text.replaceAll("[{} ]", "");
        String[] parts = cleanText.split(",");
        double x = Double.parseDouble(parts[0].split("=")[1]);
        int y = Integer.parseInt(parts[1].split("=")[1]);
        int z = Integer.parseInt(parts[2].split("=")[1]);
        return new Location(x, y, z);
    }

    /**
     * парсинг локальной даты и времени
     * @param text Текст локальной даты и времени
     * @return Локальная дата и время
     */
    private LocalDateTime parseLocalDateTime(String text) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd['T'HH[:mm[:ss]]");
        try {
            return LocalDateTime.parse(text, formatter);
        } catch (Exception e) {
            throw new IllegalArgumentException("Невозможно проанализировать дату: " + text);

        }
    }

    /**
     *Дата анализа
     * @param text текст Дата
     * @return Дата
     */
    private Date parseDate(String text) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("EEE MMM dd HH:mm:ss VV yyyy", Locale.ENGLISH);
        try {
            text = text.replace("MSK", "Europe/Moscow");
            ZonedDateTime zdt = ZonedDateTime.parse(text, formatter);
            return Date.from(zdt.toInstant());
        } catch (Exception e) {
            throw new IllegalArgumentException("Невозможно проанализировать дату: " + text);
        }
    }
}