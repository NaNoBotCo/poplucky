# -*- coding: utf-8 -*-
"""
shelf.py — Phase 1. The collector's own shelf.

Everything here is client-side and account-free: state lives in localStorage,
nothing is sent anywhere. Imported by build.py, which concatenates SHELF_CSS
and SHELF_JS onto its own and renders SHELF_BODY at /shelf/.

Trade cards are drawn in a browser canvas rather than by Pillow, which means
Thai and Chinese shape correctly — the raqm limitation that caps the og:image
cards at English does not apply here.
"""

# ---------------------------------------------------------------------------
# UI strings, merged into build.UI
# ---------------------------------------------------------------------------
SHELF_UI = {
    "shelf": {"en": "My Shelf", "th": "ชั้นของฉัน", "zh": "我的架子"},
    "have": {"en": "Have", "th": "มีแล้ว", "zh": "已有"},
    "seeking": {"en": "Seeking", "th": "กำลังตามหา", "zh": "想要"},
    "doubles": {"en": "Doubles", "th": "ตัวซ้ำ", "zh": "重复款"},
    "complete": {"en": "Complete", "th": "ครบชุด", "zh": "已集齐"},
    "shelf_blurb": {
        "en": ("Kept on this device only — no account, nothing sent anywhere. "
               "Back it up if it matters to you."),
        "th": ("เก็บไว้ในเครื่องนี้เท่านั้น ไม่ต้องสมัครสมาชิก ไม่ส่งข้อมูลไปไหน "
               "ถ้าสำคัญกับคุณ อย่าลืมสำรองไว้"),
        "zh": "只存在这台设备上 — 无需账号，不会上传。重要的话请备份。",
    },
    "shelf_empty": {
        "en": "The shelf is waiting. Mark a figure you own and it will appear here.",
        "th": "ชั้นยังว่างอยู่ กดว่ามีตัวไหนแล้ว เดี๋ยวมันจะมาอยู่ตรงนี้",
        "zh": "架子还空着。标记你已有的款式，它就会出现在这里。",
    },
    "no_trade": {
        "en": ("A trade card needs something to offer or something to look for. "
               "Mark a double, or tap the heart on a figure you want."),
        "th": ("การ์ดแลกเปลี่ยนต้องมีของให้แลก หรือของที่ตามหา "
               "กดเพิ่มตัวซ้ำ หรือกดหัวใจตัวที่อยากได้"),
        "zh": "交换卡需要有可换的或想找的。标记一个重复款，或点想要的爱心。",
    },
    "tradecard": {"en": "Make a trade card", "th": "ทำการ์ดแลกเปลี่ยน",
                  "zh": "制作交换卡"},
    "tradecard_hint": {
        "en": "A picture to post where trading already happens. Yours to share.",
        "th": "รูปสำหรับโพสต์ในกลุ่มที่เขาแลกกันอยู่แล้ว เอาไปแชร์ได้เลย",
        "zh": "一张可以发到现成交换群里的图。随你分享。",
    },
    "download": {"en": "Save the card", "th": "บันทึกการ์ด", "zh": "保存卡片"},
    "copytext": {"en": "Copy as text", "th": "คัดลอกเป็นข้อความ", "zh": "复制文字版"},
    "copied": {"en": "Copied", "th": "คัดลอกแล้ว", "zh": "已复制"},
    "backup": {"en": "Back up the shelf", "th": "สำรองชั้นของฉัน", "zh": "备份架子"},
    "restore": {"en": "Restore from a backup", "th": "กู้คืนจากไฟล์สำรอง",
                "zh": "从备份恢复"},
    "restored": {"en": "Shelf restored", "th": "กู้คืนชั้นเรียบร้อย", "zh": "架子已恢复"},
    "restore_bad": {"en": "That file was not a Poplucky backup",
                    "th": "ไฟล์นี้ไม่ใช่ไฟล์สำรองของ Poplucky",
                    "zh": "这不是 Poplucky 的备份文件"},
    "clear": {"en": "Clear the shelf", "th": "ล้างชั้น", "zh": "清空架子"},
    "clear_sure": {
        "en": "Clear the whole shelf? Back it up first if you might want it.",
        "th": "ล้างทั้งชั้นเลยไหม ถ้าอาจจะอยากได้คืน สำรองไว้ก่อนนะ",
        "zh": "要清空整个架子吗？可能还想要的话，先备份。",
    },
    "on_shelf": {"en": "On your shelf", "th": "อยู่บนชั้นแล้ว", "zh": "已在架上"},
    "across": {"en": "across", "th": "จาก", "zh": "分布于"},
    "sets": {"en": "sets", "th": "ชุด", "zh": "套"},
    "figures_word": {"en": "figures", "th": "ตัว", "zh": "款"},
    "trade_have": {"en": "HAVE", "th": "มี", "zh": "有"},
    "trade_want": {"en": "LOOKING FOR", "th": "ตามหา", "zh": "找"},
    "and_more": {"en": "and %d more", "th": "และอีก %d", "zh": "还有 %d 款"},
}

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
SHELF_CSS = """
/* --- shelf controls on a figure card ------------------------------------ */
.card{display:flex;flex-direction:column}
.card-link{text-decoration:none;color:inherit;display:block;position:relative;
  z-index:1}
.ctl{display:flex;align-items:center;gap:5px;margin-top:11px;position:relative;
  z-index:2}
.ctl button{font:inherit;font-size:.95rem;line-height:1;cursor:pointer;
  border:1px solid var(--line);background:var(--card-solid);color:var(--dim);
  width:30px;height:30px;border-radius:9px;display:grid;place-items:center;
  padding:0;transition:transform .15s cubic-bezier(.34,1.8,.5,1),
    border-color .15s,color .15s,background .15s}
.ctl button:hover{transform:translateY(-2px) scale(1.07);color:var(--ink);
  border-color:var(--pink)}
.ctl button:active{transform:scale(.9)}
.ctl .cnt{min-width:1.6em;text-align:center;font-weight:750;font-size:.95rem;
  font-variant-numeric:tabular-nums}
.ctl .cnt.zero{color:var(--dim);font-weight:500}
.ctl .wish{margin-left:auto}
.ctl .wish[aria-pressed=true]{color:var(--pink);border-color:var(--pink);
  background:rgba(255,111,165,.12)}
.ctl button[disabled]{opacity:.34;cursor:default}
.ctl button[disabled]:hover{transform:none;color:var(--dim);
  border-color:var(--line)}
.card.owned{border-color:var(--mint)}
.card.owned .fname::after{content:" \\2713";color:var(--mint);font-weight:800}
.shelf-item .spark{font-size:17px}
.shelf-item.dupe .cnt{color:var(--gold)}
/* reveal: the little pop when a figure lands on the shelf */
@keyframes popin{0%{transform:scale(1)}38%{transform:scale(1.13) rotate(-3deg)}
  100%{transform:scale(1)}}
.shelf-item.just-landed{animation:popin .52s cubic-bezier(.34,1.7,.5,1)}
.spark{position:absolute;pointer-events:none;font-size:15px;z-index:5;
  animation:fly .72s ease-out forwards}
@keyframes fly{0%{opacity:1;transform:translate(0,0) scale(.5)}
  100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1.15)}}
@media (prefers-reduced-motion:reduce){
  .shelf-item.just-landed{animation:none}
  .spark{display:none}
  .card.secret::after{animation:none}
}
/* --- standalone control on a figure page -------------------------------- */
.shelfsolo{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
  border:1px solid var(--line);border-radius:16px;padding:15px 18px;
  background:var(--card);backdrop-filter:blur(11px);margin:18px 0;
  position:relative}
.shelfsolo .lbl{font-size:.74rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--dim)}
.shelfsolo .ctl{margin-top:0}
.shelfsolo .ctl button{width:38px;height:38px;font-size:1.1rem}
.shelfsolo .ctl .cnt{font-size:1.2rem;min-width:2em}
.shelfsolo .ctl .wish{margin-left:6px}
.shelfsolo.owned{border-color:var(--mint)}
.shelfsolo .mine{color:var(--mint);font-weight:750;font-size:.9rem}
.shelfsolo:not(.owned) .mine{display:none}

/* --- shelf page --------------------------------------------------------- */
.shelfnav{margin-left:14px;font-size:.86rem;font-weight:700;text-decoration:none;
  border:1px solid var(--line);background:var(--card);padding:5px 13px;
  border-radius:999px;backdrop-filter:blur(8px);white-space:nowrap;
  transition:transform .16s,border-color .16s}
.shelfnav:hover{transform:translateY(-2px);border-color:var(--pink)}
.shelfnav .badge{color:var(--pink);font-variant-numeric:tabular-nums}
.tallies{display:grid;gap:11px;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));
  margin:18px 0 6px;padding:0;list-style:none}
.tallies li{border:1px solid var(--line);border-radius:15px;padding:13px 15px;
  background:var(--card);backdrop-filter:blur(10px)}
.tallies .big{font-size:1.9rem;font-weight:800;line-height:1.1;
  font-variant-numeric:tabular-nums;display:block}
.tallies .lbl{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--dim)}
.setrow{border-bottom:1px dashed var(--line);padding:13px 2px}
.setrow .top{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.setrow a{text-decoration:none;font-weight:700;border-bottom:1px solid var(--line)}
.setrow .frac{color:var(--dim);font-size:.88rem;font-variant-numeric:tabular-nums;
  margin-left:auto}
.bar{height:7px;border-radius:99px;background:var(--line);margin-top:9px;
  overflow:hidden}
.bar span{display:block;height:100%;border-radius:99px;
  background:linear-gradient(90deg,var(--grape),var(--pink));
  transition:width .5s cubic-bezier(.34,1.3,.5,1)}
.setrow.done .bar span{background:linear-gradient(90deg,var(--mint),var(--gold))}
.setrow.done .frac{color:var(--mint);font-weight:750}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 0;padding:0;list-style:none}
.chips li a{display:inline-flex;align-items:center;gap:6px;text-decoration:none;
  border:1px solid var(--line);background:var(--card);border-radius:999px;
  padding:5px 13px;font-size:.92rem;transition:transform .15s,border-color .15s}
.chips li a:hover{transform:translateY(-2px);border-color:var(--pink)}
.chips .x{color:var(--gold);font-weight:800;font-variant-numeric:tabular-nums}
.acts{display:flex;flex-wrap:wrap;gap:9px;margin:20px 0 0}
.acts button{font:inherit;font-size:.93rem;font-weight:700;cursor:pointer;
  border:1px solid var(--line);background:var(--card);color:var(--ink);
  padding:9px 17px;border-radius:12px;backdrop-filter:blur(8px);
  transition:transform .16s,border-color .16s}
.acts button:hover{transform:translateY(-2px);border-color:var(--pink)}
.acts button.primary{border-color:transparent;color:#fff;
  background:linear-gradient(120deg,var(--grape),var(--pink))}
.acts button.quiet{color:var(--dim);font-weight:600}
#cardwrap{margin:20px 0 0}
#cardwrap canvas{max-width:100%;height:auto;border-radius:16px;
  border:1px solid var(--line);box-shadow:var(--shadow);display:block}
.said{color:var(--mint);font-size:.9rem;margin-left:4px;align-self:center}
.hidden{display:none !important}
"""

# ---------------------------------------------------------------------------
# JS — shelf state, card controls, shelf page, trade card
# ---------------------------------------------------------------------------
SHELF_JS = r"""
(function(){
  var KEY='poplucky.shelf.v1';
  var state={};
  try{ state=JSON.parse(localStorage.getItem(KEY)||'{}')||{}; }catch(e){ state={}; }

  function save(){
    try{ localStorage.setItem(KEY,JSON.stringify(state)); }catch(e){}
    paintBadge();
  }
  function rec(id){
    if(!state[id]) state[id]={n:0,w:false};
    return state[id];
  }
  function owned(id){ return (state[id]&&state[id].n)||0; }
  function wished(id){ return !!(state[id]&&state[id].w); }
  function tidy(id){
    var r=state[id];
    if(r && !r.n && !r.w) delete state[id];
  }
  function totals(){
    var have=0,uniq=0,dup=0,want=0;
    for(var id in state){
      var r=state[id];
      if(r.n>0){ have+=r.n; uniq++; if(r.n>1) dup+=(r.n-1); }
      if(r.w && !r.n) want++;   /* same rule as the trade card */
    }
    return {have:have,uniq:uniq,dup:dup,want:want};
  }

  /* ---- sparkles ------------------------------------------------------- */
  function celebrate(el){
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    el.classList.remove('just-landed');
    void el.offsetWidth;
    el.classList.add('just-landed');
    var marks=['✨','⭐','🎁'];
    for(var i=0;i<6;i++){
      var s=document.createElement('span');
      s.className='spark';
      s.textContent=marks[i%marks.length];
      var a=(Math.PI*2)*(i/6)-Math.PI/2;
      s.style.setProperty('--dx',Math.round(Math.cos(a)*54)+'px');
      s.style.setProperty('--dy',Math.round(Math.sin(a)*54)+'px');
      s.style.left='50%'; s.style.top='42%';
      el.appendChild(s);
      (function(node){ setTimeout(function(){ node.remove(); },760); })(s);
    }
  }

  /* ---- paint one card ------------------------------------------------- */
  function paintCard(card){
    var id=card.dataset.id, n=owned(id);
    var cnt=card.querySelector('.cnt');
    if(cnt){
      cnt.textContent=n;
      cnt.classList.toggle('zero',n===0);
    }
    card.classList.toggle('owned',n>0);
    card.classList.toggle('dupe',n>1);
    var w=card.querySelector('.wish');
    if(w){
      w.setAttribute('aria-pressed',wished(id)?'true':'false');
      w.disabled = n>0;
      w.title = n>0 ? 'already on your shelf' : 'seeking';
    }
  }
  function paintAll(){
    var cards=document.querySelectorAll('.shelf-item[data-id]');
    for(var i=0;i<cards.length;i++) paintCard(cards[i]);
  }
  function paintBadge(){
    var b=document.querySelector('.shelfnav .badge');
    if(b){
      var t=totals();
      b.textContent=t.uniq?(' '+t.uniq):'';
    }
  }

  /* ---- card control clicks -------------------------------------------- */
  document.addEventListener('click',function(e){
    var btn=e.target.closest('.ctl button');
    if(!btn) return;
    e.preventDefault();
    var card=btn.closest('.shelf-item[data-id]');
    if(!card) return;
    var id=card.dataset.id, act=btn.dataset.act, r=rec(id), was=r.n;
    if(act==='inc') r.n=Math.min(r.n+1,99);
    else if(act==='dec') r.n=Math.max(r.n-1,0);
    else if(act==='wish') r.w=!r.w;
    if(act==='inc' && was===0) celebrate(card);
    if(r.n>0) r.w=false;   /* owning it satisfies seeking it */
    tidy(id); save(); paintCard(card);
    if(window.__shelfRepaint) window.__shelfRepaint();
  });

  paintAll(); paintBadge();

  /* ---- shelf page ------------------------------------------------------ */
  var page=document.getElementById('shelfpage');
  if(!page) return;

  var LANG=function(){ return document.documentElement.lang||'en'; };
  var data=null;

  function nameOf(o){
    if(!o) return '';
    return o['name_'+LANG()] || o.name_en || o.id;
  }

  fetch('/catalog.json').then(function(r){return r.json();}).then(function(d){
    data=d; render();
  }).catch(function(){
    page.innerHTML='<p class="tag">Could not load the catalogue.</p>';
  });

  function render(){
    if(!data) return;
    var figs={}, i;
    for(i=0;i<data.figure.length;i++) figs[data.figure[i].id]=data.figure[i];
    var series={};
    for(i=0;i<data.series.length;i++) series[data.series[i].id]=data.series[i];

    var t=totals();
    var setsTouched={};
    for(var id in state){
      var f=figs[id];
      if(f && state[id].n>0) setsTouched[f.series]=1;
    }
    var nSets=Object.keys(setsTouched).length;

    /* tallies */
    setTxt('t-have',t.have); setTxt('t-uniq',t.uniq);
    setTxt('t-dup',t.dup); setTxt('t-want',t.want);
    setTxt('t-sets',nSets);

    var empty=(t.have===0 && t.want===0);
    tog('emptyshelf',empty);
    tog('shelfbody',!empty);
    if(empty){ return; }

    /* per-set progress */
    var bySeries={};
    for(i=0;i<data.figure.length;i++){
      var fg=data.figure[i];
      (bySeries[fg.series]=bySeries[fg.series]||[]).push(fg);
    }
    var rows=[];
    Object.keys(bySeries).forEach(function(sid){
      var all=bySeries[sid];
      var got=all.filter(function(f){return owned(f.id)>0;}).length;
      if(!got) return;
      var pct=Math.round(got/all.length*100);
      rows.push({sid:sid,got:got,tot:all.length,pct:pct});
    });
    rows.sort(function(a,b){ return b.pct-a.pct || b.got-a.got; });
    document.getElementById('sets').innerHTML = rows.map(function(r){
      var s=series[r.sid]||{id:r.sid};
      return '<div class="setrow'+(r.got===r.tot?' done':'')+'">'
        +'<div class="top"><a href="/series/'+r.sid+'/">'+esc(nameOf(s))+'</a>'
        +'<span class="frac">'+r.got+' / '+r.tot+(r.got===r.tot?' ✓':'')+'</span></div>'
        +'<div class="bar"><span style="width:'+r.pct+'%"></span></div></div>';
    }).join('');

    /* doubles + seeking chips */
    var dupes=[],wants=[];
    for(var id2 in state){
      var f2=figs[id2]; if(!f2) continue;
      if(state[id2].n>1) dupes.push({f:f2,x:state[id2].n-1});
      if(state[id2].w && !state[id2].n) wants.push({f:f2});
    }
    dupes.sort(function(a,b){return b.x-a.x;});
    document.getElementById('dupes').innerHTML = dupes.map(function(d){
      return '<li><a href="/figure/'+d.f.id+'/">'+esc(nameOf(d.f))
        +' <span class="x">×'+d.x+'</span></a></li>';
    }).join('');
    document.getElementById('wants').innerHTML = wants.map(function(d){
      return '<li><a href="/figure/'+d.f.id+'/">'+esc(nameOf(d.f))+'</a></li>';
    }).join('');
    tog('dupesec',dupes.length>0);
    tog('wantsec',wants.length>0);
    tog('tradeable',dupes.length>0||wants.length>0);
    tog('notrade',!(dupes.length>0||wants.length>0));

    window.__trade={dupes:dupes,wants:wants,figs:figs,series:series};
  }
  window.__shelfRepaint=render;

  function setTxt(id,v){ var el=document.getElementById(id); if(el) el.textContent=v; }
  function tog(id,on){ var el=document.getElementById(id);
    if(el) el.classList.toggle('hidden',!on); }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  /* ---- trade card ------------------------------------------------------ */
  function uiText(key){
    var el=document.querySelector('[data-ui="'+key+'"] [data-i18n="'+LANG()+'"]');
    return el?el.textContent:'';
  }

  function drawCard(){
    var T=window.__trade; if(!T) return null;
    var W=1200,H=630,c=document.createElement('canvas');
    c.width=W; c.height=H;
    var g=c.getContext('2d');
    var dark=window.matchMedia('(prefers-color-scheme: dark)').matches;

    var bg=g.createLinearGradient(0,0,W,H);
    if(dark){ bg.addColorStop(0,'#221c2c'); bg.addColorStop(1,'#171420'); }
    else { bg.addColorStop(0,'#fdf6fa'); bg.addColorStop(1,'#f2ecfb'); }
    g.fillStyle=bg; g.fillRect(0,0,W,H);

    var blob=g.createRadialGradient(120,40,10,120,40,520);
    blob.addColorStop(0, dark?'rgba(255,111,165,.22)':'rgba(255,111,165,.30)');
    blob.addColorStop(1,'rgba(255,111,165,0)');
    g.fillStyle=blob; g.fillRect(0,0,W,H);
    var blob2=g.createRadialGradient(W-90,H,10,W-90,H,540);
    blob2.addColorStop(0, dark?'rgba(123,92,255,.24)':'rgba(123,92,255,.28)');
    blob2.addColorStop(1,'rgba(123,92,255,0)');
    g.fillStyle=blob2; g.fillRect(0,0,W,H);

    var stops=['#f7b32b','#ff6fa5','#7b5cff','#3ecfae','#f7b32b'];
    var rib=g.createLinearGradient(0,0,W,0);
    stops.forEach(function(s,i){ rib.addColorStop(i/(stops.length-1),s); });
    g.fillStyle=rib; g.fillRect(0,0,W,12);

    var ink=dark?'#f3eef7':'#241f2b', dim=dark?'#a89fb6':'#6b6377';
    var FS='system-ui,-apple-system,"Noto Sans Thai","Noto Sans SC",sans-serif';

    function head(txt,x,color){
      g.font='700 30px '+FS; g.fillStyle=color;
      g.fillText(txt,x,108);
    }
    function list(items,x,maxw){
      g.font='600 34px '+FS;
      var y=168, shown=0, cap=9;
      for(var i=0;i<items.length && shown<cap;i++,shown++){
        var it=items[i];
        var label=(it.f['name_'+LANG()]||it.f.name_en||it.f.id);
        /* x is SPARES, not total owned — a trade post says what is available */
        if(it.x) label+='  ×'+it.x;
        while(g.measureText(label).width>maxw && label.length>4)
          label=label.slice(0,-2)+'…';
        g.fillStyle=ink;
        g.fillText(label,x,y);
        y+=48;
      }
      if(items.length>cap){
        g.font='400 27px '+FS; g.fillStyle=dim;
        var more=(uiText('and_more')||'and %d more').replace('%d',items.length-cap);
        g.fillText(more,x,y);
      }
    }

    head((uiText('trade_have')||'HAVE'),74,'#ff6fa5');
    list(T.dupes,74,430);
    g.strokeStyle=dark?'rgba(255,255,255,.10)':'rgba(0,0,0,.10)';
    g.lineWidth=2; g.beginPath(); g.moveTo(600,86); g.lineTo(600,H-118); g.stroke();
    head((uiText('trade_want')||'LOOKING FOR'),650,'#7b5cff');
    list(T.wants,650,430);

    g.font='800 32px '+FS; g.fillStyle=ink;
    g.fillText('Poplucky',74,H-52);
    g.font='400 27px '+FS; g.fillStyle=dim;
    g.fillText('poplucky.net',74+g.measureText('Poplucky').width+42,H-52);
    return c;
  }

  function asText(){
    var T=window.__trade; if(!T) return '';
    var L=[];
    function nm(f){ return f['name_'+LANG()]||f.name_en||f.id; }
    if(T.dupes.length){
      L.push((uiText('trade_have')||'HAVE')+':');
      T.dupes.forEach(function(d){ L.push('  '+nm(d.f)+' ×'+d.x); });
    }
    if(T.wants.length){
      if(L.length) L.push('');
      L.push((uiText('trade_want')||'LOOKING FOR')+':');
      T.wants.forEach(function(d){ L.push('  '+nm(d.f)); });
    }
    L.push(''); L.push('poplucky.net');
    return L.join('\n');
  }

  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-shelf]'); if(!b) return;
    var act=b.dataset.shelf;

    if(act==='make'){
      var c=drawCard(); if(!c) return;
      var wrap=document.getElementById('cardwrap');
      wrap.innerHTML=''; wrap.appendChild(c);
      window.__cardCanvas=c;
      tog('cardacts',true);
      c.scrollIntoView({behavior:'smooth',block:'nearest'});
    }
    else if(act==='download'){
      var cv=window.__cardCanvas; if(!cv) return;
      var a=document.createElement('a');
      a.download='poplucky-trade-card.png';
      a.href=cv.toDataURL('image/png');
      a.click();
    }
    else if(act==='copy'){
      var txt=asText();
      var done=function(){ flash(b); };
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(txt).then(done,function(){ fallbackCopy(txt); done(); });
      } else { fallbackCopy(txt); done(); }
    }
    else if(act==='backup'){
      var blob=new Blob([JSON.stringify({app:'poplucky',v:1,shelf:state},null,1)],
        {type:'application/json'});
      var a2=document.createElement('a');
      a2.download='poplucky-shelf-backup.json';
      a2.href=URL.createObjectURL(blob);
      a2.click();
      setTimeout(function(){ URL.revokeObjectURL(a2.href); },2000);
    }
    else if(act==='restore'){
      document.getElementById('restorefile').click();
    }
    else if(act==='clear'){
      if(confirm(uiText('clear_sure')||'Clear the whole shelf?')){
        state={}; save(); paintAll(); render();
      }
    }
  });

  function fallbackCopy(txt){
    var ta=document.createElement('textarea');
    ta.value=txt; ta.style.position='fixed'; ta.style.opacity='0';
    document.body.appendChild(ta); ta.select();
    try{ document.execCommand('copy'); }catch(e){}
    ta.remove();
  }
  function flash(btn){
    var s=btn.parentNode.querySelector('.said');
    if(!s) return;
    s.classList.remove('hidden');
    setTimeout(function(){ s.classList.add('hidden'); },1800);
  }

  var rf=document.getElementById('restorefile');
  if(rf) rf.addEventListener('change',function(){
    var f=rf.files&&rf.files[0]; if(!f) return;
    var fr=new FileReader();
    fr.onload=function(){
      try{
        var d=JSON.parse(fr.result);
        if(!d || d.app!=='poplucky' || typeof d.shelf!=='object') throw 0;
        state=d.shelf||{}; save(); paintAll(); render();
        alert(uiText('restored')||'Shelf restored');
      }catch(e){ alert(uiText('restore_bad')||'That file was not a Poplucky backup'); }
      rf.value='';
    };
    fr.readAsText(f);
  });
})();
"""


# ---------------------------------------------------------------------------
# /shelf/ page body
# ---------------------------------------------------------------------------
def shelf_body(ui_span):
    """ui_span is build.ui_span — renders all three languages, CSS picks one."""
    def u(k):
        return '<span data-ui="%s">%s</span>' % (k, ui_span(k))

    tallies = "".join(
        '<li><span class="big" id="%s">0</span><span class="lbl">%s</span></li>'
        % (tid, ui_span(key))
        for tid, key in [("t-have", "have"), ("t-uniq", "figures_word"),
                         ("t-dup", "doubles"), ("t-want", "seeking"),
                         ("t-sets", "sets")]
    )
    return (
        '<div id="shelfpage">'
        "<h1>%s</h1>" % ui_span("shelf")
        + '<p class="tag">%s</p>' % ui_span("shelf_blurb")
        + '<ul class="tallies">%s</ul>' % tallies
        + '<p class="tag hidden" id="emptyshelf">%s</p>' % ui_span("shelf_empty")
        + '<div id="shelfbody" class="hidden">'
        + "<h2>%s</h2><div id=\"sets\"></div>" % ui_span("series")
        + '<section id="dupesec" class="hidden"><h2>%s</h2>'
          '<ul class="chips" id="dupes"></ul></section>' % ui_span("doubles")
        + '<section id="wantsec" class="hidden"><h2>%s</h2>'
          '<ul class="chips" id="wants"></ul></section>' % ui_span("seeking")
        + "<h2>%s</h2>" % ui_span("tradecard")
        + '<p class="tag hidden" id="notrade">%s</p>' % ui_span("no_trade")
        + '<div id="tradeable" class="hidden">'
        + '<p class="tag">%s</p>' % ui_span("tradecard_hint")
        + '<div class="acts"><button class="primary" data-shelf="make">%s</button></div>'
          % ui_span("tradecard")
        + '<div id="cardwrap"></div>'
        + '<div class="acts hidden" id="cardacts">'
          '<button data-shelf="download">%s</button>'
          '<button data-shelf="copy">%s</button><span class="said hidden">%s</span>'
          "</div>" % (ui_span("download"), ui_span("copytext"), ui_span("copied"))
        + "</div>"
        + '<h2>&nbsp;</h2><div class="acts">'
          '<button data-shelf="backup">%s</button>'
          '<button data-shelf="restore">%s</button>'
          '<button class="quiet" data-shelf="clear">%s</button>'
          '<input type="file" id="restorefile" accept="application/json,.json" '
          'class="hidden">'
          "</div>" % (ui_span("backup"), ui_span("restore"), ui_span("clear"))
        + "</div>"
        # hidden strings the JS reads for alerts and canvas labels
        + '<div class="hidden">%s%s%s%s%s%s</div>'
          % (u("trade_have"), u("trade_want"), u("and_more"), u("clear_sure"),
             u("restored"), u("restore_bad"))
        + "</div>"
    )
