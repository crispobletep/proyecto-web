const { chromium } = require('C:/Users/GIGAPOBLA/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1365,height:900}});
 await page.goto('http://127.0.0.1:8000/productos/');
 const brands=await page.locator('#catalog-brand-filter option').evaluateAll(options=>options.filter(o=>o.value).map(o=>({id:o.value,name:o.textContent})));
 for(const brand of brands){
  await page.goto('http://127.0.0.1:8000/productos/');
  await Promise.all([page.waitForURL(url=>url.searchParams.get('marca')===brand.id),page.locator('#catalog-brand-filter').selectOption(brand.id)]);
  const cards=await page.locator('.catalog-brand').allTextContents();
  if(!cards.length || cards.some(text=>text.trim()!==brand.name)) throw new Error('Marca incorrecta: '+brand.name+JSON.stringify(cards));
  console.log(brand.name+': '+cards.length+' fichas verificadas en la página');
 }
 await page.goto('http://127.0.0.1:8000/productos/?marca=1');
 const family=page.locator('.catalog-filter-links details').first();
 await family.locator('summary').click();
 await family.getByRole('link',{name:'Ver todos',exact:true}).click();
 if(new URL(page.url()).searchParams.get('marca')!=='1') throw new Error('Se perdió la marca');
 console.log('Familia conserva la marca; Ver todos visible');
 console.log('Opciones en familia:',await page.locator('#catalog-brand-filter option').allTextContents());
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
