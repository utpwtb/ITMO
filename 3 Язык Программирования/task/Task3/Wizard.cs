public class Wizard : Hero
{
    private static Random random  = new Random();

    public Wizard(string name, int attack, int defense, int hp) :
        base(name,
            random.Next(10, 15),
            random.Next(20, 30),
            random.Next(110, 120))
    {

    }

    public override void SpecialAbility(Hero target)
    {
        target.TakeDamage(2 * this.Attack);
    }

    public override string UseArtifact()
    {
        this.HP += 5;
        return $"{Name} used artifact to increase HP by 5.";
    }
}