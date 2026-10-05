package Places.AstronomicalObject;

import Places.MyObjectsOnStar.MyObj;
import Places.MyObjectsOnStar.ShowMyObj;
import Places.Place;

public abstract class AstronomicalObject extends Place implements ShowMyObj {

    public AstronomicalObject() {
        this.setPlaceName("a Star");
    }

    public AstronomicalObject(String placeName) {
        super(placeName);
    }

    public String toString() {
        return "AstronomicalObject{}";
    }

    @Override
    public void showMyObj(MyObj myObj) {
        System.out.println("On the " + this.getPlaceName() + " have " + myObj.getPlaceName());
    }
}
