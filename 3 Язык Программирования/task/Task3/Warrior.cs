public class Warrior : Hero
{
    private static Random random = new Random();

    public Warrior(string name, int attack, int defense, int hp) :
        base(name,
            random.Next(25, 40),
            random.Next(10, 15),
            random.Next(80, 90))
    {

    }

    public override void SpecialAbility(Hero target)
    {
        target.HP -= this.Attack;
    }

    public override string UseArtifact()
    {
        this.Defense += 1;
        return $"{Name} used artifact to increase defense by 1.";
    }

}