#!/usr/bin/env python3
"""Render a multi-section markdown file as a paginated HTML reader.

One `## ` section per page, with a dock listing the sections and, under the
active one, its own subsections. Reuses the markdown renderer from
build_tastetest.py so there is one implementation, not two.

    python3 build_reader.py reports.md "Work Reports" > reader.html
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def renderer():
    """Shared markdown renderer, with heading levels remapped for this page.

    The taste test demotes headings by two (its specimens sit inside cards under
    the page's own headings). Here each report owns the page under a single h1,
    so `###` must land on <h3>: the reader styles h3 as the section rule, and
    render() hangs its dock anchors off h3/h4. Demoting produced <h5>, which
    silently killed every section link.
    """
    src = open(os.path.join(HERE, "build_tastetest.py")).read()
    js = src[src.index("function esc("):src.index("const LETTERS")]
    old = "const n = Math.min(h[1].length + 2, 6);"
    new = "const n = Math.min(Math.max(h[1].length, 3), 6);"
    assert js.count(old) == 1, "renderer heading line moved; check build_tastetest.py"
    return js.replace(old, new)

def pages(md_text):
    out = []
    for chunk in re.split(r"^## ", md_text, flags=re.M)[1:]:
        lines = chunk.split("\n")
        title = lines[0].strip().strip('"')
        body = "\n".join(lines[1:]).strip()
        subs = [m.group(1).strip() for m in re.finditer(r"^###\s+(.*)$", body, re.M)]
        words = len(re.findall(r"\b[\w'-]+\b", body))
        out.append({"title": title, "body": body, "subs": subs, "words": words})
    return out

def main(path, title):
    items = pages(open(path).read())
    print(TEMPLATE
          .replace("/*__MD__*/", renderer())
          .replace("/*__DATA__*/", json.dumps(items))
          .replace("__TITLE__", title))

TEMPLATE = r"""<title>__TITLE__</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root{
  --paper:#f7f8f9; --sheet:#fff; --ink:#14181c; --ink-2:#39424b; --muted:#6d7883;
  --rule:#dfe3e7; --chip:#eef1f3; --accent:#1f6f5c; --accent-soft:#e3efeb;
  --serif:'Source Serif 4',Georgia,'Times New Roman',serif;
  --sans:'Source Sans 3',system-ui,-apple-system,sans-serif,'Apple Color Emoji','Segoe UI Emoji';
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace,'Apple Color Emoji';
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#0f1216; --sheet:#171c21; --ink:#e8ecef; --ink-2:#bcc5cd; --muted:#8a949e;
  --rule:#2a323a; --chip:#212931; --accent:#5fbfa5; --accent-soft:#1b2b28;
}}
:root[data-theme="dark"]{
  --paper:#0f1216; --sheet:#171c21; --ink:#e8ecef; --ink-2:#bcc5cd; --muted:#8a949e;
  --rule:#2a323a; --chip:#212931; --accent:#5fbfa5; --accent-soft:#1b2b28;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  -webkit-font-smoothing:antialiased}
.shell{display:grid;grid-template-columns:264px minmax(0,1fr);gap:0;min-height:100vh}
/* dock */
.dock{border-right:1px solid var(--rule);padding:26px 20px 40px;position:sticky;top:0;
  height:100vh;overflow-y:auto;background:var(--paper)}
.brand{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);margin-bottom:20px}
.dock ol{list-style:none;margin:0;padding:0;counter-reset:d}
.dock>ol>li{counter-increment:d;margin-bottom:3px}
.dock a{display:block;padding:9px 11px 9px 34px;border-radius:7px;text-decoration:none;
  color:var(--ink-2);font-size:13.5px;line-height:1.35;position:relative;cursor:pointer}
.dock a::before{content:counter(d);position:absolute;left:11px;top:9px;font-family:var(--mono);
  font-size:11px;color:var(--muted)}
.dock a:hover{background:var(--chip)}
.dock a.on{background:var(--accent-soft);color:var(--ink);font-weight:600}
.dock a.on::before{color:var(--accent)}
.dock a:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.subs{list-style:none;margin:2px 0 10px;padding:0 0 0 34px}
.subs li{margin:1px 0}
.subs button{background:none;border:0;padding:4px 0;font:400 12.5px/1.35 var(--sans);
  color:var(--muted);cursor:pointer;text-align:left;width:100%}
.subs button:hover{color:var(--accent)}
.wc{font-family:var(--mono);font-size:10.5px;color:var(--muted);margin-top:2px;display:block}
/* sheet */
.main{padding:0 0 90px}
.sheet{background:var(--sheet);border-bottom:1px solid var(--rule);padding:44px 6vw 56px}
.eyebrow{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--accent);margin-bottom:10px}
h1{font-family:var(--sans);font-size:27px;font-weight:700;letter-spacing:-.015em;margin:0 0 4px;
  text-wrap:balance;max-width:26em}
.meta{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin-bottom:30px}
.doc{max-width:68ch;font-family:var(--serif);font-size:17px;line-height:1.62;color:var(--ink-2)}
.doc>*:first-child{margin-top:0}
.doc p{margin:0 0 1.05em}
.doc strong{color:var(--ink);font-weight:600}
.doc h3{font-family:var(--sans);font-size:15px;font-weight:700;color:var(--ink);
  margin:2em 0 .7em;padding-top:.9em;border-top:1px solid var(--rule);letter-spacing:.01em;
  scroll-margin-top:18px}
.doc h4,.doc h5,.doc h6{font-family:var(--sans);font-size:13.5px;font-weight:600;color:var(--ink);
  margin:1.5em 0 .5em}
.doc ul,.doc ol{margin:0 0 1.05em;padding-left:1.4em}
.doc li{margin:.42em 0}
.doc li>ul,.doc li>ol{margin:.4em 0 .1em}
.doc code{font-family:var(--mono);font-size:.83em;background:var(--chip);padding:.14em .4em;
  border-radius:4px;color:var(--ink)}
.doc pre{background:var(--chip);border:1px solid var(--rule);border-left:3px solid var(--accent);
  border-radius:7px;padding:14px 16px;overflow-x:auto;margin:0 0 1.05em}
.doc pre code{background:none;padding:0;font-size:12.5px;line-height:1.55;color:var(--ink-2)}
.doc blockquote{margin:0 0 1.05em;padding-left:1em;border-left:2px solid var(--rule);color:var(--muted)}
.doc hr{border:0;border-top:1px solid var(--rule);margin:1.6em 0}
.doc .tw{overflow-x:auto;margin:0 0 1.05em}
.doc table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:14px}
.doc th,.doc td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule);
  font-variant-numeric:tabular-nums}
.doc th{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);font-weight:500;white-space:nowrap}
.doc a{color:var(--accent)}
/* pager */
.pager{display:flex;gap:10px;align-items:center;padding:22px 6vw;flex-wrap:wrap}
button.pg{font:600 13px/1 var(--sans);padding:11px 17px;border-radius:8px;border:1px solid var(--rule);
  background:var(--sheet);color:var(--ink);cursor:pointer}
button.pg:hover:not(:disabled){border-color:var(--accent);color:var(--accent)}
button.pg:disabled{opacity:.38;cursor:default}
button.pg:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.hint{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:auto}
.mobtop{display:none}
@media (max-width:880px){
  .shell{grid-template-columns:1fr}
  .dock{display:none}
  .mobtop{display:block;padding:14px 20px;border-bottom:1px solid var(--rule);position:sticky;
    top:0;background:var(--paper);z-index:5}
  .mobtop select{width:100%;padding:9px 11px;border-radius:8px;border:1px solid var(--rule);
    background:var(--sheet);color:var(--ink);font:14px var(--sans)}
  .sheet{padding:30px 22px 40px}
  .pager{padding:18px 22px}
  .doc{font-size:16.5px}
}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
html{scroll-behavior:smooth}
</style>

<div class="shell">
  <nav class="dock" aria-label="Reports">
    <div class="brand">__TITLE__</div>
    <ol id="dock"></ol>
  </nav>
  <div class="main">
    <div class="mobtop"><select id="sel" aria-label="Choose report"></select></div>
    <article class="sheet">
      <div class="eyebrow" id="eyebrow"></div>
      <h1 id="title"></h1>
      <div class="meta" id="meta"></div>
      <div class="doc" id="doc"></div>
    </article>
    <div class="pager">
      <button class="pg" id="prev">&larr; Previous</button>
      <button class="pg" id="next">Next &rarr;</button>
      <span class="hint">&larr; &rarr; to page</span>
    </div>
  </div>
</div>

<script>
/*__MD__*/
const DATA = /*__DATA__*/;
let i = 0;
const $ = s => document.querySelector(s);

function slug(s){ return s.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""); }

function buildDock(){
  const ol = $("#dock"), sel = $("#sel");
  ol.innerHTML = ""; sel.innerHTML = "";
  DATA.forEach((p, n) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.tabIndex = 0; a.className = n === i ? "on" : "";
    a.innerHTML = `${p.title.split(":")[0]}<span class="wc">${p.words} words</span>`;
    a.onclick = () => go(n);
    a.onkeydown = e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(n); } };
    li.appendChild(a);
    if (n === i && p.subs.length) {
      const ul = document.createElement("ul"); ul.className = "subs";
      p.subs.forEach(s => {
        const b = document.createElement("button");
        b.textContent = s;
        b.onclick = () => { const el = document.getElementById(slug(s)); if (el) el.scrollIntoView(); };
        const sli = document.createElement("li"); sli.appendChild(b); ul.appendChild(sli);
      });
      li.appendChild(ul);
    }
    ol.appendChild(li);
    const o = document.createElement("option");
    o.value = n; o.textContent = `${n+1}. ${p.title.split(":")[0]}`;
    o.selected = n === i; sel.appendChild(o);
  });
  sel.onchange = e => go(+e.target.value);
}

function render(){
  const p = DATA[i];
  $("#eyebrow").textContent = `Report ${i+1} of ${DATA.length}`;
  const [head, ...rest] = p.title.split(":");
  $("#title").textContent = head.trim();
  $("#meta").textContent = (rest.join(":").trim() || "") + (rest.length ? "  ·  " : "") + `${p.words} words`;
  $("#doc").innerHTML = md(p.body);
  $("#doc").querySelectorAll("h3,h4").forEach(h => h.id = slug(h.textContent));
  $("#prev").disabled = i === 0;
  $("#next").disabled = i === DATA.length - 1;
  buildDock();
  window.scrollTo({top:0});
}
$("#prev").onclick = () => go(i-1);
$("#next").onclick = () => go(i+1);
function go(n){ if (n >= 0 && n < DATA.length) { i = n; render(); } }
addEventListener("keydown", e => {
  if (e.target.tagName === "SELECT") return;
  if (e.key === "ArrowLeft") go(i-1);
  if (e.key === "ArrowRight") go(i+1);
});
render();
</script>
"""

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Reader")
