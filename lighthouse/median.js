// node median.js <dir> <name> <runs>: logs per-run metrics to runs.csv, keeps the median-score report as <name>.json
const fs = require('fs');
const [d, n, k] = process.argv.slice(2);
const files = [...Array(+k).keys()].map(i => `${d}/${n}-${i + 1}.json`).filter(f => fs.existsSync(f));
const runs = files.map(f => {
  const r = JSON.parse(fs.readFileSync(f)); const a = r.audits;
  return { f, score: r.categories.performance.score, row: [n, Math.round(r.categories.performance.score * 100),
    ...['first-contentful-paint', 'largest-contentful-paint', 'total-blocking-time', 'speed-index'].map(x => Math.round(a[x].numericValue))].join(',') };
});
fs.appendFileSync(`${d}/runs.csv`, runs.map(r => r.row).join('\n') + '\n');
runs.sort((a, b) => a.score - b.score);
fs.copyFileSync(runs[Math.floor(runs.length / 2)].f, `${d}/${n}.json`);
runs.forEach(r => fs.unlinkSync(r.f));
console.log(n, runs.map(r => r.score));
