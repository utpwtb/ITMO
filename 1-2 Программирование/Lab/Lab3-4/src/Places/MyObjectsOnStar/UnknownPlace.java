package Places.MyObjectsOnStar;

import Places.Place;

public class UnknownPlace extends Place {
    public UnknownPlace() {
        this.setPlaceName("Some Place");
    }

    public UnknownPlace(String placeName) {
        super(placeName);
    }
}
