package person;

import Exceptions.FieldException;

/**
 * класс координат
 */
public class Coordinates {
    private float x;
    private long y; //Максимальное значение поля: 797

    /**
     * Конструктор
     */
    public Coordinates() {
    }

    /**
     * Конструктор
     *
     * @param x координата х
     * @param y координата у
     */
    public Coordinates(float x, long y) {
        this.x = x;
        this.y = y;
    }

    /**
     * @return x
     */
    public float getX() {
        return x;
    }

    /**
     * @param x x
     */
    public void setX(float x) {
        this.x = x;
    }

    /**
     * @return y
     */
    public long getY() {
        return y;
    }

    /**
     * @param y y
     */
    public void setY(long y) throws FieldException {
        if (y > 797){
            throw new FieldException("Максимальное значение y: 797");
        }else {
            this.y = y;
        }
    }

    public String toString() {
        return "{x = " + x + ", y = " + y + "}";
    }
}
