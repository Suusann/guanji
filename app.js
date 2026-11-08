const state={duration:'10分钟',intent:'放松',current:'办公室',desired:'湖边',music:'中式水韵',wuxing:'金',complete:false,paused:false,customTracks:[]};

const wuxingTracks={
  金:{name:'夕阳箫鼓',artist:'群星',src:'assets/wuxing-jin-xiyangxiaogu.m4a',desc:'金 · 箫声悠远，落日铺江'},
  木:{name:'慢六板',artist:'群星',src:'assets/wuxing-mu-manliuban.m4a',desc:'木 · 江南丝竹，节拍舒展'},
  水:{name:'流水行云',artist:'群星',src:'assets/wuxing-shui-liushuixingyun.m4a',desc:'水 · 云影流转，水声潺潺'},
  火:{name:'彩云追月',artist:'群星',src:'assets/wuxing-huo-caiyunzhuiyue.m4a',desc:'火 · 光影摇曳，夜色欢愉'},
  土:{name:'十面埋伏',artist:'张强 & Noble Band',src:'assets/wuxing-tu-shimianmaifu.m4a',desc:'土 · 琵琶激越，大地回响'}
};

const musicThemes=[
  {key:'中式水韵',title:'中式水韵',desc:'古琴、箫、水声',style:'ink',track:{name:'春风又绿江南岸',artist:'李祥霆',src:'assets/guqin-spring.m4a',desc:'中式水韵 · 古琴试听'}},
  {key:'五行灵感',title:'五行灵感',desc:'金、木、水、火、土',style:'ink',wuxing:true},
  {key:'日本留白',title:'日本留白',desc:'尺八、筝、细雨',style:'japan',track:{name:'Haru no Umi 春之海',artist:'吉村七重',src:'assets/japan-haru-no-umi.m4a',desc:'日本留白 · 筝与尺八'}},
  {key:'印尼流光',title:'印尼流光',desc:'甘美兰、雨林、海浪',style:'bali',track:{name:'Bacchanale',artist:'Sanggar Ceraken of Bali',src:'',desc:'印尼流光 · 甘美兰（暂无试听）'}},
  {key:'欧美氛围',title:'欧美氛围',desc:'钢琴双奏、莫扎特 K.448',style:'oil',track:{name:'Sonata for 2 Pianos K.448 · II. Andante',artist:'Clifford Curzon & Benjamin Britten',src:'assets/west-mozart-k448-andante.m4a',desc:'欧美氛围 · 双钢琴慢板'}}
];

const $=s=>document.querySelector(s);
const $$=s=>document.querySelectorAll(s);
const audio=$('#player');

function formatTime(seconds){seconds=Math.max(0,Math.floor(seconds));return String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0')}

function syncAudioUI(){const playing=!audio.paused&&!audio.ended&&audio.currentTime>0;$('#preview-toggle').textContent=playing?'Ⅱ':'▶';$('#practice-audio-toggle').textContent=playing?'Ⅱ':'▶'}

function toast(text){let t=$('#toast');t.textContent=text;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2100)}

function show(id){
  $$('.screen').forEach(x=>x.classList.remove('active'));
  $('#'+id).classList.add('active');
  $('.nav').classList.toggle('hidden',id==='practice');
  if(id!=='practice'){cancelAnimationFrame(window.clockFrame);window.clockFrame=null;if(!audio.paused){audio.pause();syncAudioUI()}}
}

function quick(el,goal){
  $$('.quick button').forEach(x=>x.classList.remove('active'));
  el.classList.add('active');
  const copy={
    放松:['中式水韵 · 今日推荐','此刻，适合听一段\n水声与古琴','今天不必追赶什么，先听一听自己的呼吸。'],
    专注:['欧美氛围 · 今日推荐','此刻，适合听一段\n极简钢琴与风声','把注意力温柔地带回这一刻。'],
    睡前:['日本留白 · 今日推荐','此刻，适合听一场\n细雨与尺八','把白日的喧闹，慢慢放在身后。']
  }[goal];
  $('#art-theme').textContent=copy[0];
  $('#art-copy').innerHTML=copy[1].replace('\n','<br>');
  $('#home-sub').textContent=copy[2];
  state.intent=goal;
}

function renderMusicList(){
  const list=$('#music-list');
  list.innerHTML='';
  musicThemes.forEach(theme=>{
    const btn=document.createElement('button');
    btn.className='music'+(state.music===theme.key?' selected':'');
    btn.innerHTML='<b>'+theme.title+'</b><span>'+theme.desc+'</span>';
    btn.onclick=()=>{state.music=theme.key;renderMusicList();renderWuxing();loadCurrentTrack()};
    list.appendChild(btn);
  });
}

function renderWuxing(){
  const wrap=$('#wuxing');
  const theme=musicThemes.find(t=>t.key===state.music);
  if(!theme?.wuxing){wrap.hidden=true;wrap.innerHTML='';return}
  wrap.hidden=false;
  wrap.innerHTML='';
  Object.keys(wuxingTracks).forEach(el=>{
    const btn=document.createElement('button');
    btn.dataset.el=el;
    btn.className=state.wuxing===el?'selected':'';
    btn.textContent=el;
    btn.onclick=()=>{state.wuxing=el;renderWuxing();loadCurrentTrack()};
    wrap.appendChild(btn);
  });
}

function renderCustom(){
  const wrap=$('#custom-list');
  wrap.innerHTML='';
  state.customTracks.forEach((t,i)=>{
    const row=document.createElement('div');
    row.className='custom-item';
    row.innerHTML='<div><b>'+t.name+'</b> <span>· 我的疗愈音乐</span></div>';
    const use=document.createElement('button');
    use.textContent=state.customIndex===i?'使用中':'选用';
    use.onclick=()=>{state.music='自定义';state.customIndex=i;renderMusicList();renderWuxing();renderCustom();loadCurrentTrack()};
    const del=document.createElement('button');
    del.textContent='移除';
    del.onclick=()=>{URL.revokeObjectURL(t.src);state.customTracks.splice(i,1);if(state.customIndex===i){state.music='中式水韵';state.customIndex=null}renderCustom();renderMusicList();loadCurrentTrack()};
    row.appendChild(use);row.appendChild(del);
    wrap.appendChild(row);
  });
}

function currentTrack(){
  if(state.music==='自定义'&&state.customTracks[state.customIndex])return {...state.customTracks[state.customIndex],desc:'我的疗愈音乐'};
  const theme=musicThemes.find(t=>t.key===state.music);
  if(!theme)return null;
  if(theme.wuxing)return wuxingTracks[state.wuxing];
  return theme.track;
}

function loadCurrentTrack(){
  const t=currentTrack();
  if(!t){return}
  const wasPlaying=!audio.paused;
  audio.pause();
  audio.src=t.src||'';
  $('#track-name').textContent=t.artist?t.artist+' · '+t.name:t.name;
  $('#track-desc').textContent=t.desc||'';
  $('#practice-track').textContent=t.artist?t.artist+' · '+t.name:t.name;
  $('#audio-current').textContent='00:00';
  $('#audio-duration').textContent=t.src?'加载中':'暂无试听';
  $('#audio-progress').value=0;
  syncAudioUI();
  if(wasPlaying&&t.src){audio.play().catch(()=>{})}
}

function toggleAudio(){
  const t=currentTrack();
  if(!t||!t.src){toast('这首暂无试听音源');return}
  if(audio.paused){audio.play().then(syncAudioUI).catch(()=>toast('请再次点击播放'))}
  else{audio.pause();syncAudioUI()}
}

function seekAudio(v){if(Number.isFinite(audio.duration))audio.currentTime=audio.duration*v/100}

audio.addEventListener('loadedmetadata',()=>{$('#audio-duration').textContent=formatTime(audio.duration)});
audio.addEventListener('timeupdate',()=>{const p=audio.duration?audio.currentTime/audio.duration*100:0;$('#audio-progress').value=p;$('#audio-current').textContent=formatTime(audio.currentTime)});
audio.addEventListener('play',syncAudioUI);
audio.addEventListener('pause',syncAudioUI);
audio.addEventListener('ended',syncAudioUI);
audio.addEventListener('error',()=>{$('#audio-duration').textContent='加载失败';syncAudioUI()});

function openImport(){$('#import-input').click()}
$('#import-input').addEventListener('change',e=>{
  const files=[...e.target.files];
  files.forEach(f=>{
    const url=URL.createObjectURL(f);
    state.customTracks.push({name:f.name.replace(/\.[^.]+$/,''),artist:'我的疗愈音乐',src:url});
  });
  e.target.value='';
  if(files.length){state.music='自定义';state.customIndex=state.customTracks.length-1;toast('已加入 '+files.length+' 首音乐')}
  renderCustom();renderMusicList();renderWuxing();loadCurrentTrack();
});

$$('[data-group]').forEach(group=>group.addEventListener('click',e=>{
  if(!e.target.matches('button'))return;
  group.querySelectorAll('button').forEach(b=>b.classList.remove('selected'));
  e.target.classList.add('selected');
  const k=group.dataset.group;
  state[k]=e.target.querySelector('b')?.textContent||e.target.textContent;
}));

function startPractice(){
  const phases=[{label:'吸气',seconds:4,tip:'让气息慢慢落下'},{label:'停留',seconds:7,tip:'停在安静里'},{label:'呼气',seconds:8,tip:'把紧绷轻轻放开'}];
  const phaseDuration=phases.reduce((s,p)=>s+p.seconds,0)*1000;
  show('practice');
  cancelAnimationFrame(window.clockFrame);
  state.paused=false;
  $('#pause').textContent='暂停';
  state.durationMs=(parseInt(state.duration,10)||10)*60*1000;
  state.startedAt=Date.now();
  function render(){
    const elapsed=Math.max(0,Date.now()-state.startedAt);
    const remaining=Math.max(0,state.durationMs-elapsed);
    $('#timer').textContent=formatTime(Math.ceil(remaining/1000));
    const phaseElapsed=elapsed%phaseDuration;
    let acc=0,phase=phases[0];
    for(const item of phases){if(phaseElapsed<acc+item.seconds*1000){phase=item;break}acc+=item.seconds*1000}
    const phaseRemaining=Math.max(1,Math.ceil((acc+phase.seconds*1000-phaseElapsed)/1000));
    $('#phase').textContent=phase.label+' '+phaseRemaining;
    $('#phase-tip').textContent=phase.tip;
    $('#live-hr').textContent=(70+(phase.label==='停留'?1:0))+' bpm';
    if(remaining===0){endPractice();return}
    window.clockFrame=requestAnimationFrame(render);
  }
  startPractice.render=render;
  $('#practice .ripple').style.animationPlayState='running';
  render();
  if(currentTrack()?.src){audio.play().then(syncAudioUI).catch(()=>syncAudioUI())}
}

function togglePause(){
  if(state.paused){
    state.paused=false;
    state.startedAt+=Date.now()-state.pausedAt;
    $('#pause').textContent='暂停';
    $('#practice .ripple').style.animationPlayState='running';
    window.clockFrame=requestAnimationFrame(startPractice.render);
    if(currentTrack()?.src)audio.play().catch(()=>{});
  }else{
    state.paused=true;
    state.pausedAt=Date.now();
    $('#pause').textContent='继续';
    cancelAnimationFrame(window.clockFrame);
    window.clockFrame=null;
    $('#practice .ripple').style.animationPlayState='paused';
    if(!audio.paused)audio.pause();
  }
  syncAudioUI();
}

function endPractice(){
  cancelAnimationFrame(window.clockFrame);
  window.clockFrame=null;
  state.paused=false;
  audio.pause();
  syncAudioUI();
  show('report');
  const t=currentTrack();
  $('#report-summary').textContent=state.duration+' · '+(t?t.artist+' · '+t.name:state.music)+' · '+state.desired;
}

function currentStyle(){
  const theme=musicThemes.find(t=>t.key===state.music);
  if(state.music==='自定义')return 'ink';
  return theme?.style||'ink';
}

function tempoLevel(){
  const map={金:2,木:2,水:1,火:3,土:4};
  if(state.music==='五行灵感')return map[state.wuxing]||2;
  return {中式水韵:2,日本留白:1,印尼流光:3,欧美氛围:2,自定义:2}[state.music]||2;
}

function paintingSvg(style,tempo){
  const density=6+tempo*6;
  const strokes=[];
  for(let i=0;i<density;i++){
    const y=40+i*(260/density)+Math.sin(i)*4;
    strokes.push(`<path d="M0 ${y.toFixed(1)} Q ${88+i*3} ${(y-8-tempo*2).toFixed(1)} ${176} ${y.toFixed(1)} T 353 ${(y+2).toFixed(1)}" fill="none" stroke-width="${(0.6+tempo*0.2).toFixed(2)}"/>`);
  }
  if(style==='ink'){
    return `<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#f4f2e8"/><stop offset="1" stop-color="#c5cdc1"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><g stroke="#20303a" opacity=".55">${strokes.join('')}</g><path d="M-10 220 Q80 150 170 210 T370 200 V340 H-10Z" fill="#2f4a4a" opacity=".78"/><path d="M-10 258 Q100 218 190 250 T370 244 V340 H-10Z" fill="#4a6a63" opacity=".82"/><circle cx="278" cy="70" r="26" fill="#f8f2d8" opacity=".85"/><g stroke="#f5f1e0" stroke-width="1" opacity=".6"><path d="M20 296 Q140 282 240 300 T348 292"/><path d="M0 314 Q120 300 220 316 T350 310"/></g></svg>`;
  }
  if(style==='japan'){
    return `<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#f6ecdc"/><stop offset="1" stop-color="#e2b499"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><circle cx="240" cy="96" r="52" fill="#d64b3a"/><g stroke="#1a1a1a" opacity=".22" stroke-width="0.8">${strokes.join('')}</g><path d="M-10 244 Q90 200 190 236 T370 228 V340 H-10Z" fill="#5b3a2a"/><path d="M-10 274 Q120 254 220 274 T370 268 V340 H-10Z" fill="#8a5a3c" opacity=".9"/><g fill="#1a1a1a" opacity=".6"><path d="M60 260 l4 -30 l4 30z"/><path d="M120 268 l4 -34 l4 34z"/><path d="M280 262 l4 -32 l4 32z"/></g></svg>`;
  }
  if(style==='bali'){
    return `<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#ffb56b"/><stop offset=".5" stop-color="#ff7a59"/><stop offset="1" stop-color="#264d63"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><circle cx="270" cy="80" r="34" fill="#ffe6a8" opacity=".95"/><g stroke="#ffe6a8" opacity=".55">${strokes.join('')}</g><path d="M-10 240 Q120 210 240 240 T370 232 V340 H-10Z" fill="#0f3040"/><g fill="#0f3040"><path d="M40 240 q10 -80 22 -90 q4 30 -6 90z"/><path d="M280 232 q8 -70 24 -84 q4 30 -8 84z"/><path d="M170 236 q-4 -60 -20 -78 q-4 20 8 78z"/></g><g stroke="#ffe6a8" stroke-width="1" opacity=".7"><path d="M0 300 Q80 288 170 300 T353 296"/><path d="M0 318 Q100 306 200 318 T353 314"/></g></svg>`;
  }
  if(style==='oil'){
    return `<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#c9a778"/><stop offset=".5" stop-color="#6a7d5b"/><stop offset="1" stop-color="#2d3a3c"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><g stroke="#f2d69a" opacity=".55" stroke-linecap="round">${strokes.join('')}</g><path d="M-10 214 Q60 170 130 210 Q200 250 260 200 Q320 160 370 210 V340 H-10Z" fill="#3f4a37" opacity=".9"/><path d="M-10 258 Q100 224 210 260 T370 252 V340 H-10Z" fill="#233028" opacity=".92"/><circle cx="260" cy="82" r="28" fill="#f6e2b0" opacity=".9"/><circle cx="260" cy="82" r="48" fill="#f6e2b0" opacity=".18"/></svg>`;
  }
  return '';
}

function styleLabel(style){return {ink:'国风水墨',japan:'日本画',bali:'印尼海洋椰林',oil:'欧美油画'}[style]||'国风水墨'}

function generateArt(){
  const load=$('#loader'),words=['收集呼吸','聆听'+(currentTrack()?.artist||'音乐'),'描绘此刻'];
  load.classList.add('show');
  words.forEach((w,i)=>setTimeout(()=>$('#load-word').textContent=w,i*850));
  setTimeout(()=>{
    load.classList.remove('show');
    const style=currentStyle();
    const tempo=tempoLevel();
    $('#painting').innerHTML=paintingSvg(style,tempo);
    $('#style-badge').textContent=styleLabel(style)+' · 细腻度 '+tempo+'/4';
    const t=currentTrack();
    $('#painting-name').textContent={ink:'湖上微光',japan:'春之海',bali:'椰林潮声',oil:'夜色行板'}[style];
    $('#painting-desc').textContent='画面的笔触密度，来自 '+(t?t.name:state.music)+' 的节奏。' + {ink:'水墨在纸上慢慢晕开。',japan:'留白之间，只余一枚红日与筝声。',bali:'海风穿过椰林，色彩层层叠叠。',oil:'油彩堆叠出光影，如一段慢板。'}[style];
    $('#art-tags').innerHTML=[state.duration,'心率趋稳',state.music==='五行灵感'?'五行 · '+state.wuxing:state.music,state.desired,styleLabel(style)].map(x=>'<span class="tag">'+x+'</span>').join('');
    show('art');
  },2700);
}

function saveArt(){let b=$('#save-btn');b.classList.toggle('saved');b.textContent=b.classList.contains('saved')?'已收藏':'收藏画作';toast(b.classList.contains('saved')?'已收藏到你的心境画册':'已取消收藏')}
function completeHome(){state.complete=true;$('#status-title').textContent='今日状态 · 已完成一次观己';show('home');toast('今天的心境，已经被好好收藏')}

$('#thumbs').addEventListener('click',e=>{
  if(!e.target.matches('.thumb'))return;
  $$('.thumb').forEach(x=>x.classList.remove('active'));
  e.target.classList.add('active');
  const i=[...$$('.thumb')].indexOf(e.target);
  const names=['雾中远山','苔色庭园','静海浮光','暮云缓行','山雨将至','星河微眠','湖上微光'];
  $('#painting-name').textContent=names[i];
  $('#painting-desc').textContent=i===6?'湖面的纹理由你的呼吸节奏绘成。远处的微光，来自冥想后你选择的平静。':'这是你在另一日留给自己的安静一瞥。';
  toast('正在回看 '+names[i]);
});

renderMusicList();
renderWuxing();
renderCustom();
loadCurrentTrack();
