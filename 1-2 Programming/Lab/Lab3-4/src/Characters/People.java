package Characters;

import Characters.Interfaces.Condition;
import Characters.Interfaces.Move;
import Characters.Interfaces.Saw;
import Characters.Interfaces.Say;
import Places.AstronomicalObject.AstronomicalObject;
import Places.Place;
import Places.MyObjectsOnStar.UnknownPlace;

import java.util.Objects;

public abstract class People implements Move, Condition, Say, Saw {

    public People() {
        this.name = "Someone";
        this.location = new UnknownPlace();
    }

    public People(String name) {
        this.name = name;
        this.location = new UnknownPlace();
    }

    public enum Mood {
        SCARED, UNKNOWN

    }

    private String name;
    private Mood mood;
    private Place location;
    private int gravityFlag;//如果有重力就是1，如果没有重力就是-1，不改变是0
    private boolean locationFlag = true;//如果已经飞起来了就是false不能飞，反之就是true

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Mood getMood(Mood mood) {
        return mood;
    }

    public void setMood(Mood mood) {
        this.mood = mood;
    }

    public Place getLocation() {
        return location;
    }


    public int getGravityFlag() {
        return gravityFlag;
    }

    public void setGravityFlag(int gravityFlag) {
        this.gravityFlag = gravityFlag;
    }

    public boolean getLocationFlag() {
        return locationFlag;
    }

    public void setLocationFlag(boolean locationFlag) {
        this.locationFlag = locationFlag;
    }

    public void setLocation(Place location) {
        this.location.setMember(this);
    }

    public String toString() {
        return "People{name = " + name + ", mood = " + mood + ", location = " + location + "}";
    }

    public void showMood(Mood mood) {
        System.out.println(this.getName() + " is in " + mood.toString().toLowerCase());
    }

    @Override
    public void gravityCondition(People people) {
        if (people.getGravityFlag() == -1) {
            System.out.println(this.getName() + " lost gravity");
        } else if (people.getGravityFlag() == 1) {
            System.out.println(this.getName() + " get gravity");
        } else {
            System.out.println("Gravity doesn't change");
        }

    }

    @Override
    public void run(Place from, People people) {
        System.out.println(this.getName() + " from " + from.getPlaceName() + " run to " + people.getName());
    }

    @Override
    public void run(Place from, Place to) {
        System.out.println(this.name + " from " + from.getPlaceName() + " run to " + to.getPlaceName());
    }

    @Override
    public void flyUp(AstronomicalObject astronomicalObject) {
        if (this.getGravityFlag() == -1 && locationFlag) {//没有重力，也就是flag为true时可以飞起来,在地上location是true
            locationFlag = false;
            System.out.println(this.getName() + "  flying on the " + astronomicalObject.getPlaceName());
        } else if (this.getGravityFlag() == 0) {
            System.out.println("Gravity device is not working,you can not move");
        } else {
            System.out.println(this.getName() + " flew up");
        }
    }

    @Override
    public void flyDown(AstronomicalObject astronomicalObject) {
        if (this.getGravityFlag() == 1 && !locationFlag) {
            locationFlag = true;
            System.out.println(this.getName() + " flying down to the " + astronomicalObject.getPlaceName());
        } else if (this.getGravityFlag() == 0) {
            System.out.println("Gravity device is not working,you can not move");
        } else {
            System.out.println(this.getName() + " on the " + astronomicalObject.getPlaceName());
        }
    }

    @Override
    public void stop(Place place) {
        System.out.println(this.getName() + " stopped at the " + place);
    }

    @Override
    public void move(Place from, Place to) {
        System.out.println(this.getName() + " from " + from.getPlaceName() + " run to " + to.getPlaceName());
    }

    @Override
    public void comeOut(Place place) {
        System.out.println(this.getName() + " come out of the " + place.getPlaceName());
    }

    @Override
    public void say(String sentence) {
        System.out.println(this.getName() + " say " + sentence);
    }

    @Override
    public void tell(People people, String sentence) {
        System.out.println(this.getName() + " say " + sentence + " to " + people.getName());
    }

    @Override
    public void saw(String s) {
        System.out.println(this.getName() + " saw " + s);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        People people = (People) o;
        return gravityFlag == people.gravityFlag && locationFlag == people.locationFlag && Objects.equals(name, people.name) && mood == people.mood && Objects.equals(location, people.location);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, mood, location, gravityFlag, locationFlag);
    }
}
