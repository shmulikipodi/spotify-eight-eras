t=open('eras_template.html').read()
# ---- CSS additions
css='''
/* story: eras alternate with the changes between them */
.story{display:flex;flex-direction:column}
.story .era{grid-template-columns:3.2rem minmax(0,1fr)}
.change{display:grid;grid-template-columns:3.2rem minmax(0,1fr);gap:4px 16px;padding-block:8px 36px}
.change .rail{display:flex;justify-content:center}
.change .rail i{width:1px;background:var(--ink);opacity:.5;height:100%;background:repeating-linear-gradient(var(--ink) 0 4px,transparent 4px 8px)}
.change .body{display:flex;flex-direction:column;gap:14px;min-width:0;background:var(--sheet);border:1px solid var(--rule);border-radius:4px;padding:20px 22px}
.change .tag{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline}
.change .tag b{font:italic 500 1.35rem var(--display)}
.change .tag span{font:12px var(--mono);color:var(--muted)}
.change .tag .type{font:500 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--paper);background:var(--ink);padding:2px 8px;border-radius:999px}
.change p{color:var(--ink2);font-size:15px;max-width:72ch}
.change p b{color:var(--ink);font-weight:500}
.flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:12px 28px;font-size:14px}
.flow .lbl{font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
.flow ul{list-style:none;margin:0;padding:0}
.flow li{display:flex;justify-content:space-between;gap:10px;padding-block:2px;border-bottom:1px solid var(--rule)}
.flow li span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink)}
.flow li span:last-child{font:12px var(--mono);color:var(--muted);white-space:nowrap}
.firsts{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px;font-size:14px;color:var(--ink2)}
.firsts li{display:grid;grid-template-columns:6.6em minmax(0,1fr);gap:10px}
.firsts li span:first-child{font:12px var(--mono);color:var(--muted);padding-top:2px}
.firsts b{font-weight:500;color:var(--ink)}
.flow .firsts li{display:grid;justify-content:stretch;border:0}
.flow .firsts li > span:last-child{white-space:normal;font:14px/1.4 var(--body);color:var(--ink2);min-width:0}
.flow .firsts li > span:first-child{font:12px var(--mono);color:var(--muted);white-space:nowrap}
.flow .firsts li span span{white-space:normal;color:inherit;font:inherit}
.multi{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:28px 36px}
.multi>div{min-width:0;display:flex;flex-direction:column;gap:4px}
.multi .mh{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.multi .mh b{font-weight:500;display:inline-flex;align-items:center;gap:8px}
.multi .mh b i{width:11px;height:11px;border-radius:2px}
.multi .mh span{font:12px var(--mono);color:var(--muted)}
.multi p{font-size:13px;color:var(--muted)}
.after{display:flex;flex-direction:column;border-top:1px solid var(--ink)}
.arow{display:grid;grid-template-columns:minmax(0,15em) minmax(0,1fr) 7.5em;gap:6px 20px;align-items:center;padding-block:12px;border-bottom:1px solid var(--rule)}
.arow .an{font:italic 500 1.1rem var(--display)}
.arow .an small{display:block;font:12px var(--body);font-style:normal;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.arow .ab{display:flex;height:18px;gap:2px;min-width:0}
.arow .ab i{display:block;height:100%;border-radius:2px}
.arow .av{font:12px var(--mono);color:var(--ink2);text-align:end}
@media (max-width:640px){ .arow{grid-template-columns:minmax(0,1fr)} .arow .av{text-align:start} .change,.story .era{grid-template-columns:1.6rem minmax(0,1fr)} .era .n{font-size:1.6rem} .change .body{padding:16px} }
</style>'''
t=t.replace('</style>',css,1)
# ---- HTML: genre multiples before eras; eras section becomes story; afterlife after; drop library
old_eras=t[t.index('  <section aria-labelledby="erasH">'):t.index('  <section aria-labelledby="ageH">')]
new_eras='''  <section aria-labelledby="multiH">
    <div class="head">
      <p class="kicker">Share of each month's music · one shared scale</p>
      <h2 id="multiH">Each genre <em>on its own</em></h2>
      <div class="prose" id="multiP"></div>
    </div>
    <div class="multi" id="multi"></div>
  </section>

  <section aria-labelledby="storyH">
    <div class="head">
      <p class="kicker">Eight eras and the seven changes between them, in order</p>
      <h2 id="storyH">How it <em>actually went</em></h2>
      <div class="prose"><p>Each era is followed by the change that ended it. The change panels zoom in to weeks: the top bars show the genre mix each week, the gray bars below show how many hours you listened. The dashed line is where the next era begins.</p></div>
    </div>
    <div class="story" id="story"></div>
  </section>

  <section aria-labelledby="afterH">
    <div class="head">
      <p class="kicker">The artists that defined each era, before, during and after it</p>
      <h2 id="afterH">What each era <em>left behind</em></h2>
      <div class="prose" id="afterP"></div>
    </div>
    <div class="legend"><span style="display:inline-flex;gap:6px;align-items:center"><i style="background:var(--q2)"></i>before the era</span><span style="display:inline-flex;gap:6px;align-items:center"><i style="background:var(--q5)"></i>during</span><span style="display:inline-flex;gap:6px;align-items:center"><i style="background:var(--g1)"></i>after it ended</span></div>
    <div class="after" id="after"></div>
  </section>

'''
t=t.replace(old_eras,new_eras)
lib=t[t.index('  <section aria-labelledby="libH">'):t.index('  <footer>')]
t=t.replace(lib,'')
# ---- JS: replace eras renderer, drop library renderer
old_js=t[t.index('/* ---------- eras ---------- */'):t.index('/* ---------- music age ---------- */')]
t=t.replace(old_js,open('story_js.txt').read())
lib_js=t[t.index('/* ---------- library ---------- */'):t.index('</script>')]
t=t.replace(lib_js,'')
t=t.replace('<title>Eight Eras</title>','<title>Eight Eras</title>')
open('story_template.html','w').write(t)
d=open('output/dash4.json').read(); open('output/eight_eras.html','w').write(t.replace('__DATA__',d))
print('ok')
