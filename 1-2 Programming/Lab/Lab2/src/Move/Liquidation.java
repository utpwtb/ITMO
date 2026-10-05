package Move;

import ru.ifmo.se.pokemon.*;

public class Liquidation extends PhysicalMove {
    public Liquidation() {
        super(Type.WATER, 85, 100);
    }

    @Override
    protected void applyOppEffects(Pokemon pokemon) {
        if (Math.random()<=0.2){
            pokemon.addEffect(new Effect().stat(Stat.DEFENSE,-1));
        }
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
