using System;
using System.Reflection.Emit;

namespace part01
{
    [GameAttribute]
    public class DefenseAndAftermathMechanics
    {
        private static readonly Func<int, int> _halfDamage = BuildHalfDamage();
        private static readonly Action<BattleContext> _postBattleMinus20 = BuildPostBattleMinus20Hp();

        [CombatSkill("HalfDamageOnDefense", TriggerType.OnDefense, priority: 100)]
        public void OnDefense(BattleContext ctx)
        {
            ctx.DamageDealt = _halfDamage(ctx.DamageDealt);
            Console.WriteLine("OnDefense: DamageDealt halved.");
        }

        [CombatSkill("Minus20HpPostBattle", TriggerType.PostBattle, priority: 1)]
        public void PostBattle(BattleContext ctx)
        {
            _postBattleMinus20(ctx);
            Console.WriteLine("PostBattle: both units lost 20 HP.");
        }

        private static Func<int, int> BuildHalfDamage()
        {
            var dm = new DynamicMethod(
                name: "HalfDamage",
                returnType: typeof(int),
                parameterTypes: new[] { typeof(int) },
                m: typeof(DefenseAndAftermathMechanics).Module,
                skipVisibility: true);

            ILGenerator il = dm.GetILGenerator();
            //var damageField = typeof(BattleContext)
             //   .GetField(nameof(BattleContext.DamageDealt))!; // super slow

            il.Emit(OpCodes.Ldarg_0); 
            //il.Emit(OpCodes.Ldarg_0); 
            //il.Emit(OpCodes.Ldfld, damageField); 
            il.Emit(OpCodes.Ldc_I4_2);            
            il.Emit(OpCodes.Div);                 
            //il.Emit(OpCodes.Stfld, damageField);  
            il.Emit(OpCodes.Ret);
        

            return (Func<int, int>)dm.CreateDelegate(typeof(Func<int, int>));
        }


        private static Action<BattleContext> BuildPostBattleMinus20Hp()
        {
            var dm = new DynamicMethod(
                name: "PostBattleMinus20",
                returnType: typeof(void),
                parameterTypes: new[] { typeof(BattleContext) },
                m: typeof(DefenseAndAftermathMechanics).Module,
                skipVisibility: true);

            ILGenerator il = dm.GetILGenerator();

            var attackerLocal = il.DeclareLocal(typeof(UnitStats)); 
            var defenderLocal = il.DeclareLocal(typeof(UnitStats)); 

            var attackerField = typeof(BattleContext)
                .GetField(nameof(BattleContext.Attacker))!;
            var defenderField = typeof(BattleContext)
                .GetField(nameof(BattleContext.Defender))!;
            var hpField = typeof(UnitStats)
                .GetField(nameof(UnitStats.Hp))!;

            il.Emit(OpCodes.Ldarg_0);
            il.Emit(OpCodes.Ldfld, attackerField);
            il.Emit(OpCodes.Stloc, attackerLocal);

            il.Emit(OpCodes.Ldarg_0);
            il.Emit(OpCodes.Ldfld, defenderField);
            il.Emit(OpCodes.Stloc, defenderLocal);

            il.Emit(OpCodes.Ldloc, attackerLocal); 
            il.Emit(OpCodes.Ldloc, attackerLocal);
            il.Emit(OpCodes.Ldfld, hpField);
            il.Emit(OpCodes.Ldc_I4_S, 20);
            il.Emit(OpCodes.Sub);
            il.Emit(OpCodes.Stfld, hpField);

            il.Emit(OpCodes.Ldloc, defenderLocal); 
            il.Emit(OpCodes.Ldloc, defenderLocal);
            il.Emit(OpCodes.Ldfld, hpField);
            il.Emit(OpCodes.Ldc_I4_S, 20);
            il.Emit(OpCodes.Sub);
            il.Emit(OpCodes.Stfld, hpField);

            il.Emit(OpCodes.Ret);

            return (Action<BattleContext>)dm.CreateDelegate(typeof(Action<BattleContext>));
        }
    }
}
