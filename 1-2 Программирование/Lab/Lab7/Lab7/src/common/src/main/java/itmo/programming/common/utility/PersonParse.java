package itmo.programming.common.utility;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import itmo.programming.common.person.Person;

/**
 * Утилитный класс для сериализации и десериализации объектов Person.
 * Использует Jackson для преобразования между объектами Person и строками JSON.
 */
public class PersonParse {
    private static final ObjectMapper mapper;
    
    static {
        mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
    }
    
    /**
     * Преобразует объект Person в строку JSON.
     *
     * @param person объект Person для сериализации
     * @return строка JSON, представляющая объект Person
     * @throws JsonProcessingException при ошибке сериализации
     */
    public static String personToStr(Person person) throws JsonProcessingException {
        return mapper.writeValueAsString(person);
    }

    /**
     * Преобразует строку JSON в объект Person.
     *
     * @param string строка JSON для десериализации
     * @return объект Person, созданный из строки JSON
     * @throws JsonProcessingException при ошибке десериализации
     */
    public static Person strToPerson(String string) throws JsonProcessingException {
        return mapper.readValue(string, Person.class);
    }
}
