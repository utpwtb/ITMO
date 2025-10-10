package Move;

import ru.ifmo.se.pokemon.*;

public class FocusBlast extends SpecialMove {
    public FocusBlast() {
        super(Type.FIGHTING, 120, 70);
    }

    @Override
    protected void applyOppEffects(Pokemon pokemon) {
        if (Math.random() < 0.1) {
            pokemon.addEffect(new Effect().stat(Stat.DEFENSE, -1));
        }
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
