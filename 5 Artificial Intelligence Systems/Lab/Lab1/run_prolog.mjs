import SWIPL from 'swipl-wasm';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.dirname(fileURLToPath(import.meta.url)));
const swipl = await SWIPL({arguments:['-q']});
swipl.FS.writeFile('/knowledge.pl', fs.readFileSync('knowledge.pl','utf8'));
swipl.prolog.query("consult('/knowledge.pl')").once();
const cases = [
 ['character(aria)', 'findall(ok,character(aria),R)', ['ok']],
 ['character(dragon)', 'findall(ok,character(dragon),R)', []],
 ['warrior(X)', 'findall(X,warrior(X),R)', ['aria','borin']],
 ['owns(X,bow)', 'findall(X,owns(X,bow),R)', ['elin','finn']],
 ['combatant(X)', 'findall(X,combatant(X),R)', ['aria','borin','celia']],
 ['scout(X)', 'findall(X,scout(X),R)', ['elin','finn']],
 ['armed(X)', 'findall(X,armed(X),R)', ['aria','borin','celia','darin','elin','finn']],
 ['skilled_for(X,tower)', 'findall(X,skilled_for(X,tower),R)', ['celia']],
 ['ready_for(X,Q)', 'findall([X,Q],ready_for(X,Q),R)', [['aria','ruins'],['celia','tower'],['finn','forest']]],
 ['guildmate(X,Y)', 'findall([X,Y],guildmate(X,Y),R)', [['aria','celia'],['celia','aria']]],
 ['safe_character(X)', 'findall(X,safe_character(X),R)', ['aria','celia','darin','elin','finn']],
 ['ready_for(borin,ruins)', 'findall(ok,ready_for(borin,ruins),R)', []],
 ['guildmate(aria,aria)', 'findall(ok,guildmate(aria,aria),R)', []],
 ['combatant(X), safe_character(X)', 'findall(X,(combatant(X),safe_character(X)),R)', ['aria','celia']],
 ['safe_character(dragon)', 'findall(ok,safe_character(dragon),R)', []],
];
const results=cases.map(([query,goal,expected])=>{
 const actual=swipl.prolog.query(goal).once().R;
 const pass=JSON.stringify(actual)===JSON.stringify(expected);
 if(!pass) process.exitCode=1;
 console.log(`${pass?'PASS':'FAIL'} ${query}: ${JSON.stringify(actual)}`);
 return {query,expected,actual,pass};
});
fs.mkdirSync('results',{recursive:true});
fs.writeFileSync('results/prolog_results.json',JSON.stringify({version:swipl.prolog.query('current_prolog_flag(version_data,V)').once(),results},null,2));
