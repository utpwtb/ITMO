package MyObject;

import Characters.People;
import MyException.StatusZeroGravityDeviceException;

import java.util.ArrayList;
import java.util.Random;


public class ZeroGravityDevice {
    boolean deviceStatus;
    public double getR() {
        final Random r = new Random();
        return r.nextDouble();
    }

    public void changeGravityCondition(ArrayList<People> peopleArrayList) {
        if (peopleArrayList.get(0).getGravityFlag() == -1) {
            for (People people : peopleArrayList) {
                people.setGravityFlag(-1);
            }
        } else if (peopleArrayList.get(0).getGravityFlag() == 1) {
            for (People people : peopleArrayList) {
                people.setGravityFlag(1);
            }
        }
    }

    public void open(People people, ArrayList<People> peopleArrayList) {
        if (this.getR() < 0.1) {
            people.setGravityFlag(0);
            throw new StatusZeroGravityDeviceException("Gravity device is not working");
        }
        deviceStatus = true;
        people.setGravityFlag(-1);
        changeGravityCondition(peopleArrayList);
        System.out.println(people.getName() + " opened gravity device.");
    }


    public void close(People people, ArrayList<People> peopleArrayList) {
        if (!deviceStatus) {
            people.setGravityFlag(0);
            throw new StatusZeroGravityDeviceException("Gravity device is not working");
        }
        deviceStatus = false;
        people.setGravityFlag(1);
        changeGravityCondition(peopleArrayList);
        System.out.println(people.getName() + " closed gravity device.");
    }

}
