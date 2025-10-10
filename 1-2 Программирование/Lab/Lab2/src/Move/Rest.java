package Move;

import ru.ifmo.se.pokemon.Effect;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.StatusMove;
import ru.ifmo.se.pokemon.Type;

public class Rest extends StatusMove {
    public Rest(){
        super(Type.PSYCHIC,0,0);
    }

    @Override
    protected void applyOppEffects(Pokemon pokemon) {
        Effect.sleep(pokemon);
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
