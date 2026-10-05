package Fight;

import MyPokemon.*;
import ru.ifmo.se.pokemon.Battle;

public class Main {
    public static void main(String[] args) {
        Battle battle = new Battle();
        battle.addAlly(new Corsola("t1-1",30));
        battle.addAlly(new Slowpoke("t1-2",70));
        battle.addAlly(new Slowbro("t1-3",100));
        battle.addFoe(new Happiny("t2-1",30));
        battle.addFoe(new Chansey("t2-2",70));
        battle.addFoe(new Blissey("t2-3",100));
        battle.go();
    }
}
