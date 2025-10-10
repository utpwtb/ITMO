package Places;

import Characters.People;

import java.util.ArrayList;

public abstract class Place {
    private String placeName;
    ArrayList<People> peopleArrayList = new ArrayList<>();


    public Place() {
    }

    public Place(String placeName) {
        this.placeName = placeName;
    }

    public String getPlaceName() {
        return placeName;
    }

    public void setPlaceName(String placeName) {
        this.placeName = placeName;
    }

    public People setMember(People people) {
        peopleArrayList.add(people);
        return people;
    }

    public void showMember() {
        System.out.println("Now in the " + this.placeName + " are: ");
        for (People people : peopleArrayList) {
            if (people == null) {
                continue;
            }
            System.out.print(people.getName() + " ");
        }
        System.out.println(".\n");
    }

    public String toString() {
        return this.getPlaceName();
    }
}
