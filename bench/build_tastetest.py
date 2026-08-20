#!/usr/bin/env python3
"""Build a blind A/B/C/D taste-test page from per-arm answer files.

Arm -> letter mapping is shuffled independently for EVERY prompt and baked in at
build time, so the page is deterministic and the mapping is auditable. Voting "A"
every time cannot favour any single arm.

    python3 build_tastetest.py out/*.jsonl > tastetest.html
"""
import json, glob, random, sys, os

SEED = int(os.environ.get("TT_SEED", "20260819"))
PROMPTS = os.environ.get("TT_PROMPTS", "prompts.jsonl")
ARM_LABEL = {"control": "No style (control)", "shipmate": "Shipmate",
             "spartan": "Spartan", "akind": "Attention-kind",
             "A-above-boxed": "Note above, artifact boxed",
             "B-below-boxed": "Artifact boxed, note below",
             "C-none-boxed":  "Artifact boxed, no note",
             "D-above-plain": "Note above, nothing boxed"}
ARM_HUE = {"control": "#78828e", "shipmate": "#0b6e99",
           "spartan": "#a2540a", "akind": "#6d3bab",
           "A-above-boxed": "#0b6e99", "B-below-boxed": "#127f6b",
           "C-none-boxed": "#a2540a", "D-above-plain": "#8a3b52"}

def load(paths):
    answers, arms = {}, []
    for p in paths:
        for line in open(p):
            if not line.strip():
                continue
            r = json.loads(line)
            answers.setdefault(r["id"], {})[r["arm"]] = r["text"]
            if r["arm"] not in arms:
                arms.append(r["arm"])
    return answers, arms

def main(paths):
    prompts = [json.loads(l) for l in
               open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 PROMPTS)) if l.strip()]
    answers, arms = load(paths)
    rng = random.Random(SEED)
    _base = []
    items = []
    for p in prompts:
        got = answers.get(p["id"], {})
        present = [a for a in arms if a in got]
        if len(present) < 2:
            continue
        # Balanced mask: within each block of len(arms) prompts we rotate a
        # shuffled base order, so every arm lands in every slot the same number
        # of times. A per-prompt shuffle leaves reading-order bias on the table.
        if len(items) % len(present) == 0:
            base = present[:]
            rng.shuffle(base)
            _base.clear(); _base.extend(base)
        j = len(items) % len(present)
        order = _base[j:] + _base[:j]
        items.append({"id": p["id"], "kind": p["kind"], "q": p["q"],
                      "specimens": [{"arm": a, "text": got[a]} for a in order]})
    payload = json.dumps({"items": items, "label": ARM_LABEL, "hue": ARM_HUE})
    print(TEMPLATE.replace("/*__DATA__*/", payload))

TEMPLATE = r"""<title>Blind Style Tasting</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  --paper:#f6f7f8; --card:#ffffff; --ink:#171a1f; --ink-2:#3d444d;
  --muted:#6b7480; --rule:#dde1e5; --chip:#eef0f2; --focus:#0b6e99;
  --shadow:0 1px 2px rgba(23,26,31,.05),0 8px 24px -12px rgba(23,26,31,.16);
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace,'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji';
  --sans:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif,'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji';
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#101317; --card:#1a1e24; --ink:#e9ecef; --ink-2:#b9c0c8;
  --muted:#8b95a1; --rule:#2b313a; --chip:#232932; --focus:#4aa8d8;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}}
:root[data-theme="dark"]{
  --paper:#101317; --card:#1a1e24; --ink:#e9ecef; --ink-2:#b9c0c8;
  --muted:#8b95a1; --rule:#2b313a; --chip:#232932; --focus:#4aa8d8;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 96px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
h1{font-size:20px;margin:6px 0 0;letter-spacing:-.01em;text-wrap:balance}
header{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;
  padding-bottom:16px;border-bottom:1px solid var(--rule);flex-wrap:wrap}
.count{font-family:var(--mono);font-size:12px;color:var(--muted);
  font-variant-numeric:tabular-nums}
/* progress: one tick per prompt, filled when voted */
.rail{display:flex;gap:3px;margin:16px 0 22px}
.tick{height:4px;flex:1;background:var(--rule);border-radius:2px;transition:background .18s}
.tick.done{background:var(--ink-2)}
.tick.here{background:var(--focus)}
.prompt{background:var(--chip);border:1px solid var(--rule);border-radius:10px;
  padding:16px 18px;margin-bottom:22px}
.prompt .k{font-family:var(--mono);font-size:10px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
.prompt p{margin:6px 0 0;font-size:17px;font-weight:500;text-wrap:balance}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
@media (max-width:820px){.grid{grid-template-columns:1fr}}
.spec{background:var(--card);border:1px solid var(--rule);border-radius:12px;
  display:flex;flex-direction:column;box-shadow:var(--shadow);overflow:hidden}
.spec.picked{border-color:var(--focus);box-shadow:0 0 0 2px var(--focus),var(--shadow)}
.spec h2{margin:0;padding:12px 16px;border-bottom:1px solid var(--rule);
  display:flex;align-items:center;gap:10px;font-size:12px;font-family:var(--mono);
  letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:500}
.letter{width:24px;height:24px;border-radius:6px;background:var(--chip);
  color:var(--ink);display:grid;place-items:center;font-weight:600;font-size:13px;
  letter-spacing:0}
.body{padding:16px 18px;overflow-y:auto;max-height:26rem;flex:1;
  font-size:14.5px;color:var(--ink-2);word-wrap:break-word}
.body>*:first-child{margin-top:0}
.body>*:last-child{margin-bottom:0}
.body p{margin:0 0 .8em}
.body strong{color:var(--ink);font-weight:600}
.body h3,.body h4,.body h5,.body h6{color:var(--ink);margin:1.25em 0 .5em;
  font-weight:600;line-height:1.3;text-wrap:balance}
.body h3{font-size:16px}.body h4{font-size:14.5px}
.body h5,.body h6{font-size:13px;font-family:var(--mono);letter-spacing:.06em;
  text-transform:uppercase;color:var(--muted)}
.body ul,.body ol{margin:0 0 .8em;padding-left:1.35em}
.body li{margin:.3em 0}
.body li>ul,.body li>ol{margin:.35em 0 .1em}
.body code{font-family:var(--mono);font-size:.87em;background:var(--chip);
  padding:.12em .38em;border-radius:4px;color:var(--ink)}
.body pre{background:var(--chip);border:1px solid var(--rule);border-radius:8px;
  padding:11px 13px;overflow-x:auto;margin:0 0 .8em}
.body pre code{background:none;padding:0;font-size:12.5px;line-height:1.5}
.body blockquote{margin:0 0 .8em;padding-left:.9em;border-left:2px solid var(--rule);
  color:var(--muted)}
.body hr{border:0;border-top:1px solid var(--rule);margin:1.1em 0}
.body .tw{overflow-x:auto;margin:0 0 .8em}
.body table{width:100%;border-collapse:collapse;font-size:13.5px}
.body th,.body td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--rule)}
.body th{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);font-weight:500;white-space:nowrap}
.body a{color:var(--focus)}
.pick{margin:0;padding:11px 16px;border:0;border-top:1px solid var(--rule);
  background:transparent;color:var(--ink);font:500 13px/1 var(--sans);
  cursor:pointer;text-align:left}
.pick:hover{background:var(--chip)}
.pick:focus-visible{outline:2px solid var(--focus);outline-offset:-2px}
.spec.picked .pick{color:var(--focus);font-weight:600}
.nav{display:flex;gap:10px;align-items:center;margin-top:24px;flex-wrap:wrap}
button.nb{font:500 13px/1 var(--sans);padding:10px 16px;border-radius:8px;
  border:1px solid var(--rule);background:var(--card);color:var(--ink);cursor:pointer}
button.nb:hover{background:var(--chip)}
button.nb:disabled{opacity:.4;cursor:default}
button.nb:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.hint{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:auto}
/* reveal */
.reveal{margin-top:32px;border-top:1px solid var(--rule);padding-top:24px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--rule)}
th{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);font-weight:500}
td.n{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right}
.swatch{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:8px}
.bar{height:6px;border-radius:3px;min-width:2px}
.hid{display:none}
.note{display:block;margin-top:18px}
.note .k,#exportWrap .k{font-family:var(--mono);font-size:10px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);display:block;margin-bottom:6px}
textarea{width:100%;background:var(--card);color:var(--ink);border:1px solid var(--rule);
  border-radius:8px;padding:11px 13px;font:14px/1.5 var(--sans);resize:vertical}
#exportBox{font:12.5px/1.6 var(--mono);white-space:pre}
textarea:focus-visible{outline:2px solid var(--focus);outline-offset:-1px;border-color:var(--focus)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="wrap">
  <header>
    <div>
      <div class="eyebrow">Output-style benchmark &middot; blind</div>
      <h1>Which reply would you rather have gotten?</h1>
    </div>
    <div class="count" id="count"></div>
  </header>

  <div class="rail" id="rail"></div>

  <div id="stage">
    <div class="prompt"><div class="k" id="kind"></div><p id="q"></p></div>
    <div class="grid" id="grid"></div>
    <label class="note">
      <span class="k">Why? (optional, exported with your results)</span>
      <textarea id="note" rows="2" placeholder="e.g. B buried the recommendation; D's numbered steps were easiest to follow"></textarea>
    </label>
    <div class="nav">
      <button class="nb" id="prev">&larr; Back</button>
      <button class="nb" id="next">Skip &rarr;</button>
      <button class="nb" id="revealBtn">Reveal results</button>
      <button class="nb" id="exportBtn">Copy results</button>
      <span class="hint">Keys 1&ndash;4 to pick &middot; &larr; &rarr; to move &middot; saved locally</span>
    </div>
    <div id="exportWrap" class="hid">
      <div class="k" style="margin:18px 0 6px">Paste this into chat</div>
      <textarea id="exportBox" rows="14" readonly></textarea>
      <div class="hint" id="copyState" style="margin-top:6px"></div>
    </div>
  </div>

  <div class="reveal hid" id="reveal"></div>
</div>

<script>
const DATA = /*__DATA__*/;

// Minimal markdown -> HTML. No libraries: the artifact CSP blocks external scripts.
// Escapes first, so specimen text can never inject markup.
function esc(s){ return s.replace(/[&<>"]/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

function inline(s){
  return s
    .replace(/`([^`]+)`/g, (m,a) => `<code>${a}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, (m,a) => `<strong>${a}</strong>`)
    .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,;:!?]|$)/g, (m,p,a) => `${p}<em>${a}</em>`)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m,a,b) => `<a href="${b}" rel="noopener">${a}</a>`);
}

function md(src){
  const lines = esc(src.replace(/\r/g,"")).split("\n");
  let out = [], i = 0;
  const flushPara = buf => { if (buf.length) out.push(`<p>${inline(buf.join(" "))}</p>`); buf.length = 0; };
  let para = [];
  while (i < lines.length) {
    const l = lines[i];
    // fenced code
    if (/^\s*```/.test(l)) {
      flushPara(para);
      const lang = l.replace(/^\s*```/,"").trim(); i++;
      const code = [];
      while (i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i++]);
      i++;
      out.push(`<pre><code>${code.join("\n")}</code></pre>`);
      continue;
    }
    // table: header row followed by a separator row
    if (/^\s*\|/.test(l) && i+1 < lines.length && /^\s*\|[\s:|-]+\|?\s*$/.test(lines[i+1])) {
      flushPara(para);
      const cells = r => r.trim().replace(/^\||\|$/g,"").split("|").map(c => c.trim());
      const head = cells(l); i += 2;
      let body = "";
      while (i < lines.length && /^\s*\|/.test(lines[i])) {
        body += `<tr>${cells(lines[i++]).map(c => `<td>${inline(c)}</td>`).join("")}</tr>`;
      }
      out.push(`<div class="tw"><table><thead><tr>${
        head.map(c => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table></div>`);
      continue;
    }
    // heading
    const h = l.match(/^(#{1,6})\s+(.*)$/);
    if (h) { flushPara(para); const n = Math.min(h[1].length + 2, 6);
      out.push(`<h${n}>${inline(h[2])}</h${n}>`); i++; continue; }
    // horizontal rule
    if (/^\s*([-*_])\1{2,}\s*$/.test(l)) { flushPara(para); out.push("<hr>"); i++; continue; }
    // blockquote
    if (/^\s*&gt;\s?/.test(l)) {          // esc() already turned ">" into "&gt;"
      flushPara(para); const q = [];
      while (i < lines.length && /^\s*&gt;\s?/.test(lines[i])) q.push(lines[i++].replace(/^\s*&gt;\s?/,""));
      out.push(`<blockquote><p>${inline(q.join(" "))}</p></blockquote>`); continue;
    }
    // lists, ordered or not, with one level of nesting
    const li = l.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/);
    if (li) {
      flushPara(para);
      const ordered = /\d/.test(li[2]);
      const tag = ordered ? "ol" : "ul";
      let html = "", cur = null, sub = [];
      const closeSub = () => { if (sub.length){ html += md(sub.join("\n")); sub = []; } };
      while (i < lines.length) {
        const m = lines[i].match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/);
        if (m && m[1].length <= li[1].length) {
          if (cur !== null){ closeSub(); html += `</li>`; }
          html += `<li>${inline(m[3])}`; cur = 1; i++;
        } else if (cur !== null && lines[i].trim() && /^\s{2,}/.test(lines[i])) {
          sub.push(lines[i].replace(/^\s{2}/,"")); i++;
        } else break;
      }
      if (cur !== null){ closeSub(); html += `</li>`; }
      out.push(`<${tag}>${html}</${tag}>`); continue;
    }
    if (!l.trim()) { flushPara(para); i++; continue; }
    para.push(l); i++;
  }
  flushPara(para);
  return out.join("\n");
}

const LETTERS = ["A","B","C","D"];
const KEY = "tastetest:" + DATA.items.length + ":" + (DATA.items[0]||{}).id;
let votes = {}, notes = {}, i = 0;
try {
  const s = JSON.parse(localStorage.getItem(KEY) || "{}");
  votes = s.votes || {}; notes = s.notes || {};
} catch (e) {}
const save = () => { try {
  localStorage.setItem(KEY, JSON.stringify({votes, notes}));
} catch (e) {} };

const $ = s => document.querySelector(s);
const rail = $("#rail"), grid = $("#grid");

DATA.items.forEach(() => {
  const t = document.createElement("div"); t.className = "tick"; rail.appendChild(t);
});

function render(){
  const it = DATA.items[i];
  $("#kind").textContent = it.kind === "deliverable" ? "Asked to write something" : "Asked a question";
  $("#q").textContent = it.q;
  $("#count").textContent = `${i+1} / ${DATA.items.length} · ${Object.keys(votes).length} judged`;
  grid.innerHTML = "";
  it.specimens.forEach((s, n) => {
    const card = document.createElement("div");
    card.className = "spec" + (votes[it.id] === n ? " picked" : "");
    const h = document.createElement("h2");
    h.innerHTML = `<span class="letter">${LETTERS[n]}</span> Specimen ${LETTERS[n]}`;
    const b = document.createElement("div");
    b.className = "body"; b.innerHTML = md(s.text);
    const btn = document.createElement("button");
    btn.className = "pick";
    btn.textContent = votes[it.id] === n ? "✓ Your pick" : `Pick ${LETTERS[n]}`;
    btn.onclick = () => vote(n);
    card.append(h, b, btn); grid.appendChild(card);
  });
  [...rail.children].forEach((t, n) => {
    t.className = "tick" + (DATA.items[n] && votes[DATA.items[n].id] !== undefined ? " done" : "")
      + (n === i ? " here" : "");
  });
  $("#note").value = notes[it.id] || "";
  $("#prev").disabled = i === 0;
  $("#next").textContent = votes[DATA.items[i].id] !== undefined ? "Next →" : "Skip →";
  $("#next").disabled = i >= DATA.items.length - 1;
}

function vote(n){
  votes[DATA.items[i].id] = n;
  save();
  if (i < DATA.items.length - 1) { i++; render(); }
  else render();
}

$("#note").addEventListener("input", e => {
  const id = DATA.items[i].id;
  if (e.target.value.trim()) notes[id] = e.target.value; else delete notes[id];
  save();
});
$("#prev").onclick = () => { if(i>0){i--;render();} };
$("#next").onclick = () => { if(i<DATA.items.length-1){i++;render();} };
addEventListener("keydown", e => {
  if (e.target.tagName === "TEXTAREA") return;   // typing a note is not a vote
  if (e.key === "ArrowLeft" && i>0) { i--; render(); }
  else if (e.key === "ArrowRight" && i<DATA.items.length-1) { i++; render(); }
  else if (["1","2","3","4"].includes(e.key)) {
    const n = +e.key - 1;
    if (n < DATA.items[i].specimens.length) vote(n);
  }
});

$("#revealBtn").onclick = () => {
  const tally = {}, seen = {};
  DATA.items.forEach(it => {
    it.specimens.forEach(s => { tally[s.arm] = tally[s.arm] || 0; });
    const v = votes[it.id];
    if (v !== undefined) {
      const arm = it.specimens[v].arm;
      tally[arm]++;
      it.specimens.forEach(s => seen[s.arm] = (seen[s.arm]||0)+1);
    }
  });
  const judged = Object.keys(votes).length;
  const ranked = Object.entries(tally).sort((a,b) => b[1]-a[1]);
  const max = Math.max(1, ...ranked.map(r => r[1]));
  let h = `<div class="eyebrow">Unmasked</div><h1 style="margin-bottom:14px">
    ${judged} of ${DATA.items.length} prompts judged</h1>`;
  if (!judged) h += `<p style="color:var(--muted)">No picks recorded yet.</p>`;
  else {
    h += `<table><thead><tr><th>Style</th><th>Wins</th><th>Win rate</th><th style="width:38%"></th></tr></thead><tbody>`;
    ranked.forEach(([arm, n]) => {
      const pct = judged ? Math.round(100*n/judged) : 0;
      h += `<tr><td><span class="swatch" style="background:${DATA.hue[arm]}"></span>${DATA.label[arm]}</td>
        <td class="n">${n}</td><td class="n">${pct}%</td>
        <td><div class="bar" style="width:${100*n/max}%;background:${DATA.hue[arm]}"></div></td></tr>`;
    });
    h += `</tbody></table>`;
    h += `<div class="eyebrow" style="margin:26px 0 8px">Per prompt</div><table><tbody>`;
    DATA.items.forEach(it => {
      const v = votes[it.id];
      const who = v === undefined ? `<span style="color:var(--muted)">skipped</span>`
        : `<span class="swatch" style="background:${DATA.hue[it.specimens[v].arm]}"></span>${DATA.label[it.specimens[v].arm]}`;
      h += `<tr><td style="color:var(--ink-2)">${it.q.length>66?it.q.slice(0,66)+"…":it.q}</td><td>${who}</td></tr>`;
    });
    h += `</tbody></table>`;
  }
  const r = $("#reveal"); r.innerHTML = h; r.classList.remove("hid");
  r.scrollIntoView({behavior:"smooth"});
};

function buildExport(){
  const tally = {};
  DATA.items.forEach(it => it.specimens.forEach(s => { tally[s.arm] = tally[s.arm] || 0; }));
  DATA.items.forEach(it => {
    const v = votes[it.id];
    if (v !== undefined) tally[it.specimens[v].arm]++;
  });
  const judged = Object.keys(votes).length;
  let out = `## Taste test results (${judged}/${DATA.items.length} judged)\n\n`;
  out += `| Style | Wins |\n|---|---|\n`;
  Object.entries(tally).sort((a,b) => b[1]-a[1])
    .forEach(([a,n]) => { out += `| ${DATA.label[a]} | ${n} |\n`; });
  ["deliverable","answer"].forEach(kind => {
    const sub = DATA.items.filter(it => it.kind === kind);
    const t2 = {};
    sub.forEach(it => { const v = votes[it.id];
      if (v !== undefined) t2[it.specimens[v].arm] = (t2[it.specimens[v].arm]||0)+1; });
    const line = Object.entries(t2).sort((a,b)=>b[1]-a[1])
      .map(([a,n]) => `${DATA.label[a]} ${n}`).join(", ");
    out += `\n**${kind === "deliverable" ? "Asked to write something" : "Asked a question"}:** ${line || "none judged"}`;
  });
  out += `\n\n### Per prompt\n\n`;
  DATA.items.forEach(it => {
    const v = votes[it.id];
    out += `- **${it.id}** — ${v === undefined ? "skipped" : DATA.label[it.specimens[v].arm]}`;
    if (notes[it.id]) out += `\n  - "${notes[it.id].replace(/\s+/g," ").trim()}"`;
    out += `\n`;
  });
  return out;
}

$("#exportBtn").onclick = async () => {
  const txt = buildExport();
  $("#exportBox").value = txt;
  $("#exportWrap").classList.remove("hid");
  let ok = false;
  try { await navigator.clipboard.writeText(txt); ok = true; } catch (e) {}
  $("#copyState").textContent = ok
    ? "Copied to clipboard. Paste it into chat."
    : "Clipboard blocked here: select the text above and copy it.";
  $("#exportBox").scrollIntoView({behavior:"smooth", block:"nearest"});
};

render();
</script>
"""

if __name__ == "__main__":
    main(sys.argv[1:] or glob.glob("out/*.jsonl"))
