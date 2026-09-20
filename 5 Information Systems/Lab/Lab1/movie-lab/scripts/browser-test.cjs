/* Runs on the deployed application; creates and then removes its own test data. */
const {chromium, request}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');
const path=require('node:path');
const base=process.env.MOVIE_BASE_URL||'http://127.0.0.1:18081/movie-lab/';
const out=path.resolve(__dirname,'../../verification');fs.mkdirSync(out,{recursive:true});
const results=[];
function check(name,condition){results.push({name,passed:!!condition});if(!condition)throw Error(name);console.log('PASS '+name);}
(async()=>{
 const client=await request.newContext({baseURL:base});let browser,coordinate;
 try{
  check('Unauthenticated API is rejected',(await client.get('api/movies')).status()===401);
  check('Wrong password is rejected',(await client.post('api/auth',{data:{username:'student',password:'wrong'}})).status()===401);
  const auth=await client.post('api/auth',{data:{username:process.env.MOVIE_USER||'student',password:process.env.MOVIE_PASSWORD||'student'}});const session=await auth.json();check('Login returns CSRF token',auth.ok()&&!!session.csrf);
  const headers={'X-CSRF-Token':session.csrf};
  check('Mutation without CSRF is rejected',(await client.post('api/coordinates',{data:{x:1,y:2}})).status()===403);
  const c=await client.post('api/coordinates',{headers,data:{x:826,y:42}});coordinate=await c.json();check('Create coordinates',c.status()===201&&!!coordinate.id);
  const invalid=await client.post('api/movies',{headers,data:{name:'',coordinates:coordinate.id,oscarsCount:0}});check('Invalid movie yields informative error',invalid.status()===400&&(await invalid.json()).error.includes('name'));
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  const contextA=await browser.newContext({viewport:{width:1500,height:1000}}),contextB=await browser.newContext({viewport:{width:1500,height:1000}});
  const a=await contextA.newPage(),b=await contextB.newPage();const errors=[];a.on('pageerror',e=>errors.push(e.message));b.on('pageerror',e=>errors.push(e.message));
  async function login(page){await page.goto(base);await page.locator('[name=username]').fill(process.env.MOVIE_USER||'student');await page.locator('[name=password]').fill(process.env.MOVIE_PASSWORD||'student');await page.getByRole('button',{name:'Войти',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});}
  await login(a);await login(b);
  const name='Проверка UI '+Date.now();await a.locator('#create').click();await a.locator('#editor').waitFor({state:'visible'});
  const form=a.locator('#edit-form');await form.locator('[name=name]').fill(name);await form.locator('[name=coordinates]').selectOption(String(coordinate.id));await form.locator('[name=oscarsCount]').fill('5');await form.locator('[name=budget]').fill('9223372036854775807');await form.locator('[name=mpaaRating]').selectOption('PG_13');await form.locator('[name=length]').fill('121');await form.locator('[name=usaBoxOffice]').fill('100');await form.locator('[name=tagline]').fill('Проверка %_');await form.locator('[name=genre]').selectOption('HORROR');await a.locator('#save').click();await a.locator('#editor').waitFor({state:'hidden'});
  await b.getByRole('cell',{name,exact:true}).waitFor({state:'visible',timeout:12000});check('Second authenticated browser receives create automatically',true);
  const movies=await (await client.get('api/movies?filter=name&value='+encodeURIComponent(name))).json();const movie=movies.items[0];check('Full int64 budget survives browser/API round trip',movie.budget==='9223372036854775807');
  await a.getByRole('row').filter({has:a.getByRole('cell',{name,exact:true})}).getByRole('button',{name:'Открыть',exact:true}).click();await a.locator('#details').waitFor({state:'visible'});check('Details display related coordinates',(await a.locator('#detail-content').innerText()).includes('826'));await a.screenshot({path:path.join(out,'ui-details.png'),fullPage:true});await a.locator('[data-close=details]').click();
  await b.getByRole('row').filter({has:b.getByRole('cell',{name,exact:true})}).getByRole('button',{name:'Изменить',exact:true}).click();
  const update=await client.put('api/movies/'+movie.id,{headers,data:{version:movie.version,name:name+' изменён'}});check('HTTP update succeeds',update.ok());
  await b.locator('#edit-form [name=name]').fill(name+' устаревший');await b.locator('#save').click();await b.locator('#edit-error').getByText('Объект изменён другим пользователем.',{exact:false}).waitFor({state:'visible'});check('Stale browser edit rejected without losing form input',await b.locator('#editor').isVisible());await b.locator('[data-close=editor]').click();
  await b.getByRole('cell',{name:name+' изменён',exact:true}).waitFor({state:'visible',timeout:12000});check('Second browser receives update automatically',true);
  await a.screenshot({path:path.join(out,'ui-table.png'),fullPage:true});
  await a.locator('[data-view=operations]').click();await a.locator('[data-operation=average] button').click();await a.locator('#operation-result').getByText('Среднее:',{exact:false}).waitFor();check('Special operations interface works',true);await a.screenshot({path:path.join(out,'ui-operations.png'),fullPage:true});
  const current=await (await client.get('api/movies/'+movie.id)).json();check('Delete movie succeeds',(await client.delete('api/movies/'+movie.id+'?version='+current.version,{headers})).ok());await b.getByRole('cell',{name:name+' изменён',exact:true}).waitFor({state:'hidden',timeout:12000});check('Second browser receives delete automatically',true);
  check('No browser JavaScript errors',errors.length===0);
  await client.delete('api/coordinates/'+coordinate.id+'?version='+coordinate.version,{headers});coordinate=null;
  await contextA.close();await contextB.close();
 }finally{if(browser)await browser.close();await client.dispose();fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify({date:new Date().toISOString(),results},null,2));}
})().catch(e=>{console.error(e);process.exitCode=1;});
