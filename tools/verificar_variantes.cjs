const {chromium}=require('C:/Users/GIGAPOBLA/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
const b=await chromium.launch({channel:'msedge',headless:true});const p=await b.newPage({reducedMotion:'reduce'});let errors=[];p.on('pageerror',e=>errors.push(e.message));
for(const width of [1440,390]){
 await p.setViewportSize({width,height:1000});await p.goto('http://127.0.0.1:8000/productos/?marca=1');
 const c=p.locator('.catalog-card').filter({has:p.locator('.catalog-variant-select')}).first();
 const thumbs=c.locator('.catalog-thumb[data-variant-id]');const last=thumbs.last();const id=await last.getAttribute('data-variant-id');
 await last.click();
 const variant=c.locator('.catalog-variant-card[data-variant-id="'+id+'"]');
 if(!(await variant.getAttribute('class')).includes('selected'))throw Error('No seleccionó variante');
 if(await last.getAttribute('aria-pressed')!=='true')throw Error('Estado lateral incorrecto');
 const visible=await variant.evaluate(el=>{let a=el.getBoundingClientRect(),b=el.parentElement.getBoundingClientRect();return a.left>=b.left-2&&a.right<=b.right+2});
 if(!visible)throw Error('Variante fuera de vista');
 const first=c.locator('.catalog-variant-select').first();await first.focus();await p.keyboard.press('Enter');await p.mouse.move(0,0);
 const firstV=c.locator('.catalog-variant-card').first();const src=await firstV.getAttribute('data-preview-src');
 if(await c.locator('.catalog-main-image').getAttribute('src')!==src)throw Error('No actualizó imagen');
 if(await thumbs.first().getAttribute('aria-pressed')!=='true')throw Error('No sincronizó lateral');
 const railVisible=await thumbs.first().evaluate(el=>{const a=el.getBoundingClientRect(),b=el.parentElement.getBoundingClientRect();return a.left>=b.left-2&&a.right<=b.right+2&&a.top>=b.top-2&&a.bottom<=b.bottom+2});if(!railVisible)throw Error('Miniatura seleccionada fuera de vista');
 await c.screenshot({path:'tools/referencias/variantes-'+width+'.png'});
 console.log(width, 'selección, teclado, scroll e imagen correctos');
}
if(errors.length)throw Error(errors.join(';'));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
