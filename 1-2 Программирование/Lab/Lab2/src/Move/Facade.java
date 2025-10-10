package Move;

import ru.ifmo.se.pokemon.*;

public class Facade extends PhysicalMove {
    public Facade() {
        super(Type.NORMAL, 70, 100);
    }

    @Override
    protected void applyOppDamage(Pokemon pokemon, double v) {
        pokemon.setMod(Stat.HP, 70);
    }

    @Override
    protected String describe() {
        return "used " + this.getClass().getSimpleName();
    }
}
