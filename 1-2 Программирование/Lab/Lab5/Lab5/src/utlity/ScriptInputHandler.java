package utlity;

import person.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;

/**
 *Обработчик входных данных скрипта
 */
public class ScriptInputHandler {
    /**
     * Очередь для хранения параметров
     */
    private final Queue<String> inputQueue;

    /**
     * конструктор
     * @param args массив параметров
     */
    public ScriptInputHandler(String[] args) {
        this.inputQueue = new LinkedList<>(Arrays.asList(args));
    }

    /**
     * создать человека через строитель
     * @return человек
     */
    public Person createPersonFromScript() {
        Person.Builder builder = buildFromScript();
        return builder.build();
    }
    /**
     * создать человека через строитель(Использовать указанный идентификатор для обновления)
     * @return человек
     */
    public Person createPersonFromScriptWithId(long id){
        Person.Builder builder = buildFromScript();
        return builder.buildUpdate(id);
    }

    /**
     * получить строителя
     * @return строители
     */
    public Person.Builder buildFromScript() {
        Person.Builder builder = new Person.Builder();
        builder
                .name(inputQueue.poll())
                .coordinates(new Coordinates(Float.parseFloat(inputQueue.poll()), Long.parseLong(inputQueue.poll())))
                .height(Long.parseLong(inputQueue.poll()))
                .birthday(LocalDateTime.parse(inputQueue.poll(), DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm")))
                .eyeColor(Enum.valueOf(EyeColor.class, inputQueue.poll().toUpperCase()))
                .hairColor(Enum.valueOf(HairColor.class, inputQueue.poll().toUpperCase()))
                .location(new Location(Double.parseDouble(inputQueue.poll()), Integer.parseInt(inputQueue.poll()), Integer.parseInt(inputQueue.poll())));
        return builder;
    }
}
