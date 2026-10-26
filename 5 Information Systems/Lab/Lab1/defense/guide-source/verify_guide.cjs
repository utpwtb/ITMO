const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('C:/Users/CHL/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert = require('node:assert/strict');

(async()=>{
  const file = path.resolve(__dirname, '..', '信息系统答辩_中俄双语.html');
  const qa = path.resolve(__dirname, '..', 'verification');
  fs.mkdirSync(qa,{recursive:true});
  const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  const context = await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const page = await context.newPage();
  const errors = [], requests = [];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(!r.url().startsWith('file:'))requests.push(r.url());});
  await page.goto(pathToFileURL(file).href);
  await page.waitForFunction(()=>document.querySelector('#drill-question').textContent.trim().length>0);
  const basics = await page.evaluate(()=>({
    topics:document.querySelectorAll('.chapter').length,
    ids:[...document.querySelectorAll('[id]')].map(x=>x.id),
    links:[...document.querySelectorAll('a[href^="#"]')].map(x=>x.hash.slice(1)),
    pairs:document.querySelectorAll('.pair').length,
    details:document.querySelectorAll('details').length,
    code:document.querySelectorAll('.code-box').length,
    table:document.querySelectorAll('table').length,
    sources:document.querySelectorAll('.sources a').length,
    externalAssets:document.querySelectorAll('script[src],link[rel="stylesheet"],img[src^="http"],iframe').length,
    badPairs:[...document.querySelectorAll('.pair')].filter(x=>!x.querySelector(':scope>.lang-zh')||!x.querySelector(':scope>.lang-ru')).length,
    replacementCharacters:document.body.textContent.includes('\uFFFD'),
  }));
  assert.equal(basics.topics,9);
  assert.equal(basics.ids.length,new Set(basics.ids).size,'IDs must be unique');
  assert.equal(basics.externalAssets,0);
  assert.equal(basics.badPairs,0);
  assert.equal(basics.replacementCharacters,false);
  assert(basics.details>=36);
  for(const id of basics.links)assert(basics.ids.includes(id),`Missing anchor ${id}`);
  const sizes=[];
  for(const [width,height,name] of [[1440,1000,'desktop'],[1024,1024,'tablet-landscape'],[768,1024,'tablet'],[390,844,'phone'],[360,800,'small-phone']]){
    await page.setViewportSize({width,height});
    await page.waitForTimeout(90);
    const layout=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,topbar:document.querySelector('.topbar').getBoundingClientRect().height,offenders:[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();return b.width&&b.right>innerWidth+1&&!e.closest('pre')&&!e.closest('.table-wrap')&&!e.closest('.sidebar')}).map(e=>`${e.tagName}.${e.className}`).slice(0,8)}));
    assert(layout.scrollWidth<=width+1,`${name}: horizontal page overflow ${layout.scrollWidth}`);
    sizes.push({name,...layout});
    if(['desktop','tablet','phone'].includes(name))await page.screenshot({path:path.join(qa,`${name}.png`)});
  }
  await page.setViewportSize({width:390,height:844});
  await page.locator('#chapter-select').selectOption('persistence');
  await page.waitForTimeout(1800);
  await page.screenshot({path:path.join(qa,'phone-persistence.png')});
  const headingPos=await page.locator('#persistence').evaluate(e=>e.getBoundingClientRect().top);
  const topHeight=await page.locator('.topbar').evaluate(e=>e.getBoundingClientRect().bottom);
  assert(headingPos>=topHeight-1,'anchor hidden by sticky controls');
  await page.locator('#chapter-select').selectOption('orm');
  await page.waitForTimeout(300);
  const table = page.locator('#orm table').first();
  await table.scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(qa,'phone-comparison.png')});
  await page.locator('[data-lang-choice="ru"]').click();
  assert.equal(await page.locator('#cdi .chapter-summary>.lang-zh').isVisible(),false);
  assert.equal(await page.locator('#cdi .chapter-summary>.lang-ru').isVisible(),true);
  assert.equal(await page.locator('html').getAttribute('lang'),'ru');
  await page.locator('[data-lang-choice="zh"]').click();
  assert.equal(await page.locator('#cdi .chapter-summary>.lang-ru').isVisible(),false);
  await page.locator('[data-lang-choice="both"]').click();
  await page.locator('#review-toggle').click();
  assert.equal(await page.locator('#orm .full-only').first().isVisible(),false);
  assert.equal(await page.locator('#orm .oral').isVisible(),true);
  await page.locator('#review-toggle').click();
  await page.locator('#search').fill('持久化上下文');
  assert(await page.locator('#persistence').isVisible());
  assert.equal(await page.locator('#hero').isVisible(),false);
  await page.locator('#search').fill('несуществующий-запрос-123');
  assert.equal(await page.locator('#empty').isVisible(),true);
  await page.locator('#clear-search').click();
  assert.equal(await page.locator('#hero').isVisible(),true);
  await page.locator('#search').fill('транзакц');
  assert(await page.locator('.chapter:visible').count()>0);
  await page.locator('#clear-search').click();
  await page.locator('#patterns .learn-button').click();
  assert.equal(await page.locator('#patterns .learn-button').getAttribute('aria-pressed'),'true');
  await page.reload();
  assert.equal(await page.locator('#patterns .learn-button').getAttribute('aria-pressed'),'true');
  const question=page.locator('#cdi details').first();
  await question.locator('summary').click();
  assert(await question.getAttribute('open')!==null);
  const deck = await page.locator('#drill-data').evaluate(e=>JSON.parse(e.textContent));
  const seen = new Set();
  for(let i=0;i<deck.length;i++){
    const q = await page.locator('#drill-question').textContent();
    assert(!seen.has(q),'Question repeated before deck exhausted');
    seen.add(q);
    await page.locator('#reveal-answer').click();
    assert.equal(await page.locator('#drill-answer').isVisible(),true);
    await page.locator('#next-question').click();
    assert.equal(await page.locator('#drill-answer').isVisible(),false);
  }
  await page.locator('#search').fill('Spring Boot');
  await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
  assert.equal(await page.locator('.chapter[hidden]').count(),0);
  assert.equal(await page.locator('details:not([open])').count(),0);
  await page.emulateMedia({media:'print'});
  await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
  await page.waitForTimeout(300);
  assert.equal(await page.locator('.topbar').isVisible(),false);
  await page.screenshot({path:path.join(qa,'print-preview.png')});
  await page.emulateMedia({media:'screen'});
  await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
  assert(await page.locator('.chapter[hidden]').count()>0);
  await page.locator('#clear-search').click();
  await context.close();
  const noJS=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const staticPage=await noJS.newPage();
  await staticPage.goto(pathToFileURL(file).href);
  assert.equal(await staticPage.locator('.chapter').count(),9);
  assert(await staticPage.locator('#persistence .content-block').count()>0);
  const staticLayout=await staticPage.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);
  assert(staticLayout);
  await noJS.close();
  await browser.close();
  assert.deepEqual(errors,[],'Browser exceptions');
  assert.deepEqual(requests,[],'Offline guide made network requests');
  const result={result:'PASS',basics,viewports:sizes,randomQuestionsVerified:seen.size,features:['language-switch','search-zh-ru','recite-mode','progress-persistence','toc-anchor','details','random-deck-no-repeats','print-all-and-restore','no-js-content','offline-no-network'],browserErrors:errors};
  fs.writeFileSync(path.join(qa,'checks.json'),JSON.stringify(result,null,2),'utf8');
  console.log(JSON.stringify(result,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
