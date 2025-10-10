public interface IAttackable
{
    void TakeDamage(int damage);
}

public interface IArtifact
{
    void Use(Hero hero);
}

public abstract class Hero : IAttackable
{
    // Property
    public string Name { get; set; }
    public int Attack { get; set; }
    public int Defense { get; set; }
    public int HP { get; set; }

    public IArtifact Artifact { get; set; }

    public Hero(string name, int attack, int defense, int hp)
    {
        Attack = attack;
        HP = hp;
        Defense = defense;
        Name = name;
    }

    public void TakeDamage(int damage)
    {
        if (damage < 0)
        {
            return;
        }
        if (damage < Defense)
        {
            return;
        }

        HP -= damage - Defense;
    }

    //public abstract void TakeDamage(int damage);

    // abstract => без реализации
    // abstract => обязательно делать override
    public abstract void SpecialAbility(Hero target);

    // virtual => обязан быть с телом
    // virtual => не обязательно делать override
    public virtual string UseArtifact()
    {
        if (Artifact == null) return String.Empty;
        return $"{this.Name} used Artifact.";
    }

    public override string ToString()
    {
        return $"[Name = {Name}, HP = {HP}, Damage = {Attack}, Defense = {Defense}, {2 + 2}]";
    }
}




