package Characters.Interfaces;

import Characters.People;

public interface Say {
    void say(String sentence);

    void tell(People people, String sentence);

}
