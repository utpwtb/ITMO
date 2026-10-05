package Move;

import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.SpecialMove;
import ru.ifmo.se.pokemon.Stat;
import ru.ifmo.se.pokemon.Type;

public class WaterGun extends SpecialMove {
    public WaterGun(){
        super(Type.WATER,40,100);
    }

    @Override
    protected void applyOppDamage(Pokemon pokemon, double v) {
        pokemon.setMod(Stat.HP,1);
    }

    @Override
    protected String describe() {
        return "used "  + this.getClass().getSimpleName();
    }
}
