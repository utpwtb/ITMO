package MyPokemon;

import Move.FocusBlast;
import Move.Rest;
import Move.SlackOff;
import Move.WaterGun;
import ru.ifmo.se.pokemon.Type;

public class Slowbro extends Slowpoke {

    public Slowbro(String name, int level) {
        super(name, level);
        setType(Type.WATER, Type.PSYCHIC);
        setStats(90, 65, 65, 40, 40, 15);
        FocusBlast move4 = new FocusBlast();
        addMove(move4);
    }
}
