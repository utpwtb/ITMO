package Characters.Interfaces;

import Characters.People;
import Places.AstronomicalObject.AstronomicalObject;
import Places.Place;

public interface Move {

    void run(Place from, People people);

    void run(Place from, Place to);

    void flyUp(AstronomicalObject astronomicalObject);

    void flyDown(AstronomicalObject astronomicalObject);

    void stop(Place place);

    void move(Place from, Place to);

    void comeOut(Place place);
}
