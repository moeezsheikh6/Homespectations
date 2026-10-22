// Usage: node summarize.js report.json  -> prints a compact summary
const fs = require('fs');
const r = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const a = r.audits;
const ms = id => a[id] && a[id].numericValue != null ? Math.round(a[id].numericValue) : null;
const out = {
  url: r.finalDisplayedUrl,
  score: Math.round(r.categories.performance.score * 100),
  FCP: ms('first-contentful-paint'), LCP: ms('largest-contentful-paint'), TBT: ms('total-blocking-time'),
  CLS: a['cumulative-layout-shift'].numericValue.toFixed(3), SI: ms('speed-index'), TTFB: ms('server-response-time'),
  totalKB: Math.round(a['total-byte-weight'].numericValue / 1024),
  requests: (a['network-requests'].details.items || []).length,
  domSize: ms('dom-size'),
  lcpElement: (((a['largest-contentful-paint-element'] || {}).details || {}).items || []).map(i => JSON.stringify(i).slice(0, 400)),
  mainThreadBreakdown: ((a['mainthread-work-breakdown'].details || {}).items || []).map(i => `${i.groupLabel}: ${Math.round(i.duration)}ms`),
  thirdParties: ((a['third-party-summary'].details || {}).items || []).map(i => `${i.entity && i.entity.text || i.entity}: ${Math.round(i.transferSize/1024)}KB, main-thread ${Math.round(i.mainThreadTime)}ms, blocking ${Math.round(i.blockingTime)}ms`),
  renderBlocking: ((a['render-blocking-resources'].details || {}).items || []).map(i => `${i.url} ${Math.round(i.totalBytes/1024)}KB ${Math.round(i.wastedMs)}ms`),
  bootupTime: ((a['bootup-time'].details || {}).items || []).slice(0, 15).map(i => `${i.url}: total ${Math.round(i.total)}ms script ${Math.round(i.scripting)}ms`),
  unusedJS: ((a['unused-javascript'].details || {}).items || []).slice(0, 15).map(i => `${i.url}: ${Math.round(i.wastedBytes/1024)}KB unused of ${Math.round(i.totalBytes/1024)}KB`),
  unusedCSS: ((a['unused-css-rules'].details || {}).items || []).slice(0, 10).map(i => `${i.url}: ${Math.round(i.wastedBytes/1024)}KB unused of ${Math.round(i.totalBytes/1024)}KB`),
  images: ['uses-responsive-images', 'offscreen-images', 'modern-image-formats', 'uses-optimized-images'].map(id => `${id}: ${Math.round(((a[id] || {}).details || {}).overallSavingsBytes / 1024 || 0)}KB`),
  imageItems: ((a['uses-responsive-images'].details || {}).items || []).slice(0, 10).map(i => `${i.url} ${Math.round(i.totalBytes/1024)}KB waste ${Math.round(i.wastedBytes/1024)}KB`),
  offscreen: ((a['offscreen-images'].details || {}).items || []).slice(0, 10).map(i => `${i.url} ${Math.round(i.totalBytes/1024)}KB`),
  biggest: (a['network-requests'].details.items || []).sort((x, y) => y.transferSize - x.transferSize).slice(0, 25).map(i => `${Math.round(i.transferSize/1024)}KB ${i.resourceType} ${i.url.slice(0, 160)}`),
  fonts: ((a['font-display'].details || {}).items || []).map(i => i.url),
  lcpPhases: (((a['lcp-breakdown-insight'] || a['largest-contentful-paint-element'] || {}).details || {}).items || []).map(i => JSON.stringify(i).slice(0, 600)),
};
console.log(JSON.stringify(out, null, 1));
