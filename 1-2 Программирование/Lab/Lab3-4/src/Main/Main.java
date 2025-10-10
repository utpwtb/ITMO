package Main;

import Characters.MainCharacters.Klepka;
import Characters.People;
import Characters.MainCharacters.Znayka;
import Characters.MainCharacters.Zvezdochkin;
import Characters.OtherCharacters.ShortPersons;
import MyException.StatusZeroGravityDeviceException;
import Places.AstronomicalObject.Moon;
import MyObject.ZeroGravityDevice;
import Places.MyObjectsOnStar.PyramidHill;
import Places.MyObjectsOnStar.Rocket;
import Places.MyObjectsOnStar.UnknownPlace;

import java.util.ArrayList;


public class Main {
    public static void main(String[] args) {

        Znayka znayka = new Znayka();
        Klepka klepka = new Klepka();
        Zvezdochkin zvezdochkin = new Zvezdochkin();
        Rocket rocket = new Rocket();
        PyramidHill pyramidHill = new PyramidHill();
        ZeroGravityDevice zeroGravityDevice = new ZeroGravityDevice();
        Moon moon = new Moon();

        ArrayList<People> peopleArrayList = new ArrayList<>();
        peopleArrayList.add(moon.setMember(znayka));
        peopleArrayList.add(moon.setMember(klepka));
        peopleArrayList.add(moon.setMember(zvezdochkin));
        moon.showMember();

        System.out.println("Objects on the moon:");
        moon.showMyObj(rocket);
        moon.showMyObj(pyramidHill);
        System.out.println();

        UnknownPlace unknownPlace = new UnknownPlace("a hundred meters");
        znayka.run(rocket, unknownPlace);
        znayka.stop(unknownPlace);
        System.out.println();

        klepka.run(rocket, znayka);
        zvezdochkin.run(rocket, znayka);
        System.out.println();

        try {
            zeroGravityDevice.open(znayka, peopleArrayList);
        } catch (StatusZeroGravityDeviceException e) {
            String message = e.getMessage();
            System.out.println(message);
        }
        for (People people : peopleArrayList) {
            people.gravityCondition(people);
        }
        System.out.println();

        klepka.flyUp(moon);
        zvezdochkin.flyUp(moon);
        System.out.println();

        znayka.saw("them fly");
        znayka.showMood(Znayka.Mood.SCARED);
        System.out.println();

        try {
            zeroGravityDevice.close(znayka, peopleArrayList);
        } catch (StatusZeroGravityDeviceException e) {
            String message = e.getMessage();
            System.out.println(message);
        }
        for (People people : peopleArrayList) {
            people.gravityCondition(people);
        }
        System.out.println();

        klepka.flyDown(moon);
        zvezdochkin.flyDown(moon);
        System.out.println();

        klepka.tell(znayka, "We're fine,we're just in shock");
        zvezdochkin.tell(znayka, "We're fine,we're just in shock");
        System.out.println();

        znayka.run(unknownPlace, rocket);
        System.out.println();

        ShortPersons shortPersons = new ShortPersons("Short Persons");
        shortPersons.comeOut(rocket);
        System.out.println();

        znayka.tell(shortPersons,"nothing");
        znayka.move(rocket, pyramidHill);
        System.out.println();

        try {
            zeroGravityDevice.open(znayka, peopleArrayList);
        } catch (StatusZeroGravityDeviceException e) {
            String message = e.getMessage();
            System.out.println(message);
        }
        znayka.say("No loss of gravity");

    }
}
