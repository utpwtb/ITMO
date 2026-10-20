import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('C:/develop/NOTE_UTP/StudyNote/5 User Interface Design/Task/Task1/presentation/AI_Knowledge_Agent_RU_20260920.pptx'));
console.log((await p.inspect({kind:'slide,table',maxChars:16000})).ndjson);
console.log(p.help('shapes',{search:'delete',include:['index','notes'],maxChars:4000}));
console.log('SHAPES PROTOTYPE',Object.getOwnPropertyNames(Object.getPrototypeOf(p.slides.items[5].shapes)));
console.log('SHAPE PROTOTYPE',Object.getOwnPropertyNames(Object.getPrototypeOf(p.slides.items[5].shapes.items[0])));
await fs.writeFile('C:/develop/NOTE_UTP/StudyNote/5 User Interface Design/Task/Task1/.pptx-build-ru/source-edit-inspect.ndjson',(await p.inspect({kind:'slide,shape,textbox,table',maxChars:100000})).ndjson);
