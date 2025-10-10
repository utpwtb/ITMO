package person;

import Exceptions.FieldException;

public class Location {
    private Double x; //Поле не может быть null
    private Integer y; //Поле не может быть null
    private Integer z; //Поле не может быть null

    /**
     * Конструктор
     */
    public Location() {
    }

    /**
     * Конструктор
     * @param x x
     * @param y y
     * @param z z
     */
    public Location(Double x, Integer y, Integer z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    /**
     * @return x
     */
    public Double getX() {
        return x;
    }

    /**
     * @param x x
     */
    public void setX(Double x) throws FieldException {
        if (x == null){
            throw new FieldException("x не может быть null");
        }else {
            this.x = x;
        }
    }

    /**
     * @return y
     */
    public Integer getY() {
        return y;
    }

    /**
     * @param y y
     */
    public void setY(Integer y) throws FieldException{
        if (y == null){
            throw new FieldException("y не может быть null");
        }else {
            this.y = y;
        }
    }

    /**
     * @return z
     */
    public Integer getZ() {
        return z;
    }

    /**
     * @param z z
     */
    public void setZ(Integer z) throws FieldException{
        if (z == null){
            throw new FieldException("z не может быть null");
        }else {
            this.z = z;
        }
    }

    public String toString() {
        return "{x = " + x + ", y = " + y + ", z = " + z + "}";
    }
}
