package Move;

import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Stat;
import ru.ifmo.se.pokemon.StatusMove;
import ru.ifmo.se.pokemon.Type;

public class SlackOff extends StatusMove {
    public SlackOff() {
        super(Type.NORMAL, 0, 0);
    }

    @Override
    protected void applySelfEffects(Pokemon pokemon) {
        pokemon.setMod(Stat.HP, (int) (pokemon.getHP() * (Math.random() * 0.5 + 1)));
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
