public class AutoBattler
{
    private Hero hero1;
    private Hero hero2;
    private Random random = new Random();
    private int turnCounter = 0;
    private string logFile = Path.Combine(Environment.CurrentDirectory, "log.txt");

    public AutoBattler(Hero hero1, Hero hero2)
    {
        this.hero1 = hero1;
        this.hero2 = hero2;
        File.WriteAllText(logFile, "Battle Start!\n");
    }

    public void StartBattle()
    {
        ConsoleUtils.Logger($"Battle Start! {hero1.Name} VS {hero2.Name}", ConsoleColor.Red);
        ConsoleUtils.Logger(hero1.ToString(), ConsoleColor.Cyan);
        ConsoleUtils.Logger(hero2.ToString(), ConsoleColor.Green);
        File.AppendAllText(logFile, $"Battle Start! {hero1.Name} VS {hero2.Name}\n");
        File.AppendAllText(logFile, hero1.ToString() + "\n");
        File.AppendAllText(logFile, hero2.ToString() + "\n");

        while (hero1.HP > 0 && hero2.HP > 0)
        {
            turnCounter++;
            Hero attacker = random.Next(0, 2) == 0 ? hero1 : hero2;
            Hero defender = attacker == hero1 ? hero2 : hero1;
            ConsoleColor color = attacker == hero1 ? ConsoleColor.Cyan : ConsoleColor.Green;

            if (random.Next(0, 100) < 20)
            {
                string message = attacker.UseArtifact();
                ConsoleUtils.Logger(message, ConsoleColor.Yellow);
                ConsoleUtils.Logger($"{attacker.Name} HP is now {attacker.HP}, Defense is {attacker.Defense}", ConsoleColor.Magenta);
                File.AppendAllText(logFile, message + "\n");
                File.AppendAllText(logFile, $"{attacker.Name} HP is now {attacker.HP}, Defense is {attacker.Defense}\n");
                
                continue;
            }

            if (turnCounter % 3 == 0)
            {
                attacker.SpecialAbility(defender);
                ConsoleUtils.Logger($"{attacker.Name} used special ability!", color);
                ConsoleUtils.Logger($"{defender.Name} HP is now {defender.HP}", ConsoleColor.Magenta);
                File.AppendAllText(logFile, $"{attacker.Name} used special ability!\n");
            }
            else
            {
                defender.TakeDamage(attacker.Attack);
                ConsoleUtils.Logger($"{attacker.Name} attacked {defender.Name} for {attacker.Attack} damage.", color);
                ConsoleUtils.Logger($"{defender.Name} HP is now {defender.HP}", ConsoleColor.Magenta);
                File.AppendAllText(logFile, $"{attacker.Name} attacked {defender.Name} for {attacker.Attack} damage.\n");
            }

            ConsoleUtils.Beep();
        }

        Hero winner = hero1.HP > 0 ? hero1 : hero2;
        ConsoleUtils.Logger($"{winner.Name} wins!", ConsoleColor.Yellow);
        File.AppendAllText(logFile, $"{winner.Name} wins!\n");

        
    }

}