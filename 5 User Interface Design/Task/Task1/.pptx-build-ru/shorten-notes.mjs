import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const workspaceDir='C:/develop/NOTE_UTP/StudyNote/5 User Interface Design/Task/Task1';
const build=path.join(workspaceDir,'.pptx-build-ru/short-notes');
const skill='C:/Users/CHL/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
const runtime='C:/Users/CHL/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const notes=[
`Наш проект помогает сохранять полезные знания из разговоров с ИИ.
Человек задаёт вопросы, уточняет ответы и приходит к выводам.
Система анализирует весь диалог и добавляет важное в личную базу Obsidian.
Она связывает новые знания с существующими заметками.`,
`Наши пользователи часто обсуждают с ИИ рабочие задачи, личные проекты или новые темы.
Они хотят использовать полученные знания позже.
Например, это разработчики, исследователи и авторы.
На первом этапе мы ориентируемся на людей, которые уже ведут заметки в Obsidian.`,
`Полезный вывод часто появляется после нескольких вопросов и уточнений.
Важная информация остаётся в разных частях разговора.
Чтобы сохранить её, человеку приходится перечитывать диалог и собирать заметку вручную.
Наш интерфейс помогает организовать эти знания по темам и связать их между собой.`,
`Мы сохраняем понятия, способы решения задач и важные выводы.
Также полезно показать, как изменилось понимание человека во время разговора.
Повторы и случайные детали можно пропустить.
Главный вопрос: будет ли это знание полезно через несколько месяцев?`,
`Система сравнивает новые знания с базой.
Для новой темы она создаёт заметку, а знакомую тему дополняет.
Небольшую деталь можно добавить в отдельный раздел.
Повторы система пропускает, связанные заметки соединяет ссылками.
Если есть противоречие, решение принимает пользователь.`,
`Рассмотрим пример разговора о резервных копиях и проверке восстановления.
Пользователь импортирует готовый диалог.
Система выделяет полезное знание, находит заметку о резервном копировании и предлагает добавить раздел.
Пользователь проверяет план.
После одобрения система сама пишет текст, сохраняет изменения и проверяет результат.`,
`Это макет интерфейса.
Слева видны знание и фрагмент диалога, справа находится план изменений.
Пользователь может одобрить план, убрать действие или отказаться.
Окончательный текст система создаёт после одобрения.
По отдельной настройке создание новых заметок с низким риском может проходить автоматически.`,
`Без приложения человек сам перечитывает разговор, ищет нужную заметку и переносит информацию.
Наша система выполняет эту работу и добавляет связи.
Пользователь загружает диалог и при необходимости проверяет план.
Поэтому мы ожидаем, что сохранение знаний займёт меньше времени.`,
`Чтобы проверить пользу, мы сравним ручной способ и наш интерфейс.
Измерим время и проверим качество заметок: нет ли пропусков, повторов и неверных связей.
Позже попросим участников найти сохранённое знание.
Это план проверки, готовых результатов пока нет.`,
`Спасибо за внимание!
Готовы ответить на ваши вопросы.`
];
const sources=[
'README.md; docs/requirements.md, разделы 1–3.',
'docs/requirements.md, разделы 1–2; README.md. Группы пользователей являются гипотезой проекта.',
'docs/requirements.md, US-2, US-3, US-7 и сценарий 9; docs/agent-workflow.md, шаги 2–5.',
'backend/app/prompts/extract/prompt.md; backend/app/prompts/classify/prompt.md; backend/app/prompts/generate/prompt.md; docs/learning/05-knowledge-extraction.md.',
'backend/app/prompts/plan/prompt.md; docs/agent-workflow.md, шаги 5–10; docs/architecture.md, D5.',
'docs/agent-workflow.md, шаги 4–13; docs/architecture.md, D2 и D5; backend/app/agent/policy.py. Пример иллюстративный. Дополнение существующей заметки требует одобрения.',
'docs/agent-workflow.md, шаги 8–13; backend/app/agent/policy.py; frontend/src/components/PlanPanel.vue. По умолчанию подтверждение включено. Автоматический допуск возможен только для соответствующих условиям планов создания новых заметок.',
'docs/architecture.md, D2; docs/agent-workflow.md, шаги 8–13; backend/app/agent/policy.py. Выигрыш во времени является гипотезой.',
'Предлагаемый план исследования. Критерии качества: docs/requirements.md, раздел 6. Ограничения: docs/known-limitations.md, раздел 9.',
''
];
await fs.mkdir(build,{recursive:true});
const counts=notes.map(t=>(t.match(/[\p{L}\p{N}]+(?:[-–][\p{L}\p{N}]+)*/gu)||[]).length);
const total=counts.reduce((a,b)=>a+b,0);
console.log(JSON.stringify({counts,total}));
await fs.writeFile(path.join(build,'speaker-notes.json'),JSON.stringify({notes,counts,total},null,2));
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(workspaceDir,'presentation/AI_Knowledge_Agent_RU_Final_10slides.pptx')));
for(let i=0;i<10;i++)p.slides.items[i].speakerNotes.textFrame.setText(notes[i]+(sources[i]?'\n\nИсточники и уточнения (не читать вслух):\n'+sources[i]:''));
const candidatePath=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(workspaceDir,'presentation/AI_Knowledge_Agent_RU_5min.pptx');
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath,pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','5','--require-native-table-slide','8'],explicitTotalSlideCount:10,requiredNativeTableOwnerSlides:[5,8],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify({finalPath:result.finalPath,sha256:result.finalSha256,layoutFindings:result.presentationLayout.findingCount}));
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
const comparisons=[];
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(let i=0;i<10;i++){
 const png=await final.export({slide:final.slides.items[i],format:'png',scale:1});
 const bytes=new Uint8Array(await png.arrayBuffer());
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),bytes);
 const previous=await fs.readFile(path.join(workspaceDir,`.pptx-build-ru/roles-and-thanks/slide-${i+1}.png`));
 comparisons.push({slide:i+1,unchanged:hash(bytes)===hash(previous)});
 console.log(`Rendered ${i+1}, unchanged: ${comparisons.at(-1).unchanged}`);
}
await fs.writeFile(path.join(build,'visual-comparison.json'),JSON.stringify(comparisons,null,2));
if(comparisons.some(s=>!s.unchanged))throw new Error('Slide visuals changed; review required.');
