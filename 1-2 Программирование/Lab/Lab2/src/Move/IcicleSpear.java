package Move;

import ru.ifmo.se.pokemon.PhysicalMove;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Stat;
import ru.ifmo.se.pokemon.Type;

public class IcicleSpear extends PhysicalMove {
    public IcicleSpear() {
        super(Type.ICE, 25, 100);
    }

    @Override
    protected void applyOppDamage(Pokemon pokemon, double v) {
        if (Math.random() <= 0.375) {
            pokemon.setMod(Stat.HP, 50);
        } else if (Math.random() <= 0.75) {
            pokemon.setMod(Stat.HP, 75);
        } else if (Math.random() <= 0.875) {
            pokemon.setMod(Stat.HP, 100);
        } else {
            pokemon.setMod(Stat.HP, 125);
        }
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
