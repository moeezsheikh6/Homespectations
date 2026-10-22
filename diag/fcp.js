// Measures first-contentful-paint on the live site with different request groups blocked.
const { chromium, devices } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'https://homespectations.pk/collections/beds';
const variants = {
  normal: [],
  noAppExt: [/cdn\.shopify\.com\/extensions/],
  noTracking: [/facebook|googletagmanager|google-analytics|merchant-center|carthike|web-pixels|\/wpm\//],
  noFonts: [/\/cdn\/fonts\//],
  noThemeJs: [/\/assets\/.*\.js/],
};
(async () => {
  const browser = await chromium.launch();
  const out = [];
  for (let round = 0; round < 6; round++) {
    for (const [name, pats] of Object.entries(variants)) {
      const ctx = await browser.newContext({ ...devices['Moto G4'] });
      const page = await ctx.newPage();
      if (pats.length) await page.route('**/*', r => pats.some(p => p.test(r.request().url())) ? r.abort() : r.continue());
      const t0 = Date.now();
      await page.goto(URL, { waitUntil: 'load', timeout: 60000 }).catch(e => {});
      await page.waitForTimeout(3500);
      const m = await page.evaluate(() => {
        const p = performance.getEntriesByType('paint').find(e => e.name === 'first-contentful-paint');
        const n = performance.getEntriesByType('navigation')[0];
        return { fcp: p ? Math.round(p.startTime) : null, dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd) };
      });
      out.push([name, round, m.fcp, m.dcl, m.load].join(','));
      console.log(name, round, JSON.stringify(m));
      await ctx.close();
    }
  }
  fs.writeFileSync('diag/fcp.csv', 'variant,round,fcp,dcl,load\n' + out.join('\n') + '\n');
  await browser.close();
})();
