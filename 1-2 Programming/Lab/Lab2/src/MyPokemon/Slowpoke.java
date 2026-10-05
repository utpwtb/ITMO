package MyPokemon;

import Move.Rest;
import Move.SlackOff;
import Move.WaterGun;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Slowpoke extends Pokemon {
    public Slowpoke(String name, int level) {
        super(name, level);
        setType(Type.WATER, Type.PSYCHIC);
        setStats(90, 65, 65, 40, 40, 15);
        Rest move1 = new Rest();
        SlackOff move2 = new SlackOff();
        WaterGun move3 = new WaterGun();
        setMove(move1, move2, move3);
    }
}
