package MyPokemon;

import Move.ThunderWave;
import ru.ifmo.se.pokemon.Type;

public class Blissey extends Chansey {
    public Blissey(String name, int level) {
        super(name, level);
        setType(Type.NORMAL);
        setStats(255, 10, 10, 75, 135, 55);
        ThunderWave move4 = new ThunderWave();
        addMove(move4);
    }
}
