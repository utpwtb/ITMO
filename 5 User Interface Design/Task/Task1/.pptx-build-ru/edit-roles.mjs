import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const workspaceDir='C:/develop/NOTE_UTP/StudyNote/5 User Interface Design/Task/Task1';
const build=path.join(workspaceDir,'.pptx-build-ru/roles-and-thanks');
const skill='C:/Users/CHL/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
const runtime='C:/Users/CHL/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
await fs.mkdir(build,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(workspaceDir,'presentation/AI_Knowledge_Agent_RU_20260920.pptx')));
const C={bg:'#F7F6F2',ink:'#182B3A',muted:'#61707A',blue:'#315FEA',white:'#FFFFFF'};
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false){
 const t=s.shapes.add({geometry:'textbox',name:str.slice(0,70),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=str;t.text.style={typeface:'Arial',fontSize:size,color,bold,autoFit:'none',verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};return t;
}
const records=(await p.inspect({kind:'slide,textbox,table',maxChars:150000})).ndjson.split('\n').filter(Boolean).map(s=>JSON.parse(s));
const s6=p.resolve(records.find(r=>r.kind==='slide'&&r.slide===6).id);
for(const r of records.filter(r=>r.kind==='textbox'&&r.slide===6&&r.id!=='sh/dcnm98zm'&&r.id!=='sh/yhg7epsj'))p.resolve(r.id).delete();
text(s6,'Условный пример',72,139,1090,32,21,C.muted);
text(s6,'Исходный диалог',72,201,305,44,27,C.muted,true);
text(s6,'До импорта в приложение',72,247,314,40,22,C.muted);
text(s6,'«Как делать\nрезервные копии?»',72,311,315,90,28);
text(s6,'«Как проверить\nвосстановление?»',72,423,315,88,28);
text(s6,'Ответы ИИ и уточнения\nпользователя',72,526,315,69,24,C.muted);
text(s6,'Система обрабатывает',432,201,414,44,27,C.blue,true);
text(s6,'Извлекает знание:\nпроверка восстановления',432,283,408,87,26);
text(s6,'Находит заметку\n«Резервное копирование»',432,387,408,88,26);
text(s6,'Готовит дополнение\nи связи с другими заметками',432,494,408,92,26);
text(s6,'Результат в базе',900,201,309,44,27,C.blue,true);
text(s6,'Дополненная\nзаметка со связями',900,283,309,105,32,C.ink,true);
text(s6,'Система генерирует текст,\nзаписывает изменения\nи проверяет результат.',900,419,309,128,25);
text(s6,'Пользователь импортирует диалог и при необходимости одобряет план.',72,617,1110,36,24,C.blue);
text(s6,'Низкорисковые новые заметки могут сохраняться автоматически по настройке.',72,657,1050,32,21,C.muted);
s6.speakerNotes.textFrame.setText('Слева показан исходный разговор, который уже состоялся между человеком и ИИ до импорта в наше приложение. В нём обсуждаются резервные копии и проверка восстановления. Пользователь импортирует этот разговор. Далее система сама выделяет ценные знания, ищет существующие заметки и определяет, что создать, дополнить, связать или пропустить. В этом условном примере она находит заметку о резервном копировании и готовит добавление раздела о проверке восстановления. Пользователь по умолчанию рассматривает готовый план: он может одобрить его, исключить отдельные действия или отказаться. Генерацию текста, запись и проверку результата выполняет система после допуска плана. При включённой настройке низкорисковые планы создания новых заметок могут проходить автоматически. Рассматриваемый пример дополняет существующую заметку, поэтому не относится к автоматическому созданию новых заметок.\n\nОснование: docs/agent-workflow.md, шаги 4–13 и раздел 5; docs/architecture.md, D2 и D5; backend/app/agent/policy.py. Сценарий иллюстративный.');

const s8=p.resolve(records.find(r=>r.kind==='slide'&&r.slide===8).id);
const tb=p.resolve(records.find(r=>r.kind==='table'&&r.slide===8).id);
const values=[
 ['Способ работы','Ручная работа\nбез нашего приложения','Что выполняет\nнаша система'],
 ['Сохранить историю\nразговора','Перечитать и найти\nважные фрагменты','Извлекает ценные знания\nиз разных реплик'],
 ['Перенести вручную\nв заметки','Организовать материал\nи проверить повторы','Находит связанные заметки,\nопределяет дополнения\nи повторы'],
 ['Получить резюме\nи сохранить вручную','Выбрать место, записать\nи связать с прежними заметками','Генерирует текст, создаёт\nили дополняет заметки,\nдобавляет связи']
];
const heights=[80,90,101,101];
for(let r=0;r<4;r++){
 tb.rows[r].height=heights[r];
 for(let c=0;c<3;c++){
  tb.cells.set(r,c,values[r][c]);
  tb.getCell(r,c).text.style={typeface:'Arial',fontSize:r===0?23:24,color:r===0?C.white:c===2?C.blue:C.ink,bold:r===0};
 }
}
p.resolve('sh/ri9g7uhw').delete();
text(s8,'После допуска плана система записывает изменения и проверяет результат.',72,597,1136,40,25,C.blue);
text(s8,'Пользователь импортирует диалог и при необходимости проверяет план.',72,640,1080,35,23,C.muted);
s8.speakerNotes.textFrame.setText('В этой таблице средняя колонка описывает ручную работу при использовании обычных способов без нашего приложения. Эти действия не возлагаются на пользователя нашего продукта. Система сама извлекает знания, определяет структуру, ищет существующие заметки, сравнивает содержание и готовит действия. Затем, после допуска плана, она генерирует текст, создаёт или дополняет заметки и записывает ссылки. Она также проверяет сохранённые файлы. Пользователь импортирует диалог и в режиме с подтверждением проверяет готовый план, может исключить отдельные действия или отказать. Конфликты требуют решения человека. Низкорисковые планы создания заметок могут выполняться автоматически, если пользователь включил соответствующую настройку. По умолчанию автоматический допуск выключен. Именно сокращение повторного чтения и ручной организации даёт основание ожидать выигрыша во времени. Этот эффект ещё нужно проверить в пользовательском тесте.\n\nОснование: docs/architecture.md, таблица D2; docs/agent-workflow.md, шаги 8–13 и раздел 5; backend/app/agent/policy.py. Сравнение рабочих сценариев, без утверждения об измеренном превосходстве.');

const s7=p.resolve(records.find(r=>r.kind==='slide'&&r.slide===7).id);
p.resolve('sh/l0vuh0rm').text='Найденная заметка\nи план системы';
s7.speakerNotes.textFrame.setText('Пользователь импортирует разговор. Система автоматически анализирует его, извлекает знания и сопоставляет их с базой. На концептуальном макете слева показаны найденное знание и фрагмент исходного разговора, а справа — выбранная системой заметка и предлагаемое дополнение. Пользователь рассматривает уже подготовленный план: может исключить действие, одобрить план или отказаться. После допуска плана система сама генерирует содержание, записывает изменения и проверяет результат. По умолчанию включено подтверждение. Настройка автоматического допуска распространяется на соответствующие условиям низкорисковые планы создания новых заметок. Показанный пример дополнения существующей заметки требует проверки плана. В текущей реализации план показывает структуру и назначение изменений, окончательный текст генерируется после допуска. Макет является концепцией интерфейса.\n\nОснование: docs/agent-workflow.md, шаги 8–13; backend/app/agent/policy.py; frontend/src/components/PlanPanel.vue.');

const s10=p.slides.add();s10.background.fill=C.ink;
text(s10,'Спасибо за внимание!',72,247,1136,118,76,C.white,true);
text(s10,'Готовы ответить на ваши вопросы',76,408,1095,68,32,'#D1DCE4');
text(s10,'Conversation-to-Knowledge Agent',76,605,1080,36,23,'#A8B7C3');
text(s10,'10',1170,665,45,25,18,'#A8B7C3');
s10.speakerNotes.textFrame.setText('Спасибо за внимание! Готовы ответить на ваши вопросы о проекте и предлагаемом интерфейсе.');

const candidatePath=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(workspaceDir,'presentation/AI_Knowledge_Agent_RU_Final_10slides.pptx');
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath,pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','5','--require-native-table-slide','8'],explicitTotalSlideCount:10,requiredNativeTableOwnerSlides:[5,8],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify({finalPath:result.finalPath,sha256:result.finalSha256,layoutFindings:result.presentationLayout.findingCount}));
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(let i=0;i<final.slides.items.length;i++){
 const slide=final.slides.items[i];const png=await final.export({slide,format:'png',scale:1});await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));console.log(`Rendered ${i+1}`);
}
