#!/usr/bin/env python3
"""Build a blind A/B/C/D taste-test page from per-arm answer files.

Arm -> letter mapping is shuffled independently for EVERY prompt and baked in at
build time, so the page is deterministic and the mapping is auditable. Voting "A"
every time cannot favour any single arm.

    python3 build_tastetest.py out/*.jsonl > tastetest.html
"""
import json, glob, random, html, sys, os

SEED = 20260819
ARM_LABEL = {"control": "No style (control)", "shipmate": "Shipmate",
             "spartan": "Spartan", "akind": "Attention-kind"}
ARM_HUE = {"control": "#78828e", "shipmate": "#0b6e99",
           "spartan": "#a2540a", "akind": "#6d3bab"}

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
                                 "prompts.jsonl")) if l.strip()]
    answers, arms = load(paths)
    rng = random.Random(SEED)
    items = []
    for p in prompts:
        got = answers.get(p["id"], {})
        present = [a for a in arms if a in got]
        if len(present) < 2:
            continue
        order = present[:]
        rng.shuffle(order)                      # fresh mask for every prompt
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
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  --sans:'IBM Plex Sans',system-ui,-apple-system,Segoe UI,sans-serif;
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
.body{padding:16px;overflow-y:auto;max-height:26rem;flex:1;
  font-size:14.5px;color:var(--ink-2);white-space:pre-wrap;word-wrap:break-word}
.body strong{color:var(--ink)}
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
    <div class="nav">
      <button class="nb" id="prev">&larr; Back</button>
      <button class="nb" id="next">Skip &rarr;</button>
      <button class="nb" id="revealBtn">Reveal results</button>
      <span class="hint">Keys 1&ndash;4 to pick &middot; &larr; &rarr; to move</span>
    </div>
  </div>

  <div class="reveal hid" id="reveal"></div>
</div>

<script>
const DATA = /*__DATA__*/;
const LETTERS = ["A","B","C","D"];
const votes = {};
let i = 0;

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
    b.className = "body"; b.textContent = s.text;
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
  $("#prev").disabled = i === 0;
  $("#next").textContent = votes[DATA.items[i].id] !== undefined ? "Next →" : "Skip →";
  $("#next").disabled = i >= DATA.items.length - 1;
}

function vote(n){
  votes[DATA.items[i].id] = n;
  if (i < DATA.items.length - 1) { i++; render(); }
  else render();
}

$("#prev").onclick = () => { if(i>0){i--;render();} };
$("#next").onclick = () => { if(i<DATA.items.length-1){i++;render();} };
addEventListener("keydown", e => {
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

render();
</script>
"""

if __name__ == "__main__":
    main(sys.argv[1:] or glob.glob("out/*.jsonl"))
