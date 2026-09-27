// Design review screenshots of the built site: light and dark, desktop and phone.
// Usage: node scripts/screenshots.mjs [page ...]     (default: a representative set)
// Output: .checks/shots/<page>-<scheme>-<device>.png
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const ROOT = resolve(new URL("..", import.meta.url).pathname);
const SITE = join(ROOT, "site");
const OUT = join(ROOT, ".checks", "shots");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9334;
const PAGES = process.argv.slice(2).length ? process.argv.slice(2) : ["index.html", "literacy/c3.html", "engineering/c6.html"];
const DEVICES = { desktop: { width: 1280, height: 900, mobile: false }, phone: { width: 390, height: 844, mobile: true } };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "shots-"))}`, "about:blank"], { stdio: "ignore" });
let target;
for (let i = 0; i < 150 && !target; i++) {
  try { target = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).find((t) => t.type === "page"); } catch {}
  if (!target) await sleep(200);
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let seq = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise((r) => { const i = ++seq; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });

await send("Page.enable");
for (const [device, metrics] of Object.entries(DEVICES)) {
  await send("Emulation.setDeviceMetricsOverride", { ...metrics, deviceScaleFactor: 1 });
  for (const scheme of ["light", "dark"]) {
    await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: scheme }] });
    for (const page of PAGES) {
      // Material remembers the palette in localStorage; clear it so the emulated scheme applies.
      await send("Runtime.evaluate", { expression: "try { localStorage.clear() } catch (e) {}" });
      await send("Page.navigate", { url: `file://${SITE}/${page}` });
      await sleep(1200);
      // Material restores a remembered palette on file:// pages; set the scheme explicitly.
      const value = scheme === "dark" ? "slate" : "default";
      await send("Runtime.evaluate", { expression: `document.body.setAttribute("data-md-color-scheme", "${value}"); document.querySelector(location.hash || null)?.scrollIntoView();` });
      await sleep(300);
      const shot = await send("Page.captureScreenshot", { format: "png" });
      const name = `${page.replace(/[\/#]/g, "_").replace(".html", "")}-${scheme}-${device}.png`;
      writeFileSync(join(OUT, name), Buffer.from(shot.result.data, "base64"));
    }
  }
}
ws.close();
chrome.kill();
console.log(`Saved ${PAGES.length * 4} screenshots to .checks/shots/`);
process.exit(0);
