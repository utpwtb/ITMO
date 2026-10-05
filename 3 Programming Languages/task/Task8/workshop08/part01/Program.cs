using System;
using System.Reflection;
using part01;

var engine = new SkillEngine();

engine.RegisterAssembly(Assembly.GetExecutingAssembly());

var context = new BattleContext
{
    DamageDealt = 100,
    Attacker = new UnitStats { Hp = 50 },
    Defender = new UnitStats { Hp = 100 }
};

Console.WriteLine("");
Console.WriteLine("=== Battle Start ===");

Console.WriteLine("--- OnDefense Phase ---");
engine.ExecutePipeline(TriggerType.OnDefense, context);

Console.WriteLine("--- OnAttack Phase ---");
engine.ExecutePipeline(TriggerType.OnAttack, context);

Console.WriteLine("--- PostBattle Phase ---");
engine.ExecutePipeline(TriggerType.PostBattle, context);

Console.WriteLine("=== Battle End ===");

Console.WriteLine($"Final DamageDealt: {context.DamageDealt}");
Console.WriteLine($"Attacker Final HP: {context.Attacker.Hp}");
Console.WriteLine($"Defender Final HP: {context.Defender.Hp}");
