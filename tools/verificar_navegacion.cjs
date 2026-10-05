const { chromium } = require('C:/Users/GIGAPOBLA/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
 const browser = await chromium.launch({headless:true,channel:"msedge"});
 const page = await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 for(const width of [1440,390]) {
  await page.setViewportSize({width,height:1000});
  for(const route of ['/','/productos/','/empresa/','/servicios/','/proyectos/','/contacto/']) {
   const response=await page.goto('http://127.0.0.1:8000'+route,{waitUntil:'domcontentloaded'});
   console.log(width,route,response.status(),await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth})));
   if(route==='/' || route==='/productos/') await page.screenshot({path:'tools/referencias/revision-'+(route==='/'?'inicio':'productos')+'-'+width+'.png',fullPage:false});
  }
  await page.goto('http://127.0.0.1:8000/');
  if(width===390) await page.locator('.menu-toggle').click();
  await page.locator('.nav-branch summary').first().click();
  console.log('Construcciones visible',await page.locator('.nav-submenu').first().isVisible());
  await page.keyboard.press('Escape');
  console.log('Cierre con Escape',!(await page.locator('.nav-branch details').first().getAttribute('open')!==null));
 }
 await page.goto('http://127.0.0.1:8000/productos/?q=noexiste123&marca=invalid');
 console.log('Sin resultados',await page.locator('.catalog-empty').isVisible());
 await page.goto('http://127.0.0.1:8000/contacto/?servicio=Productos');
 console.log('Cotización productos',await page.locator('select[name=servicio]').inputValue());
 console.log('JS errors',errors);
 await browser.close();
})();

