package itmo.programming.Common.person;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import itmo.programming.Common.exceptions.FieldException;


/**
 * класс координат.
 */
public class Coordinates {
    private float coordinatesX;
    private long coordinatesY; // Максимальное значение поля: 797

    /**
     * Конструктор.
     */
    public Coordinates() {
    }

    /**
     * Конструктор.
     *
     * @param coordinatesX координата х
     * @param coordinatesY координата у
     */
    @JsonCreator
    public Coordinates(
            @JsonProperty("x") float coordinatesX,
            @JsonProperty("y") long coordinatesY) throws FieldException {
        this.coordinatesX = coordinatesX;
        this.coordinatesY = coordinatesY;
        final long maxValue = 797;
        if (coordinatesY > maxValue) {
            throw new FieldException("Максимальное значение y: 797");
        }
    }

    /**
     * Получить x.
     *
     * @return x
     */
    public float getCoordinatesX() {
        return coordinatesX;
    }

    /**
     * Установить x.
     *
     * @param coordinatesX x
     */
    public void setCoordinatesX(float coordinatesX) {
        this.coordinatesX = coordinatesX;
    }

    /**
     * Получить y.
     *
     * @return y
     */
    public long getCoordinatesY() {
        return coordinatesY;
    }

    /**
     * Установить y.
     *
     * @param coordinatesY y
     */
    public void setCoordinatesY(long coordinatesY) throws FieldException {
        final long maxValue = 797;
        if (coordinatesY > maxValue) {
            throw new FieldException("Максимальное значение y: 797");
        } else {
            this.coordinatesY = coordinatesY;
        }
    }

    /**
     * Получить строку.
     *
     * @return строка
     */
    public String toString() {
        return "{x = " + coordinatesX + ", y = " + coordinatesY + "}";
    }
}
