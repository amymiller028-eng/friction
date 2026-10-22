"""Turn the Chapter 4 findings into an accordion like the live page: title + 'In the book' always visible,
the data opens on click, first one open, one open at a time. Text is unchanged."""
import re
import sys

for path in sys.argv[1:]:
    h = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    if 'class="ins acc"' in h:
        print(path, 'already converted'); continue
    pat = re.compile(r'      <article class="ins">\n        <h3>(.*?)</h3>\n        <p class="inbook">(.*?)</p>\n(.*?)      </article>\n', re.S)
    n = [0]

    def conv(m):
        n[0] += 1
        title, inbook, body = m.group(1), m.group(2), m.group(3)
        return (f'      <details class="ins acc" id="finding-{n[0]}"{" open" if n[0] == 1 else ""}>\n'
                f'        <summary><span class="acc-t" role="heading" aria-level="3">{title}</span>'
                f'<span class="acc-b">{inbook}</span><span class="chev" aria-hidden="true"></span></summary>\n'
                f'        <div class="acc-body">\n{body}        </div>\n      </details>\n')
    h = pat.sub(conv, h)
    if n[0] != 8:
        raise SystemExit(f'{path}: expected 8 findings, converted {n[0]}')
    h = h.replace('</style>', '''
/* chapter 4 accordion, like the live page */
.ch4d{gap:.9rem}
.ins.acc{border:1px solid var(--hair);border-radius:10px;padding:0;background:var(--surface);overflow:hidden}
.ins.acc summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:minmax(0,1fr) 28px;gap:.35rem 1rem;padding:1.15rem 1.3rem;transition:background .15s}
.ins.acc summary::-webkit-details-marker{display:none}
.ins.acc summary:hover{background:var(--aside)}
.acc-t{grid-column:1;font-family:var(--font-display);font-weight:700;font-size:clamp(1.05rem,2.3vw,1.25rem);line-height:1.25;color:var(--ink)}
.acc-b{grid-column:1;font-size:.93rem;color:var(--ink-2);line-height:1.55}
.acc-b b{color:var(--ink)}
.chev{grid-column:2;grid-row:1/span 2;align-self:center;width:28px;height:28px;border-radius:50%;background:var(--aside);position:relative;transition:transform .25s}
.chev::before{content:"";position:absolute;left:50%;top:45%;width:8px;height:8px;border-right:2px solid var(--navy);border-bottom:2px solid var(--navy);transform:translate(-50%,-50%) rotate(45deg)}
.ins.acc[open] .chev{transform:rotate(180deg)}
.ins.acc[open] summary{border-bottom:1px solid var(--hair)}
.acc-body{padding:1rem 1.3rem .4rem}
@media (prefers-reduced-motion:reduce){.chev{transition:none}}
</style>''', 1)
    h = h.replace('</body>', '''<script>
// one Chapter 4 finding open at a time
document.querySelectorAll('details.acc').forEach(function (d) {
  d.addEventListener('toggle', function () {
    if (d.open) document.querySelectorAll('details.acc[open]').forEach(function (o) { if (o !== d) o.open = false; });
  });
});
</script>
</body>''', 1)
    open(path, 'w', encoding='utf-8').write(h)
    print(path, 'converted', n[0])
