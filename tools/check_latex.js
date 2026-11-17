const fs=require('fs'), katex=require('katex'), MarkdownIt=require('markdown-it');
const md=new MarkdownIt({html:false});
const files=process.argv.slice(2);
let total=0,bad=0;
const css=fs.readFileSync(require.resolve('katex/dist/katex.min.css'),'utf8');
for(const f of files){
  const nb=JSON.parse(fs.readFileSync(f,'utf8'));
  let html='';
  for(const c of nb.cells){
    const src=Array.isArray(c.source)?c.source.join(''):c.source;
    if(c.cell_type==='code'){ if(!src.startsWith('%%writefile')) html+='<pre class="code">'+src.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</pre>'; continue; }
    // pull out math, keep code spans intact
    const store=[]; 
    let t=src.replace(/(`+)([\s\S]*?)\1/g,(m)=>{store.push({k:'code',v:m});return '\u0000'+(store.length-1)+'\u0000';});
    t=t.replace(/\$\$([\s\S]+?)\$\$/g,(m,x)=>{store.push({k:'disp',v:x});return '\u0000'+(store.length-1)+'\u0000';});
    t=t.replace(/\$([^$\n]+?)\$/g,(m,x)=>{store.push({k:'inl',v:x});return '\u0000'+(store.length-1)+'\u0000';});
    if(/\$/.test(t)){bad++;console.log('STRAY $ in',f,':',t.slice(Math.max(0,t.indexOf('$')-40),t.indexOf('$')+40).replace(/\n/g,' '));}
    // pipes inside inline math within a table row would break the table
    for(const line of src.split('\n')){ if(line.trim().startsWith('|')){ const ms=line.match(/\$[^$]+\$/g)||[]; for(const m of ms) if(m.includes('|')){bad++;console.log('PIPE in table math:',m);} } }
    t=t.replace(/\u0000(\d+)\u0000/g,(m,i)=>{const s=store[+i]; if(s.k==='code') return s.v; return 'MATHPH'+i+'X';});
    let h=md.render(t);
    h=h.replace(/MATHPH(\d+)X/g,(m,i)=>{const s=store[+i]; total++;
      try{ return katex.renderToString(s.v,{displayMode:s.k==='disp',throwOnError:true,strict:'error'}); }
      catch(e){ bad++; console.log('KATEX ERROR in',f,':',s.v,'=>',e.message); return '<b style="color:red">'+s.v+'</b>'; }});
    html+='<div class="md">'+h+'</div>';
  }
  const out=f.replace(/.*\//,'').replace('.ipynb','.html');
  fs.writeFileSync(out,`<!doctype html><meta charset="utf-8"><style>${css.replace(/url\(fonts\//g,'url(node_modules/katex/dist/fonts/')}
  body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:20px auto;padding:0 16px}
  table{border-collapse:collapse;margin:10px 0}td,th{border:1px solid #bbb;padding:4px 10px;text-align:left}
  pre.code{background:#f3f3f3;padding:8px 10px;border-radius:4px;font-size:13px;overflow:auto}code{background:#f3f3f3;padding:1px 4px;border-radius:3px}</style>${html}`);
}
console.log('math snippets:',total,' problems:',bad);
