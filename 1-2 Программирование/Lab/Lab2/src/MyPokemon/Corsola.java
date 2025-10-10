package MyPokemon;

import Move.IcicleSpear;
import Move.Liquidation;
import Move.RockPolish;
import Move.Tackle;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Corsola extends Pokemon {
    public Corsola(String name, int level) {
        super(name, level);
        setType(Type.WATER, Type.ROCK);
        setStats(65, 55, 95, 65, 95, 35);
        RockPolish move1 = new RockPolish();
        Liquidation move2 = new Liquidation();
        IcicleSpear move3 = new IcicleSpear();
        Tackle move4 = new Tackle();
        setMove(move1, move2, move3, move4);
    }
}
