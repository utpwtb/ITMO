package MyPokemon;

import Move.MudBomb;
import ru.ifmo.se.pokemon.Type;

public class Chansey extends Happiny {
    public Chansey(String name, int level) {
        super(name, level);
        setType(Type.NORMAL);
        setStats(250, 5, 5, 35, 105, 50);
        MudBomb move3 = new MudBomb();
        addMove(move3);
    }
}
