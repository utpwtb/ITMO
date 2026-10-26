(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const chapters = $$('.chapter');
  const units = $$('[data-search-unit]');
  const storageKey = 'is-defense-zh-ru-v1';
  let state = {language:'both', study:'full', learned:[]};
  try { const saved = JSON.parse(localStorage.getItem(storageKey) || 'null'); if (saved && typeof saved === 'object') state = {...state,...saved}; } catch (_) {}
  if (!['both','zh','ru'].includes(state.language)) state.language = 'both';
  if (!['full','recite'].includes(state.study)) state.study = 'full';
  if (!Array.isArray(state.learned)) state.learned = [];
  state.learned = [...new Set(state.learned.filter(id => chapters.some(c => c.id === id)))];
  const save = () => {try {localStorage.setItem(storageKey, JSON.stringify(state));} catch (_) {}};
  const bilingual = (zh,ru) => state.language === 'zh' ? zh : state.language === 'ru' ? ru : `${zh} / ${ru}`;
  let toastTimer;
  function toast(text) { const t = $('#toast'); t.textContent = text; t.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => t.hidden = true, 2600); }
  function refreshState() {
    document.body.dataset.language = state.language;
    document.documentElement.lang = state.language === 'ru' ? 'ru' : 'zh-CN';
    document.body.dataset.study = state.study;
    $$('[data-lang-choice]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.langChoice === state.language)));
    $('#review-toggle').setAttribute('aria-pressed',String(state.study === 'recite'));
    $('#search').placeholder = bilingual('搜索概念或问题','Поиск понятия или вопроса');
    $('#search').setAttribute('aria-label',bilingual('搜索学习资料','Поиск по материалам'));
    chapters.forEach(chapter => {
      const learned = state.learned.includes(chapter.id);
      const btn = $('.learn-button',chapter);
      btn.setAttribute('aria-pressed',String(learned));
      $('.lang-zh',btn).textContent = learned ? '✓ 已掌握' : '○ 标记掌握';
      $('.lang-ru',btn).textContent = learned ? '✓ Освоено' : '○ Отметить';
    });
    $('#progress-label').textContent = bilingual(`已掌握 ${state.learned.length} / 9 题`,`Освоено ${state.learned.length} / 9 тем`);
    $('#progress-bar').style.width = `${state.learned.length / 9 * 100}%`;
    $('#progress-track').setAttribute('aria-valuenow',String(state.learned.length));
    updateTopHeight();
  }
  function updateTopHeight(){ document.documentElement.style.setProperty('--top',`${Math.ceil($('.topbar').getBoundingClientRect().height)}px`); }
  $$('[data-lang-choice]').forEach(b => b.addEventListener('click',() => {state.language=b.dataset.langChoice;refreshState();runSearch();save();}));
  $('#review-toggle').addEventListener('click',() => {state.study = state.study === 'full' ? 'recite' : 'full';refreshState();save();});
  $$('.learn-button').forEach(b => b.addEventListener('click',() => { const id=b.closest('.chapter').id;state.learned=state.learned.includes(id) ? state.learned.filter(x=>x!==id) : [...state.learned,id];refreshState();save(); }));
  units.forEach(u => u.dataset.searchText = u.textContent.toLocaleLowerCase());
  function runSearch(){
    const value=$('#search').value.trim().toLocaleLowerCase();
    const words=value.split(/\s+/).filter(Boolean);
    let hits=0;
    units.forEach(u=>{const show=!words.length || words.every(w=>u.dataset.searchText.includes(w));u.hidden=!show;if(show)hits++;});
    $('#hero').hidden=!!value;
    $('#empty').hidden=!value || hits>0;
    $('#search-status').hidden=!value;
    $('#search-status').textContent=bilingual(`找到 ${hits} 个相关章节；在章节内使用浏览器查找可定位原文。`,`Найдено разделов: ${hits}. Для поиска внутри раздела используйте поиск браузера.`);
    $('#clear-search').hidden=!value;
    $$('.toc a').forEach(a=>{const target=document.getElementById(a.hash.slice(1));a.hidden=!!target?.hidden;});
    $$('#chapter-select option').forEach(o=>{if(o.value)o.hidden=!!document.getElementById(o.value)?.hidden;});
  }
  $('#search').addEventListener('input',runSearch);
  $('#clear-search').addEventListener('click',()=>{$('#search').value='';runSearch();$('#search').focus();});
  function navigate(id){const target=document.getElementById(id);if(!target)return;if(target.hidden){$('#search').value='';runSearch();}target.scrollIntoView({block:'start'});history.replaceState(null,'',`#${id}`);}
  $('#chapter-select').addEventListener('change',e=>{if(e.target.value)navigate(e.target.value);});
  $$('.toc a').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();navigate(a.hash.slice(1));}));
  $('#back-top').addEventListener('click',()=>window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
  let observer;
  if ('IntersectionObserver' in window){observer = new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){$$('.toc a').forEach(a=>a.classList.toggle('active',a.hash===`#${entry.target.id}`));$('#chapter-select').value=entry.target.id;}}},{rootMargin:'-15% 0px -70% 0px'});units.forEach(u=>observer.observe(u));}
  $$('.copy-btn').forEach(b=>b.addEventListener('click',async()=>{const code=$('pre',b.closest('.code-box')).textContent;try{await navigator.clipboard.writeText(code);toast(bilingual('代码已复制','Код скопирован'));}catch(_){const sel=window.getSelection();const range=document.createRange();range.selectNodeContents($('pre',b.closest('.code-box')));sel.removeAllRanges();sel.addRange(range);toast(bilingual('已选中代码，可手动复制','Код выделен: скопируйте вручную'));}}));
  const deck = JSON.parse($('#drill-data').textContent);
  let bag=[], current;
  function pEl(p){const wrap=document.createElement('div');wrap.className='pair';[['zh','zh-CN'],['ru','ru']].forEach(([k,lang])=>{const span=document.createElement('div');span.className=`lang lang-${k}`;span.lang=lang;span.textContent=p[k];wrap.append(span);});return wrap;}
  function nextQuestion(){if(!bag.length){bag=deck.map((_,i)=>i);for(let i=bag.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[bag[i],bag[j]]=[bag[j],bag[i]];}if(bag.length>1&&bag[bag.length-1]===current)[bag[bag.length-1],bag[0]]=[bag[0],bag[bag.length-1]];}current=bag.pop();const item=deck[current];$('#drill-meta').replaceChildren(pEl(item.topic));$('#drill-question').replaceChildren(pEl(item.q));$('#drill-answer').replaceChildren(pEl(item.a));$('#drill-answer').hidden=true;$('#reveal-answer').setAttribute('aria-expanded','false');$('#drill-position').textContent=bilingual(`本轮剩余 ${bag.length} 题`,`Осталось в раунде: ${bag.length}`);}
  $('#next-question').addEventListener('click',nextQuestion);
  $('#reveal-answer').addEventListener('click',()=>{const answer=$('#drill-answer');answer.hidden=!answer.hidden;$('#reveal-answer').setAttribute('aria-expanded',String(!answer.hidden));});
  let printSnapshot;
  function beforePrint(){if(printSnapshot)return;printSnapshot={search:$('#search').value,units:units.map(x=>x.hidden),hero:$('#hero').hidden,details:$$('details').map(d=>d.open)};units.forEach(x=>x.hidden=false);$('#hero').hidden=false;$$('details').forEach(d=>d.open=true);}
  function afterPrint(){if(!printSnapshot)return;units.forEach((x,i)=>x.hidden=printSnapshot.units[i]);$('#hero').hidden=printSnapshot.hero;$$('details').forEach((d,i)=>d.open=printSnapshot.details[i]);printSnapshot=null;}
  window.addEventListener('beforeprint',beforePrint);window.addEventListener('afterprint',afterPrint);
  $('#print-guide').addEventListener('click',()=>window.print());
  window.addEventListener('resize',updateTopHeight);
  refreshState();nextQuestion();
  if(location.hash){const id=decodeURIComponent(location.hash.slice(1));if(document.getElementById(id))setTimeout(()=>navigate(id),80);}
})();
