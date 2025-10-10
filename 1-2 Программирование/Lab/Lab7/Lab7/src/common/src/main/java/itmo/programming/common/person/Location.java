package itmo.programming.common.person;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import itmo.programming.common.exceptions.FieldException;
import java.io.Serial;
import java.io.Serializable;


/**
 * Класс местоположения.
 */
public class Location implements Serializable {

    @Serial
    private static final long serialVersionUID = -987654321L;

    private Double locationX; // Поле не может быть null
    private Integer locationY; // Поле не может быть null
    private Integer locationZ; // Поле не может быть null

    /**
     * Конструктор.
     */
    public Location() {
    }

    /**
     * Конструктор.
     */
    @JsonCreator
    public Location(
            @JsonProperty("x") double x,
            @JsonProperty("y") int y,
            @JsonProperty("z") int z) {
        this.locationX = x;
        this.locationY = y;
        this.locationZ = z;
    }

    /**
     * Получить x.
     *
     * @return x
     */
    public Double getLocationX() {
        return locationX;
    }

    /**
     * Установить x.
     *
     * @param locationX x
     */
    public void setLocationX(Double locationX) throws FieldException {
        if (locationX == null) {
            throw new FieldException("x не может быть null");
        } else {
            this.locationX = locationX;
        }
    }

    /**
     * Получить y.
     *
     * @return y
     */
    public Integer getLocationY() {
        return locationY;
    }

    /**
     * Установить y.
     *
     * @param locationY y
     */
    public void setLocationY(Integer locationY) throws FieldException {
        if (locationY == null) {
            throw new FieldException("y не может быть null");
        } else {
            this.locationY = locationY;
        }
    }

    /**
     * Получить z.
     *
     * @return z
     */
    public Integer getLocationZ() {
        return locationZ;
    }

    /**
     * Установить z.
     *
     * @param locationZ z
     */
    public void setLocationZ(Integer locationZ) throws FieldException {
        if (locationZ == null) {
            throw new FieldException("z не может быть null");
        } else {
            this.locationZ = locationZ;
        }
    }

    /**
     * Получить строку.
     *
     * @return строка
     */
    public String toString() {
        return "{x = " + locationX + ", y = " + locationY + ", z = " + locationZ + "}";
    }
}
