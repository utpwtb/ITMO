package Move;

import ru.ifmo.se.pokemon.*;

public class MudBomb extends SpecialMove {
    public MudBomb() {
        super(Type.GROUND, 65, 85);
    }

    @Override
    protected void applyOppEffects(Pokemon pokemon) {
        if (Math.random() <= 0.3){
            pokemon.addEffect(new Effect().stat(Stat.ACCURACY,-1));
        }
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
