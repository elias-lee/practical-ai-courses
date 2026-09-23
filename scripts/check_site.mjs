// End-to-end check of the BUILT site in headless Chrome, exactly as colleagues open it:
// via file:// with all network access blocked.
//
// Usage: node scripts/check_site.mjs [site-dir]      (default: site)
// Screenshots go to .checks/. Exits non-zero if any check fails.
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { inflateSync } from "node:zlib";

const ROOT = resolve(new URL("..", import.meta.url).pathname);
const SITE = resolve(ROOT, process.argv[2] || "site");
const OUT = join(ROOT, ".checks");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9333;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, "--window-size=1280,900",
  `--user-data-dir=${mkdtempSync(join(tmpdir(), "cdp-"))}`, "about:blank",
], { stdio: "ignore" });

// Chrome can take a while to start on CI runners: wait up to 30 s for a page target.
let pageTarget;
for (let i = 0; i < 150 && !pageTarget; i++) {
  try { pageTarget = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).find((t) => t.type === "page"); } catch {}
  if (!pageTarget) await sleep(200);
}
if (!pageTarget) { console.error(`Chrome did not start (${CHROME})`); chrome.kill(); process.exit(1); }
const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));

let seq = 0;
const pending = new Map();
const errors = [];
ws.addEventListener("message", (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  if (msg.method === "Runtime.exceptionThrown") errors.push(msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text);
  if (msg.method === "Log.entryAdded" && msg.params.entry.level === "error") errors.push(`${msg.params.entry.text} ${msg.params.entry.url || ""}`);
});
const send = (method, params = {}) => new Promise((r) => { const i = ++seq; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evaluate = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.result.value;
const shot = async (name, clip) => {
  const r = await send("Page.captureScreenshot", { format: "png", ...(clip ? { clip } : {}) });
  writeFileSync(join(OUT, name), Buffer.from(r.result.data, "base64"));
};
const go = async (path) => { await send("Page.navigate", { url: `file://${SITE}/${path}` }); await sleep(1500); };

await send("Page.enable"); await send("Runtime.enable"); await send("Log.enable"); await send("Network.enable");
// Fail every real network request. (Network.setBlockedURLs is unusable here: its "http://*"
// pattern also matches inside data: URLs, e.g. the xmlns of every inline SVG icon.)
const networkRequests = [];
ws.addEventListener("message", (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.method === "Fetch.requestPaused") {
    networkRequests.push(msg.params.request.url);
    send("Fetch.failRequest", { requestId: msg.params.requestId, errorReason: "InternetDisconnected" });
  }
});
await send("Fetch.enable", { patterns: [{ urlPattern: "http://*" }, { urlPattern: "https://*" }] });

const failures = [];
const check = (name, ok, detail) => { console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail !== undefined ? `  (${JSON.stringify(detail)})` : ""}`); if (!ok) failures.push(name); };

// Decode an 8-bit RGB/RGBA non-interlaced PNG (what Chrome produces) into raw pixels.
function decodePng(buf) {
  let pos = 8, width, height, channels, idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos), type = buf.toString("ascii", pos + 4, pos + 8), data = buf.subarray(pos + 8, pos + 8 + len);
    if (type === "IHDR") { width = data.readUInt32BE(0); height = data.readUInt32BE(4); channels = data[9] === 6 ? 4 : 3; }
    if (type === "IDAT") idat.push(data);
    pos += 12 + len;
  }
  const raw = inflateSync(Buffer.concat(idat)), stride = width * channels, px = Buffer.alloc(height * stride);
  for (let y = 0; y < height; y++) {
    const f = raw[y * (stride + 1)], line = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    for (let x = 0; x < stride; x++) {
      const a = x >= channels ? px[y * stride + x - channels] : 0, b = y ? px[(y - 1) * stride + x] : 0;
      const c = x >= channels && y ? px[(y - 1) * stride + x - channels] : 0;
      const pred = f === 1 ? a : f === 2 ? b : f === 3 ? (a + b) >> 1 : f === 4 ? paeth(a, b, c) : 0;
      px[y * stride + x] = (line[x] + pred) & 255;
    }
  }
  return { width, height, channels, px };
}
function paeth(a, b, c) { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c); return pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }

// Is the ::before icon of `selector` painted? Screenshot its box and count saturated pixels
// (icons are coloured; titles are dark text on a pale background).
async function iconPainted(selector, file) {
  const box = await evaluate(`(() => {
    const el = document.querySelector(${JSON.stringify(selector)});
    el.scrollIntoView({ block: 'center' });
    const t = el.getBoundingClientRect();
    // Screenshot clips are in page coordinates, not viewport coordinates.
    return { x: t.x + scrollX, y: t.y + scrollY, width: 48, height: t.height, scale: 1 };
  })()`);
  await sleep(200);
  const r = await send("Page.captureScreenshot", { format: "png", clip: box });
  const png = Buffer.from(r.result.data, "base64");
  writeFileSync(join(OUT, file), png);
  const { px, channels } = decodePng(png);
  let saturated = 0;
  for (let i = 0; i < px.length; i += channels) {
    const max = Math.max(px[i], px[i + 1], px[i + 2]), min = Math.min(px[i], px[i + 1], px[i + 2]);
    if (max - min > 120) saturated++;
  }
  const style = await evaluate(`(() => {
    const s = getComputedStyle(document.querySelector(${JSON.stringify(selector)}), '::before');
    return { mask: s.maskImage.slice(0, 30), bgColor: s.backgroundColor, size: s.width + 'x' + s.height };
  })()`);
  return { saturated, style };
}

// ---- Home
await go("index.html");
await shot("home.png");
check("home renders path cards", (await evaluate(`document.querySelectorAll('.path-card').length`)) === 2);

// ---- Literacy C3: quiz, copy buttons, sidebars, completion
await go("literacy/c3.html");
const c3 = await evaluate(`(() => {
  const q = document.querySelector('.quiz-q');
  const wrong = q.querySelector('.quiz-option[data-correct="false"]');
  wrong.click();
  const r = {
    questions: document.querySelectorAll('.quiz-q').length,
    wrongMarked: wrong.classList.contains('is-wrong'),
    answerMarked: !!q.querySelector('.quiz-option.is-answer'),
    whysShown: [...q.querySelectorAll('.quiz-why')].every(w => !w.hidden),
    locked: [...q.querySelectorAll('.quiz-option')].every(b => b.disabled),
    score: document.querySelector('.quiz-score').textContent,
    copyButtons: document.querySelectorAll('.md-code__button, button.md-clipboard').length,
    codeBlocks: document.querySelectorAll('pre > code').length,
    sidebars: document.querySelectorAll('details.info').length,
  };
  q.scrollIntoView({ block: 'start' });
  return r;
})()`);
check("c3 quiz marks wrong + correct answers", c3.wrongMarked && c3.answerMarked && c3.locked, c3);
check("c3 quiz reveals all explanations", c3.whysShown);
check("c3 quiz score updates", c3.score === `1 / ${c3.questions} answered · 0 correct`, c3.score);
check("c3 every code block has a copy button", c3.copyButtons >= c3.codeBlocks && c3.codeBlocks > 0, [c3.copyButtons, c3.codeBlocks]);
await sleep(300);
await shot("c3-quiz.png");
const done = await evaluate(`(() => { document.querySelector('.complete-btn').click(); return localStorage.getItem('aicourse:done:literacy/c3.html'); })()`);
check("c3 mark-complete stores progress", done === "1");

// ---- Icons (CSS masks) must paint under file://
const admonitionIcon = await iconPainted(".admonition.abstract > .admonition-title", "icon-admonition.png");
check("admonition icons paint under file://", admonitionIcon.saturated > 20, admonitionIcon);
const sidebarIcon = await iconPainted("details.info > summary", "icon-sidebar.png");
check("sidebar icons paint under file://", sidebarIcon.saturated > 20, sidebarIcon);

// ---- Course hub shows progress
await go("literacy/index.html");
check("hub shows completion badge", (await evaluate(`document.querySelector('[data-progress-for="literacy/c3.html"]').textContent`)) === "✓ done");

// ---- Offline search
const search = await evaluate(`(async () => {
  const input = document.querySelector('.md-search__input');
  document.querySelector('label[for="__search"]').click();
  input.focus(); input.value = 'orchestrator';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
  await new Promise(r => setTimeout(r, 2500));
  return document.querySelectorAll('.md-search-result__item').length;
})()`);
check("offline search returns results", search > 0, search);
await shot("search.png");

// ---- Engineering C6
await go("engineering/c6.html");
await shot("c6-top.png");
const c6 = await evaluate(`({ questions: document.querySelectorAll('.quiz-q').length, sidebars: document.querySelectorAll('details.info').length, diagram: document.querySelector('.diagram img')?.naturalWidth > 0 })`);
check("c6 quiz, sidebars and diagram present", c6.questions > 0 && c6.sidebars > 0 && c6.diagram, c6);

// ---- Every class page: quiz rendered, sidebars resolved, completion button present
const PAGES = [
  ...[1, 2, 3, 4, 5, 6, 7, 8].map((n) => `literacy/c${n}.html`),
  "engineering/prework.html",
  ...[1, 2, 3, 4, 5, 6, 7, 8].map((n) => `engineering/c${n}.html`),
];
const pageProblems = [];
for (const path of PAGES) {
  await go(path);
  const p = await evaluate(`({
    quiz: document.querySelectorAll('.quiz-q').length,
    unresolved: document.body.innerText.includes('--8<--') || document.body.innerHTML.includes('<!-- quiz:'),
    toggle: !!document.querySelector('.complete-btn'),
    img: [...document.querySelectorAll('article img')].every(i => i.complete && i.naturalWidth > 0),
  })`);
  const needsQuiz = !path.includes("prework");
  if ((needsQuiz && p.quiz === 0) || p.unresolved || !p.toggle || !p.img) pageProblems.push({ path, ...p });
}
check(`all ${PAGES.length} class pages complete (quiz, sidebars, images, completion button)`, pageProblems.length === 0, pageProblems);

check("no JavaScript or resource errors", errors.length === 0, errors);
check("site makes no network requests", networkRequests.length === 0, networkRequests);

ws.close();
chrome.kill();
console.log(failures.length ? `\n${failures.length} check(s) failed. Screenshots in .checks/` : "\nAll checks passed. Screenshots in .checks/");
process.exit(failures.length ? 1 : 0);
