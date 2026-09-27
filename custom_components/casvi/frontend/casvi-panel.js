/* Bundled school panel. Private text is inserted with textContent, never HTML. */
class CasviSchoolPanel extends HTMLElement {
  constructor() {
    super(); this.attachShadow({mode: 'open'}); this.accounts = []; this.loading = false; this.view='home'; this.offset=0;
    this.shadowRoot.innerHTML = `
      <style>
        :host {display:block;height:100%;overflow:auto;background:var(--primary-background-color,#f6f8fb);color:var(--primary-text-color,#203344);font:16px/1.5 var(--paper-font-body1_-_font-family,system-ui,sans-serif)}
        *{box-sizing:border-box} main{max-width:1160px;margin:auto;padding:28px 30px 64px} header{display:flex;align-items:center;gap:16px;margin-bottom:28px} h1{font-size:34px;font-weight:650;letter-spacing:-1px;margin:0} .subtitle{color:var(--secondary-text-color,#526575);margin:2px 0 0} .spacer{flex:1} button,select,a{font:inherit} button,select{border:1px solid var(--divider-color,#bcc9d1);border-radius:8px;padding:10px 14px;background:var(--card-background-color,white);color:inherit} button{cursor:pointer} button:hover{border-color:#12677b} button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #d79a25;outline-offset:3px} button:disabled{opacity:.6;cursor:wait} a{color:var(--primary-color,#12677b)} .grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:28px;align-items:start} h2{font-size:21px;font-weight:650;margin:0 0 16px} .menu{background:var(--card-background-color,white);border-top:6px solid #12677b;border-radius:4px;padding:24px;margin-bottom:30px}.date{color:var(--secondary-text-color,#526575);font-size:14px}.menu p{white-space:pre-wrap;line-height:1.85;margin-bottom:0} .row{display:block;width:100%;text-align:left;border:0;border-bottom:1px solid var(--divider-color,#dce3e8);border-radius:0;padding:18px 8px;background:transparent}.row:hover{background:var(--secondary-background-color,#edf3f7)}.subject{display:block;font-weight:600;line-height:1.4}.excerpt{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:14px;line-height:1.5;margin-top:7px;color:var(--secondary-text-color,#526575);overflow-wrap:anywhere}.meta{display:block;font-size:14px;color:var(--secondary-text-color,#526575);margin-top:6px}.badge{display:inline-block;font-size:12px;color:#09586c;background:#e2f3f6;border-radius:4px;padding:2px 7px;margin-bottom:7px}.toolbar{display:flex;gap:12px;align-items:center;margin-bottom:12px}.toolbar h2{margin:0;flex:1}.hint{font-size:14px;color:var(--secondary-text-color,#526575)}.error{border-left:4px solid #b74532;padding:12px;background:var(--card-background-color,white);margin-bottom:18px}.events{padding:0;list-style:none}.events li{padding:12px 0;border-bottom:1px solid var(--divider-color,#dce3e8)}.events strong{display:block} .empty{padding:20px 0;color:var(--secondary-text-color,#526575)}dialog{background:var(--card-background-color,white);color:inherit;border:0;border-radius:12px;max-width:720px;width:calc(100% - 32px);max-height:85vh;padding:26px;box-shadow:0 10px 60px #0004}dialog::backdrop{background:#10253588}.body{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.8}.dialog-head{display:flex;gap:15px;align-items:start}.dialog-head h2{flex:1}.links{margin-top:24px} [hidden]{display:none!important} @media(max-width:720px){main{padding:18px 18px 48px}.grid{grid-template-columns:1fr;gap:8px}h1{font-size:29px}header{gap:10px;flex-wrap:wrap}.toolbar{flex-wrap:wrap}.menu{margin-bottom:22px}.row{padding:16px 0}dialog{padding:20px}}

        nav{display:flex;gap:8px;overflow:auto;margin:0 0 24px;padding-bottom:8px}nav button{display:inline-flex;align-items:center;gap:8px;white-space:nowrap;border-color:transparent;background:transparent}nav button[aria-selected="true"]{background:#12677b;color:white} .grid.inbox{display:block;margin-bottom:28px}.recipient{display:block;font-size:13px;color:var(--primary-color,#12677b);margin-top:6px}.pager{display:flex;gap:12px;align-items:center;justify-content:space-between;margin:20px 0}.child-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:28px}.child-heading{margin-bottom:24px}.people{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;list-style:decimal inside;padding:0;width:100%}.people li::marker{font-weight:600;color:var(--primary-color,#12677b)}.people li{background:var(--card-background-color,white);padding:6px 12px;border-radius:6px}.tutorial{border-bottom:1px solid var(--divider-color,#dce3e8);padding:16px 0}.tutorial h3{margin:0;font-size:17px}.tutorial p{white-space:pre-wrap}.document-list{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}.pdf{display:block;width:100%;height:auto;border:0;margin-top:12px;background:white}.pdf-link{display:block;margin:12px 0} @media(max-width:720px){.child-grid{grid-template-columns:1fr}.pager{flex-wrap:wrap}}

        .teachers{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:0 0 30px}.teacher{display:flex;gap:16px;padding:16px;background:var(--card-background-color,white);border:1px solid var(--divider-color,#dce3e8);border-radius:8px;min-width:0}.portrait{flex:0 0 80px;height:100px;display:flex;align-items:center;justify-content:center;background:var(--secondary-background-color,#edf3f7);border-radius:6px;overflow:hidden;color:var(--secondary-text-color,#526575);font-size:13px}.portrait img{width:100%;height:100%;object-fit:cover;object-position:top}.teacher h3{font-size:17px;margin:0 0 6px;overflow-wrap:anywhere}.teacher p{font-size:14px;color:var(--secondary-text-color,#526575);margin:0}.teacher-details{min-width:0}
      .schedule-section{margin:0 0 30px;padding:22px;background:var(--card-background-color,white);border-radius:8px}.schedule-status{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.schedule-status span{display:inline-flex;align-items:center;gap:7px;padding:7px 12px;border-radius:6px;background:var(--secondary-background-color,#edf3f7);font-size:14px}.schedule-status .active{background:#e2f3f6;color:#09586c}.schedule-table{overflow:auto}.schedule-table table{border-collapse:collapse;width:100%;font-size:14px}.schedule-table th,.schedule-table td{padding:10px;text-align:left;border-bottom:1px solid var(--divider-color,#dce3e8);vertical-align:top}.schedule-table th{white-space:nowrap}.schedule-table.week table{table-layout:fixed;min-width:620px}.schedule-table.week th,.schedule-table.week td{min-width:0;white-space:normal;overflow-wrap:anywhere;padding:9px 7px;font-size:13px}.schedule-table.week th:first-child{width:100px;white-space:nowrap}.schedule-section details{margin-top:18px}.schedule-section summary{cursor:pointer}
      .meal-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr) minmax(0,1fr);gap:18px;margin-bottom:28px;align-items:stretch}.meal-row .menu{margin:0;padding:20px;border-top-color:var(--divider-color,#bcc9d1);overflow-wrap:anywhere}.meal-row .today{border-top-color:#12677b;box-shadow:0 0 0 1px #12677b33}.meal-row h2{font-size:19px;margin:9px 0}.meal-row .today h2{color:var(--primary-color,#12677b)} .meal-controls{display:none}@media(max-width:600px){.meal-row{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;overscroll-behavior-x:contain;scrollbar-width:none;margin-bottom:12px}.meal-row::-webkit-scrollbar{display:none}.meal-row .menu{flex:0 0 100%;min-width:0;scroll-snap-align:start;scroll-snap-stop:always;padding:20px}.meal-row h2{font-size:21px}.meal-row .date{font-size:14px}.meal-row p{font-size:16px;line-height:1.7}.meal-controls{display:flex;justify-content:center;gap:8px;margin-bottom:28px}.meal-controls button{display:flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;border:0;border-radius:50%;background:transparent}.meal-controls button::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--divider-color,#bcc9d1)}.meal-controls button[aria-pressed="true"]::before{background:var(--primary-color,#12677b);transform:scale(1.25)}}
      .home-schedule-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:20px;margin-bottom:28px}.home-schedule-cards .schedule-section{margin:0;min-width:0}.home-schedule-cards h3{margin:0;font-size:20px}
      .schedule-status svg{flex-shrink:0}
      #account:not([hidden]){display:block;margin-bottom:20px}
      .modal-close{display:inline-flex;align-items:center;justify-content:center;flex:0 0 40px;width:40px;height:40px;padding:8px;border:0;border-radius:50%;background:transparent}.modal-close:hover{background:var(--secondary-background-color,#edf3f7)}.dialog-head h2{margin:4px 0 0;overflow-wrap:anywhere}.body.message-body{white-space:normal;line-height:1.65}.message-body p{margin:0 0 1em}.message-body p:last-child{margin-bottom:0}
      #sender{margin:2px 0 14px;line-height:1.4}.dialog-head{gap:10px}
      .loader{display:flex;align-items:center;justify-content:center;width:100%;min-height:64px;margin:0 auto}.portrait .loader{height:100%;min-height:0}.spinner{display:block;width:24px;height:24px;border:3px solid var(--divider-color,#dce3e8);border-top-color:var(--primary-color,#12677b);border-radius:50%;animation:casvi-spin .8s linear infinite}@keyframes casvi-spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.spinner{animation-duration:2.5s}}
      .panel-navigation{display:flex;align-items:flex-start;gap:8px}.panel-navigation nav{flex:1;min-width:0}#sidebar-toggle{display:none;flex:0 0 44px;width:44px;height:44px;align-items:center;justify-content:center;padding:10px;border:0;background:transparent}@media(max-width:870px){#sidebar-toggle{display:inline-flex}}
      .message-body div{margin:0}.message-body ul,.message-body ol{padding-left:1.5em;margin:.6em 0 1em}.message-body li{margin:.25em 0}.message-body blockquote{margin:1em 0;padding-left:1em;border-left:3px solid var(--divider-color,#dce3e8)}.message-body h1,.message-body h2,.message-body h3,.message-body h4{font-size:1.1em;margin:1em 0 .5em}.message-body p:empty{display:none}
      .month-scroll{overflow-x:auto}.month-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;min-width:600px}.month-weekday{text-align:center;font-weight:600;padding:8px}.month-day{padding:10px;min-height:150px;border:1px solid var(--divider-color,#dce3e8);border-radius:6px;background:var(--card-background-color,white)}.month-day.today{border:2px solid var(--primary-color,#12677b)}.month-day p{font-size:13px;white-space:pre-line;overflow-wrap:anywhere;margin:8px 0 0}.month-day time{font-weight:650}.month-day.empty-day{background:transparent;border:0}.month-toolbar{display:block;width:100%}.month-toolbar h2{width:100%;margin:0;text-transform:capitalize;text-align:center}
      #mobile-section{display:none;position:relative}#mobile-section summary{display:flex;align-items:center;justify-content:space-between;gap:12px;list-style:none;cursor:pointer;border:1px solid var(--divider-color,#dce3e8);border-radius:12px;padding:12px 16px;background:var(--card-background-color,white);min-height:50px;box-shadow:0 2px 8px #10253506}#mobile-section summary::-webkit-details-marker{display:none}#mobile-current{display:flex;align-items:center;gap:12px;font-weight:600}#mobile-current svg{color:var(--primary-color,#12677b)}.section-chevron{color:var(--secondary-text-color,#526575);transition:transform .15s}#mobile-section[open] .section-chevron{transform:rotate(180deg)}#mobile-section[open] summary{border-color:var(--primary-color,#12677b)}#mobile-section summary:focus-visible{outline:3px solid #d79a25;outline-offset:3px}#mobile-options{position:absolute;top:calc(100% + 8px);left:0;right:0;z-index:20;padding:6px;background:var(--card-background-color,white);border:1px solid var(--divider-color,#dce3e8);border-radius:14px;box-shadow:0 12px 32px #10253522;max-height:60vh;overflow:auto}#mobile-options button{display:flex;align-items:center;gap:12px;width:100%;border:0;border-radius:9px;padding:12px;text-align:left;background:transparent}#mobile-options button[aria-current="page"]{background:var(--secondary-background-color,#e2f3f6);color:var(--primary-color,#12677b);font-weight:600}#mobile-options button[aria-current="page"]::after{content:'✓';margin-left:auto}#mobile-options button:hover{background:var(--secondary-background-color,#edf3f7)}@media(max-width:600px){.panel-navigation nav{display:none}#mobile-section{display:block;flex:1;min-width:0;width:100%}.panel-navigation{align-items:center;margin-bottom:24px}}

      </style>
      <main>
        <select id="account" aria-label="Cuenta familiar" hidden></select>
        <div class="panel-navigation"><button id="sidebar-toggle" aria-label="Abrir menú lateral" title="Abrir menú lateral"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button><details id="mobile-section"><summary aria-label="Elegir sección"><span id="mobile-current"></span><svg class="section-chevron" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></summary><div id="mobile-options" aria-label="Secciones del colegio"></div></details><nav id="tabs" aria-label="Secciones del colegio" role="tablist"></nav></div><div id="error" role="status" class="error" hidden></div><div id="loading"></div>
        <section id="meal-row" class="meal-row" aria-label="Menús del comedor" tabindex="0" hidden></section><div id="meal-controls" class="meal-controls" aria-label="Día del menú" hidden></div><div id="content" class="grid" hidden>
          <section><div class="toolbar"><h2 id="messages-title">Últimos mensajes</h2><button id="filter" aria-pressed="false">Solo pendientes</button></div><p id="count" class="hint"></p><div id="messages"></div><div id="pager" class="pager" hidden><button id="previous">Anterior</button><span id="page-label"></span><button id="next">Siguiente</button></div></section>
        </div>
        <section id="home-schedules" hidden><h2>Clases de hoy</h2><div id="home-schedule-cards" class="home-schedule-cards"></div></section>
        <section id="dining-view" hidden><div class="toolbar month-toolbar"><h2 id="month-title"></h2></div><div id="month-status" role="status"></div><div class="month-scroll"><div id="month-grid" class="month-grid"></div></div></section>
        <section id="child-view" hidden><div class="child-heading"><h2 id="child-name"></h2><p id="child-group"></p><p id="child-tutor"></p><p id="child-status" role="status"></p></div><section id="schedule-section" class="schedule-section" hidden><h2>Horario semanal</h2><p id="schedule-note" class="hint"></p><div id="schedule-week-table" class="schedule-table week"></div></section><section id="teacher-section"><h2>Profesores</h2><div id="teachers" class="teachers"></div></section><section id="child-data"><h2>Compañeros de clase</h2><ol id="classmates" class="people"></ol></section></section>
        <dialog><div class="dialog-head"><h2 id="subject"></h2><button id="close" class="modal-close" aria-label="Cerrar mensaje" title="Cerrar"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div><p id="sender" class="hint"></p><div id="body" class="body" role="status"></div><div id="attachments"></div></dialog>
      </main>`;
    this.shadowRoot.addEventListener('click',event=>{if(!this.$('mobile-section').contains(event.target))this.$('mobile-section').open=false;});
    this.$('mobile-section').addEventListener('keydown',event=>{if(event.key==='Escape'){this.$('mobile-section').open=false;this.$('mobile-section').querySelector('summary').focus();}});
    this.$('sidebar-toggle').onclick=()=>this.dispatchEvent(new Event('hass-toggle-menu',{bubbles:true,composed:true}));
    this.mealIndex=1;
    this.$('meal-controls').replaceChildren(...['Ayer','Hoy','Mañana'].map((label,index)=>{const button=document.createElement('button');button.setAttribute('aria-label',label);button.title=label;button.onclick=()=>{this.mealIndex=index;this.positionMeal(true);};return button;}));
    this.$('meal-row').onscroll=()=>{if(!matchMedia('(max-width:600px)').matches)return;const row=this.$('meal-row');if(!row.clientWidth)return;this.mealIndex=Math.max(0,Math.min(2,Math.round(row.scrollLeft/(row.clientWidth+12))));this.updateMealControls();};
    this.$('meal-row').onkeydown=event=>{if(!matchMedia('(max-width:600px)').matches||!['ArrowLeft','ArrowRight'].includes(event.key))return;event.preventDefault();this.mealIndex=Math.max(0,Math.min(2,this.mealIndex+(event.key==='ArrowRight'?1:-1)));this.positionMeal(true);};
    this.mealResize=new ResizeObserver(()=>this.positionMeal());
    this.$('loading').append(this.loader('Cargando el colegio'));
    this.$('account').onchange = () => {this.page=null;this.profile=null;this.navigate('home');};
    this.$('previous').onclick=()=>this.loadPage(Math.max(0,this.offset-20));
    this.$('next').onclick=()=>this.loadPage(this.offset+20);
    this.$('filter').onclick = () => {this.onlyUnread = !this.onlyUnread; this.render();};
    this.shadowRoot.querySelector('dialog').addEventListener('close',()=>{this.requestId=(this.requestId||0)+1;this.clearPDF();});
    this.$('close').onclick = () => {this.requestId = (this.requestId || 0) + 1; this.shadowRoot.querySelector('dialog').close(); this.clearPDF();};
  }
  loader(label){
    const status=document.createElement('span');status.className='loader';status.setAttribute('role','status');status.setAttribute('aria-label',label);
    const ring=document.createElement('span');ring.className='spinner';ring.setAttribute('aria-hidden','true');status.append(ring);return status;
  }
  $(id) {return this.shadowRoot.getElementById(id);}
  set hass(value) {this._hass=value; if(this.isConnected && !this.started){this.started=true; this.load(true);} this.handleDeepLink();}
  set route(value) {this._route=value; this.handleDeepLink();}
  connectedCallback() {this.mealResize.observe(this.$('meal-row'));if(this._hass && !this.started){this.started=true;this.load(true);} this.timer=setInterval(()=>this.load(),30000);}
  disconnectedCallback() {this.mealResize.disconnect();this.homeRequest=(this.homeRequest||0)+1;clearInterval(this.timer);this.clearPDF();this.started=false;}
  async load(refresh=false) {
    if(!this._hass) return;
    if(this.loading){this.refreshPending=this.refreshPending||refresh;return;}
    this.loading=true;
    try {
      this.accounts=await this._hass.callWS({type:'casvi/overview',refresh});
      const previous=this.$('account').value;
      this.$('account').replaceChildren(...this.accounts.map(a=>{const o=document.createElement('option');o.value=a.entry_id;o.textContent=a.name;return o;}));
      if(this.accounts.some(a=>a.entry_id===previous)) this.$('account').value=previous;
      this.$('account').hidden=this.accounts.length<2;
      this.$('error').hidden=true; this.render();
      if(this.view==='home'&&(refresh||!this.homeProfiles))this.loadHomeSchedules();
      this.handleDeepLink();
    } catch (_) {this.$('error').textContent='No se pudo cargar el panel. Comprueba la conexión y que tu usuario sea administrador.';this.$('error').hidden=false;}
    finally {this.loading=false;this.$('loading').hidden=true;if(this.refreshPending){this.refreshPending=false;this.load(true);}}
  }
  handleDeepLink() {
    if(!this._hass || !this.accounts.length) return;
    const search=window.location.search;
    if(this.lastDeepLink===search) return;
    this.lastDeepLink=search;
    const q=new URLSearchParams(search);
    const account=this.accounts.find(a=>a.entry_id===q.get('entry'));
    if(account && q.get('message') && q.get('recipient')){
      this.$('account').value=account.entry_id;this.render();
      this.openMessage(account.entry_id,q.get('message'),q.get('recipient'));
    }
  }
  render() {
    const a=this.accounts.find(a=>a.entry_id===this.$('account').value)||this.accounts[0];
    this.$('meal-row').hidden=!a||this.view!=='home';
    this.$('meal-controls').hidden=!a||this.view!=='home';
    this.$('home-schedules').hidden=!a||this.view!=='home';
    if(a&&this.view==='home')this.renderHomeSchedules(a);
    this.$('content').hidden=!a || this.view.startsWith('child:') || this.view==='dining';
    this.$('dining-view').hidden=!a||this.view!=='dining';
    this.$('child-view').hidden=!a || !this.view.startsWith('child:');
    if(!a){this.$('error').textContent='Añade tu cuenta en Ajustes → Dispositivos y servicios → Casvi.';this.$('error').hidden=false;return;}
    this.renderTabs(a);
    if(this.view==='dining')return;
    if(this.view.startsWith('child:')) {this.renderChild(a);return;}
    this.$('content').classList.add('inbox');
    this.$('messages-title').textContent=this.view==='messages'?'Todos los mensajes':`Mensajes no leídos (${a.messages.filter(m=>!m.read).length})`;
    this.$('filter').hidden=true;
    this.$('pager').hidden=this.view!=='messages';
    if(!a.available){this.$('error').textContent='Casvi no está disponible. Se muestran los últimos datos recibidos.';this.$('error').hidden=false;}
    this.renderMeals(a);
    this.$('count').hidden=this.view!=='messages';
    this.$('count').textContent=this.view==='messages'?`${this.page?.total??a.total_messages} mensajes en el buzón`:'';
    this.$('previous').disabled=this.pageLoading||this.offset===0;
    this.$('next').disabled=this.pageLoading||!this.page||this.offset+20>=this.page.total;
    this.$('page-label').textContent=this.pageLoading?'':`Página ${Math.floor(this.offset/20)+1} de ${Math.max(1,Math.ceil((this.page?.total||0)/20))}`;
    this.$('filter').setAttribute('aria-pressed',String(!!this.onlyUnread));
    this.$('filter').textContent=this.onlyUnread?'Mostrar todos':'Solo pendientes';
    this.$('messages').replaceChildren();
    const rows=this.view==='messages'?(this.page?.messages||[]):a.messages.filter(m=>!m.read);
    this.renderMessages(rows,a,this.$('messages'));
  }
  eventDate(start){
    // Date-only events already express the school calendar day.
    if(/^\d{4}-\d{2}-\d{2}$/.test(start))return start;
    const date=new Date(start);if(Number.isNaN(date.getTime()))return '';
    return new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Madrid',year:'numeric',month:'2-digit',day:'2-digit'}).format(date);
  }
  updateMealControls(){[...this.$('meal-controls').children].forEach((button,index)=>button.setAttribute('aria-pressed',String(index===this.mealIndex)));}
  positionMeal(smooth=false){
    const row=this.$('meal-row');if(row.hidden||!row.clientWidth)return;
    row.scrollTo({left:matchMedia('(max-width:600px)').matches?this.mealIndex*(row.clientWidth+12):0,behavior:smooth&&!matchMedia('(prefers-reduced-motion:reduce)').matches?'smooth':'instant'});this.updateMealControls();
  }
  renderMeals(account){
    const signature=JSON.stringify([account.entry_id,account.date,account.menus,account.menu]);
    if(this.mealSignature===signature)return;
    if(this.mealDate!==account.date||this.mealAccount!==account.entry_id)this.mealIndex=1;
    this.mealDate=account.date;this.mealAccount=account.entry_id;this.mealSignature=signature;
    const titles=['Qué comimos ayer','Qué comemos hoy','Qué comeremos mañana'];
    this.$('meal-row').replaceChildren(...[-1,0,1].map((offset,index)=>{
      const date=new Date(account.date+'T12:00:00Z');date.setUTCDate(date.getUTCDate()+offset);const key=date.toISOString().slice(0,10);
      const menu=account.menus?.find(m=>m.date===key)?.menu||(offset===0?account.menu:'');
      const article=document.createElement('article');article.className='menu'+(offset===0?' today':'');
      const label=document.createElement('div');label.className='date';label.textContent=date.toLocaleDateString('es-ES',{weekday:'long',day:'numeric',month:'long',timeZone:'UTC'});
      const title=document.createElement('h2');title.textContent=titles[index];const content=document.createElement('p');content.textContent=menu||'No hay menú publicado para este día.';
      article.append(label,title,content);return article;
    }));
    this.positionMeal();
  }
  currentAccount(){return this.accounts.find(a=>a.entry_id===this.$('account').value)||this.accounts[0];}
  recipientLabel(m){return (m.children||[]).map(c=>c.name).join(', ')||'Destinatario no indicado por Casvi';}
  childGivenName(child){return child.given_name?.trim()||child.name?.trim().split(/\s+/)[0]||'Alumno';}
  renderTabs(a){
    const tabs=[['home','Inicio','home'],['messages','Mensajes','mail'],['dining','Comedor','dining'],...(a.children||[]).map(c=>['child:'+c.id,this.childGivenName(c),'student'])];
    const selected=tabs.find(([value])=>value===this.view)||tabs[0];
    this.$('mobile-current').replaceChildren(this.tabIcon(selected[2]),document.createTextNode(selected[1]));
    this.$('mobile-options').replaceChildren(...tabs.map(([value,label,icon])=>{const option=document.createElement('button');option.setAttribute('aria-label',label);option.append(this.tabIcon(icon),document.createTextNode(label));if(this.view===value)option.setAttribute('aria-current','page');option.onclick=()=>{this.$('mobile-section').open=false;this.navigate(value);this.$('mobile-section').querySelector('summary').focus();};return option;}));
    this.$('tabs').replaceChildren(...tabs.map(([value,label,icon])=>{
      const b=document.createElement('button');b.append(this.tabIcon(icon),document.createTextNode(label));b.setAttribute('role','tab');b.setAttribute('aria-selected',String(this.view===value));
      b.onclick=()=>this.navigate(value);return b;
    }));
  }
  navigate(value){
    this.menuRequest=(this.menuRequest||0)+1;
    this.pageRequest=(this.pageRequest||0)+1;this.childRequest=(this.childRequest||0)+1;
    this.homeRequest=(this.homeRequest||0)+1;this.homeProfiles=null;this.view=value;this.onlyUnread=false;this.page=null;this.profile=null;this.offset=0;
    this.pageLoading=false;this.childLoading=false;this.$('error').hidden=true;this.render();
    this.load(true);
    if(value==='dining')this.loadMenuMonth();
    else if(value==='messages')this.loadPage(0);
    else if(value.startsWith('child:'))this.loadChild();
  }
  async loadMenuMonth(){
    const account=this.currentAccount();if(!account)return;
    const [year,month]=account.date.slice(0,7).split('-').map(Number);const request=this.menuRequest=(this.menuRequest||0)+1;
    this.$('month-title').textContent=new Intl.DateTimeFormat('es',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(Date.UTC(year,month-1,1)));
    this.$('month-grid').replaceChildren();this.$('month-status').replaceChildren(this.loader('Cargando menú del mes'));
    try{
      const result=await this._hass.callWS({type:'casvi/menu',entry_id:account.entry_id,year,month});
      if(request!==this.menuRequest||this.view!=='dining')return;
      this.$('month-status').replaceChildren();
      const grid=this.$('month-grid');
      for(const name of ['Lunes','Martes','Miércoles','Jueves','Viernes']){const cell=document.createElement('div');cell.className='month-weekday';cell.textContent=name;grid.append(cell);}
      const offset=(new Date(Date.UTC(year,month-1,1)).getUTCDay()+6)%7;
      const days=new Date(Date.UTC(year,month,0)).getUTCDate();
      for(let slot=0;slot<Math.ceil((offset+days)/7)*7;slot++){
        if(slot%7>=5)continue;
        const day=slot-offset+1;const cell=document.createElement('div');cell.className='month-day';
        if(day<1||day>days){cell.classList.add('empty-day');cell.setAttribute('aria-hidden','true');grid.append(cell);continue;}
        const key=`${year}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
        if(key===account.date)cell.classList.add('today');
        const date=document.createElement('time');date.dateTime=key;date.textContent=String(day);
        const menu=document.createElement('p');menu.textContent=result.menus.filter(m=>m.date===key).map(m=>m.menu).filter(Boolean).join('\n')||'Sin menú publicado';
        cell.append(date,menu);grid.append(cell);
      }
    }catch(_){if(request===this.menuRequest){this.$('month-status').textContent='No se pudo cargar el menú. ';const retry=document.createElement('button');retry.textContent='Reintentar';retry.onclick=()=>this.loadMenuMonth();this.$('month-status').append(retry);}}
  }
  tabIcon(name){
    const paths={attachment:'M21 11l-9 9a6 6 0 0 1-8-8l10-10a4 4 0 0 1 6 6L10 18a2 2 0 0 1-3-3l9-9',dining:'M4 3v6q0 3 3 3V3 M4 7h6V3 M7 12v9 M19 3q-5 5-3 10h3 M19 3v18',pool:'M2 17q2-2 4 0t4 0t4 0t4 0t4 0 M2 21q2-2 4 0t4 0t4 0t4 0t4 0 M5 13l5-5 5 4 4 1 M10 8 7 5 3 7 M17 6a2 2 0 1 0 4 0a2 2 0 1 0-4 0',physical:'M13 4a2 2 0 1 0 4 0a2 2 0 1 0-4 0 M8 10l4-3 4 4 4 1 M12 7l-2 7 5 3-1 5 M10 14l-3 5H3',home:'M3 10 12 3 21 10 M5 9v12h5v-7h4v7h5V9',mail:'M3 5h18v14H3z M3 5l9 7 9-7',student:'M2 8l10-5 10 5-10 5z M6 10v6c3 3 9 3 12 0v-6 M22 8v7'};
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    for(const [key,value] of Object.entries({viewBox:'0 0 24 24',width:'20',height:'20',fill:'none',stroke:'currentColor','stroke-width':'1.7','stroke-linecap':'round','stroke-linejoin':'round','aria-hidden':'true'}))svg.setAttribute(key,value);
    const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',paths[name]);svg.append(path);return svg;
  }
  renderMessages(rows,a,container){
    container.replaceChildren();
    rows.forEach(m=>{
      const b=document.createElement('button');b.className='row';
      if(!m.read){const badge=document.createElement('span');badge.className='badge';badge.textContent='Pendiente';b.append(badge);}
      const title=document.createElement('span');title.className='subject';title.textContent=m.subject||'Sin asunto';
      if(m.attachment_count>0){const indicator=document.createElement('span');indicator.style.cssText='display:inline-flex;vertical-align:middle;margin-left:8px';const label=m.attachment_count===1?'1 archivo adjunto':`${m.attachment_count} archivos adjuntos`;indicator.title=label;indicator.setAttribute('role','img');indicator.setAttribute('aria-label',label);indicator.append(this.tabIcon('attachment'));title.append(indicator);}
      const meta=document.createElement('span');meta.className='meta';meta.textContent=`${m.sender} · ${m.date.slice(0,16)}`;
      const recipient=document.createElement('span');recipient.className='recipient';recipient.textContent=this.recipientLabel(m);
      const excerpt=document.createElement('span');excerpt.className='excerpt';excerpt.textContent=m.excerpt||'Abrir para ver el contenido';
      b.append(title,excerpt,meta,recipient);b.onclick=()=>this.openMessage(a.entry_id,m.id,m.id_para);container.append(b);
    });
    if(!rows.length){const empty=document.createElement('p');empty.className='empty';if(this.pageLoading)empty.append(this.loader('Cargando mensajes'));else empty.textContent=this.view==='home'?'No hay mensajes no leídos entre los consultados.':'No hay mensajes en esta vista.';container.append(empty);}
  }
  async loadPage(offset){
    const a=this.currentAccount();if(!a)return;
    const request=this.pageRequest=(this.pageRequest||0)+1;
    this.pageLoading=true;this.offset=offset;this.page=null;this.render();
    try{
      const page=await this._hass.callWS({type:'casvi/messages',entry_id:a.entry_id,start:offset,length:20});
      if(request!==this.pageRequest||this.currentAccount()?.entry_id!==a.entry_id)return;
      this.page=page;this.$('error').hidden=true;
    }catch(_){if(request!==this.pageRequest)return;this.$('error').textContent='No se pudo cargar esta página. Vuelve a pulsar la pestaña para reintentar.';this.$('error').hidden=false;}
    finally{if(request===this.pageRequest){this.pageLoading=false;this.render();}}
  }
  async loadChild(){
    const a=this.currentAccount();const id=this.view.slice(6);if(!a||!a.children.some(c=>c.id===id))return;
    const request=this.childRequest=(this.childRequest||0)+1;this.childLoading=true;this.profile=null;this.render();
    try{
      const profile=await this._hass.callWS({type:'casvi/child',entry_id:a.entry_id,child_id:id});
      if(request!==this.childRequest||this.currentAccount()?.entry_id!==a.entry_id||this.view!=='child:'+id)return;
      this.profile=profile;this.$('error').hidden=true;this.loadSchedule(a.entry_id,id,profile,request);this.loadTeacherPhotos(a.entry_id,id,profile,request);
    }catch(_){if(request!==this.childRequest)return;this.$('error').textContent='No se pudo cargar la ficha. Vuelve a pulsar la pestaña para reintentar.';this.$('error').hidden=false;}
    finally{if(request===this.childRequest){this.childLoading=false;this.render();}}
  }
  renderChild(a){
    const id=this.view.slice(6);const child=(a.children||[]).find(c=>c.id===id);const p=this.profile;
    this.$('child-name').textContent=child?.name||'Alumno';this.$('child-status').replaceChildren();if(this.childLoading)this.$('child-status').append(this.loader('Cargando la ficha'));else this.$('child-status').textContent=p?'':'La ficha todavía no está disponible.';
    this.$('child-group').textContent=p?.group||'';this.$('child-tutor').textContent=p?.tutor?'Tutor: '+p.tutor:'';this.$('schedule-section').hidden=!p;this.renderSchedule(p);this.$('child-data').hidden=!p;this.$('teacher-section').hidden=!p;if(!p)return;this.renderTeachers(p);
    this.$('classmates').replaceChildren(...p.classmates.map(name=>{const li=document.createElement('li');li.textContent=name;return li;}));
    if(!p.classmates.length)this.$('classmates').textContent='No hay compañeros disponibles.';
  }
  async loadSchedule(entry,child,profile,request,guard=null,update=null){
    const current=guard||(()=>request===this.childRequest&&this.profile===profile&&this.view==='child:'+child&&this.currentAccount()?.entry_id===entry);
    const render=update||(()=>this.renderSchedule(profile));
    if(profile.schedule){
      this.scheduleParser=await import('/casvi-static/schedule.mjs');
      if(current())render();return;
    }
    const doc=this.latestSchedule(profile.documents)[0];
    if(!doc){profile.scheduleError='No hay un horario PDF publicado.';if(current())render();return;}
    profile.scheduleLoading=true;if(current())render();let task;
    try{
      const result=await this._hass.callWS({type:'casvi/document',entry_id:entry,child_id:child,document_id:doc.id,kind:doc.kind});
      if(!current())return;
      const [pdfjs,parser]=await Promise.all([import('/casvi-static/pdfjs/pdf.mjs'),import('/casvi-static/schedule.mjs')]);
      pdfjs.GlobalWorkerOptions.workerSrc='/casvi-static/pdfjs/pdf.worker.mjs';
      task=pdfjs.getDocument({data:Uint8Array.from(atob(result.pdf),c=>c.charCodeAt(0)),isEvalSupported:false,cMapUrl:'/casvi-static/pdfjs/cmaps/',cMapPacked:true,standardFontDataUrl:'/casvi-static/pdfjs/standard_fonts/',wasmUrl:'/casvi-static/pdfjs/wasm/'});
      const pdf=await task.promise;let schedule;
      for(let pageNumber=1;pageNumber<=Math.min(pdf.numPages,3);pageNumber++){
        if(!current())return;
        const page=await pdf.getPage(pageNumber);const content=await page.getTextContent();
        try{schedule=parser.parseSchedule(content.items);}catch(_){}page.cleanup();if(schedule)break;
      }
      if(!schedule)throw Error('Unsupported schedule');
      if(current()){profile.schedule=schedule;this.scheduleParser=parser;}
    }catch(_){if(current())profile.scheduleError='No se ha podido interpretar este horario con seguridad. Consulta el PDF original.';}
    finally{if(task)await task.destroy().catch(()=>{});if(current()){profile.scheduleLoading=false;render();}}
  }
  async loadHomeSchedules(){
    const account=this.currentAccount();if(!account)return;
    const request=this.homeRequest=(this.homeRequest||0)+1;
    this.homeProfiles={};
    const current=()=>request===this.homeRequest&&this.view==='home'&&this.currentAccount()?.entry_id===account.entry_id&&this.isConnected;
    this.renderHomeSchedules(account);
    for(const child of account.children||[]){
      if(!current())return;
      try{
        const profile=await this._hass.callWS({type:'casvi/child',entry_id:account.entry_id,child_id:child.id});
        if(!current())return;
        this.homeProfiles[child.id]=profile;
        await this.loadSchedule(account.entry_id,child.id,profile,request,current,()=>this.renderHomeSchedules(this.currentAccount()));
      }catch(_){if(current()){this.homeProfiles[child.id]={scheduleError:'No se pudo cargar el horario.'};this.renderHomeSchedules(this.currentAccount());}}
    }
  }
  renderHomeSchedules(account){
    const weekday=(new Date(account.date+'T12:00:00Z').getUTCDay()+6)%7;
    this.$('home-schedule-cards').replaceChildren(...(account.children||[]).map(child=>{
      const card=document.createElement('article');card.className='schedule-section';
      const heading=document.createElement('h3');heading.textContent=this.childGivenName(child);card.append(heading);
      const profile=this.homeProfiles?.[child.id];
      if(!profile?.schedule){const status=document.createElement('p');status.className='hint';status.setAttribute('role','status');if(profile?.scheduleError)status.textContent=profile.scheduleError;else status.append(this.loader('Cargando horario'));card.append(status);return card;}
      const day=this.scheduleParser.daySchedule(profile.schedule,weekday);
      const flags=document.createElement('div');flags.className='schedule-status';
      const labels=[['Piscina',day.swimming,day.combined,'pool']];
      if(/infantil/i.test(profile.group||''))labels.push(['Psicomotricidad',day.psychomotor,false,'physical']);
      else if(/primaria|secundaria|\beso\b|bachiller/i.test(profile.group||''))labels.push(['Educación física',day.physical,day.combined,'physical']);
      for(const [label,yes,uncertain,icon] of labels){const badge=document.createElement('span');if(icon)badge.append(this.tabIcon(icon));badge.append(document.createTextNode(label+': '+(yes?'Sí':uncertain?'EF/NAT · por confirmar':'No')));if(yes||uncertain)badge.className='active';flags.append(badge);}card.append(flags);
      if(day.rows.length){const wrapper=document.createElement('div');wrapper.className='schedule-table';wrapper.append(this.scheduleTable(['Hora','Clase'],day.rows.map(r=>[r.start+'–'+r.end,r.subject])));card.append(wrapper);}
      else{const empty=document.createElement('p');empty.textContent='Hoy no hay clases en el horario semanal.';card.append(empty);}
      return card;
    }));
  }
  renderSchedule(profile){
    if(!profile)return;
    this.$('schedule-week-table').replaceChildren();
    if(!profile.schedule){this.$('schedule-note').replaceChildren();if(profile.scheduleError)this.$('schedule-note').textContent=profile.scheduleError;else this.$('schedule-note').append(this.loader('Leyendo el horario PDF'));return;}
    this.$('schedule-note').textContent='';
    this.$('schedule-week-table').append(this.scheduleTable(['Hora','Lunes','Martes','Miércoles','Jueves','Viernes'],profile.schedule.rows.map(r=>[r.start+'–'+r.end,...r.subjects])));
  }
  scheduleTable(headers,rows){
    const table=document.createElement('table');const head=document.createElement('thead');const hr=document.createElement('tr');
    for(const title of headers){const th=document.createElement('th');th.scope='col';th.textContent=title;hr.append(th);}head.append(hr);table.append(head);
    const body=document.createElement('tbody');for(const row of rows){const tr=document.createElement('tr');row.forEach((value,index)=>{const cell=document.createElement(index?'td':'th');if(!index)cell.scope='row';cell.textContent=value;tr.append(cell);});body.append(tr);}table.append(body);return table;
  }
  latestSchedule(documents){
    const schedules=documents.filter(d=>/\bhorario\b/i.test(d.title||''));
    // Group documents describe the current class. Casvi lists them newest first.
    const group=schedules.filter(d=>d.kind==='documentoGrupo');
    return (group.length?group:schedules).slice(0,1);
  }
  teacherDisplayName(name){
    // Casvi's group roster uses "surname1 surname2 given names".
    // Keep all given names together, including compound names.
    const text=(name||'').trim().replace(/\s+/g,' ');
    if(text==='Profesor sin nombre')return text;
    if(text.includes(',')){const [surnames,...given]=text.split(',');return `${given.join(' ').trim()} ${surnames.trim()}`.trim();}
    const parts=text.split(' ');
    return parts.length>=3?[...parts.slice(2),...parts.slice(0,2)].join(' '):text;
  }
  renderTeachers(profile){
    const container=this.$('teachers');container.replaceChildren();
    for(const teacher of profile.teachers||[])for(const subject of teacher.subjects?.length?teacher.subjects:['Asignatura no indicada']){
      const card=document.createElement('article');card.className='teacher';
      const portrait=document.createElement('div');portrait.className='portrait';
      if(teacher.photo){const img=document.createElement('img');img.src=teacher.photo;img.alt='Foto de '+this.teacherDisplayName(teacher.name);img.loading='lazy';img.onerror=()=>{portrait.textContent='Sin foto';};portrait.append(img);}
      else if(teacher.photoState==='missing')portrait.textContent='Sin foto';else portrait.append(this.loader('Cargando foto'));
      const details=document.createElement('div');details.className='teacher-details';const name=document.createElement('h3');name.textContent=this.teacherDisplayName(teacher.name);const assignment=document.createElement('p');assignment.textContent=subject;details.append(name,assignment);card.append(portrait,details);container.append(card);
    }
    if(!(profile.teachers||[]).length)container.textContent=profile.teachers_available===false?'No se pudieron cargar los profesores. Vuelve a pulsar la pestaña para reintentar.':'Casvi no ha publicado profesores para este grupo.';
  }
  async loadTeacherPhotos(entry,child,profile,request){
    const queue=[...(profile.teachers||[])];
    const current=()=>request===this.childRequest&&this.profile===profile&&this.view==='child:'+child&&this.currentAccount()?.entry_id===entry&&this.isConnected;
    const worker=async()=>{
      while(queue.length&&current()){
        const teacher=queue.shift();
        try{const result=await this._hass.callWS({type:'casvi/teacher_photo',entry_id:entry,child_id:child,teacher_id:teacher.id});if(!current())return;teacher.photo=result.photo;}
        catch(_){teacher.photoState='missing';}
        if(current())this.renderTeachers(profile);
      }
    };
    await Promise.all([worker(),worker(),worker()]);
  }
  clearPDF(){for(const task of this.attachmentTasks||[])task.destroy().catch(()=>{});this.attachmentTasks=[];for(const url of this.attachmentURLs||[])URL.revokeObjectURL(url);this.attachmentURLs=[];if(this.pdfTask){this.pdfTask.destroy().catch(()=>{});this.pdfTask=null;}if(this.pdfURL){URL.revokeObjectURL(this.pdfURL);this.pdfURL=null;}this.shadowRoot.querySelectorAll('.pdf,.pdf-link').forEach(e=>e.remove());}
  async openDocument(entry,child,documentInfo){
    const request=this.requestId=(this.requestId||0)+1;this.clearPDF();this.$('subject').textContent=documentInfo.title;this.$('sender').textContent='';this.$('body').replaceChildren(this.loader('Cargando PDF'));this.$('attachments').replaceChildren();
    const dialog=this.shadowRoot.querySelector('dialog');if(!dialog.open)dialog.showModal();
    try{
      const result=await this._hass.callWS({type:'casvi/document',entry_id:entry,child_id:child,document_id:documentInfo.id,kind:documentInfo.kind});
      if(request!==this.requestId)return;
      const bytes=Uint8Array.from(atob(result.pdf),c=>c.charCodeAt(0));this.pdfURL=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));
      this.$('body').textContent='';const link=document.createElement('a');link.className='pdf-link';link.href=this.pdfURL;link.target='_blank';link.rel='noopener';link.textContent='Abrir PDF en otra pestaña';
      this.$('body').append(link);
      const pdfjs=await import('/casvi-static/pdfjs/pdf.mjs');
      if(request!==this.requestId)return;
      pdfjs.GlobalWorkerOptions.workerSrc='/casvi-static/pdfjs/pdf.worker.mjs';
      this.pdfTask=pdfjs.getDocument({data:bytes,isEvalSupported:false,
        cMapUrl:'/casvi-static/pdfjs/cmaps/',cMapPacked:true,
        standardFontDataUrl:'/casvi-static/pdfjs/standard_fonts/',wasmUrl:'/casvi-static/pdfjs/wasm/'});
      const pdf=await this.pdfTask.promise;
      for(let number=1;number<=Math.min(pdf.numPages,10);number++){
        if(request!==this.requestId)return;
        const page=await pdf.getPage(number);const natural=page.getViewport({scale:1});
        const scale=Math.min(2,1100/natural.width,Math.sqrt(1500000/(natural.width*natural.height)));
        const viewport=page.getViewport({scale});const canvas=document.createElement('canvas');canvas.className='pdf';canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);canvas.setAttribute('role','img');canvas.setAttribute('aria-label',result.title+', página '+number);
        await page.render({canvasContext:canvas.getContext('2d'),viewport}).promise;
        if(request!==this.requestId)return;this.$('body').append(canvas);page.cleanup();
      }
      if(pdf.numPages>10){const note=document.createElement('p');note.textContent='Vista previa de las primeras 10 páginas. Abre el PDF para ver el documento completo.';this.$('body').append(note);}

    }catch(_){if(request===this.requestId)this.$('body').textContent='No se pudo mostrar el documento. Puede no ser un PDF o superar 5 MB. Consulta los documentos en la intranet.';}
  }
  messageDate(value){
    if(!value)return '';
    const match=value.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/);
    return match?`${match[3]}/${match[2]}/${match[1]} ${match[4]}:${match[5]}`:value;
  }
  messageParagraphs(content){
    return (content||'').replace(/\r\n?/g,'\n').split(/\n[\t \u00a0]*\n+/).map(part=>part.replace(/\s+/g,' ').trim()).filter(Boolean);
  }
  appendMessageLinks(container,text){
    const pattern=/\b(?:https?:\/\/|www\.)[^\s<>]+/gi;let offset=0;
    for(const match of text.matchAll(pattern)){
      let label=match[0].replace(/[.,;:!?]+$/,'');
      while(label.endsWith(')')&&(label.match(/\)/g)||[]).length>(label.match(/\(/g)||[]).length)label=label.slice(0,-1);
      let url;try{url=new URL(label.startsWith('www.')?'https://'+label:label);}catch(_){continue;}
      if(!['http:','https:'].includes(url.protocol)||url.username||url.password)continue;
      container.append(document.createTextNode(text.slice(offset,match.index)));
      const link=document.createElement('a');link.href=url.href;link.textContent=label;link.target='_blank';link.rel='noopener noreferrer';container.append(link);
      offset=match.index+label.length;
    }
    container.append(document.createTextNode(text.slice(offset)));
  }
  appendMessageNodes(parent,nodes,inLink=false,depth=0){
    if(depth>50)return;
    const allowed=new Set(['p','div','br','strong','b','em','i','u','s','ul','ol','li','blockquote','h1','h2','h3','h4','a']);
    for(const node of nodes){
      if(typeof node.text==='string'){if(inLink)parent.append(document.createTextNode(node.text));else this.appendMessageLinks(parent,node.text);continue;}
      if(!allowed.has(node.tag))continue;
      const element=document.createElement(node.tag);
      if(node.tag==='a'&&node.href){try{const url=new URL(node.href);if(['https:','http:'].includes(url.protocol)&&!url.username&&!url.password){element.href=url.href;element.target='_blank';element.rel='noopener noreferrer';}}catch(_){} }
      this.appendMessageNodes(element,node.children||[],inLink||node.tag==='a',depth+1);parent.append(element);
    }
  }
  renderMessageBody(content,nodes){
    const body=this.$('body');body.classList.add('message-body');
    if(Array.isArray(nodes)&&nodes.length){body.replaceChildren();this.appendMessageNodes(body,nodes);return;}
    const paragraphs=this.messageParagraphs(content);
    body.replaceChildren(...(paragraphs.length?paragraphs:['Este mensaje no contiene texto.']).map(text=>{const p=document.createElement('p');this.appendMessageLinks(p,text);return p;}));
  }
  async renderAttachments(attachments,entry,id,recipient,request){
    if(!attachments.length)return;
    const container=this.$('attachments');const heading=document.createElement('h3');heading.textContent='Adjuntos';container.append(heading);
    for(const [index,attachment] of attachments.entries()){
      if(request!==this.requestId)return;
      const section=document.createElement('section');section.style.margin='20px 0';
      const title=document.createElement('p');title.textContent=attachment.name;section.append(title);
      const preview=document.createElement('div');preview.append(this.loader('Cargando adjunto'));section.append(preview);
      const link=document.createElement('a');link.textContent='Descargar '+attachment.name;link.target='_blank';link.rel='noopener noreferrer';
      if(attachment.url){link.href=attachment.url;section.append(link);}container.append(section);
      try{
        const result=await this._hass.callWS({type:'casvi/attachment',entry_id:entry,message_id:id,recipient_id:recipient,index});
        if(request!==this.requestId)return;
        if(!['application/pdf','image/png','image/jpeg','image/gif','image/webp'].includes(result.mime))throw new Error('Unsupported attachment');
        const bytes=Uint8Array.from(atob(result.data),c=>c.charCodeAt(0));
        const url=URL.createObjectURL(new Blob([bytes],{type:result.mime}));(this.attachmentURLs??=[]).push(url);
        link.href=url;link.download=attachment.name;if(!link.isConnected)section.append(link);
        if(result.mime.startsWith('image/')){
          const image=document.createElement('img');image.alt=attachment.name;image.style.cssText='display:block;max-width:100%;height:auto;margin:12px auto';
          image.src=url;preview.replaceChildren(image);
        }else{
          const pdfjs=await import('/casvi-static/pdfjs/pdf.mjs');if(request!==this.requestId)return;
          pdfjs.GlobalWorkerOptions.workerSrc='/casvi-static/pdfjs/pdf.worker.mjs';
          const task=pdfjs.getDocument({data:bytes,isEvalSupported:false,cMapUrl:'/casvi-static/pdfjs/cmaps/',cMapPacked:true,standardFontDataUrl:'/casvi-static/pdfjs/standard_fonts/',wasmUrl:'/casvi-static/pdfjs/wasm/'});
          (this.attachmentTasks??=[]).push(task);const pdf=await task.promise;if(request!==this.requestId)return;preview.replaceChildren();
          for(let number=1;number<=Math.min(pdf.numPages,10);number++){
            if(request!==this.requestId)return;
            const page=await pdf.getPage(number);const natural=page.getViewport({scale:1});
            const viewport=page.getViewport({scale:Math.min(2,1100/natural.width,Math.sqrt(1500000/(natural.width*natural.height)))});
            const canvas=document.createElement('canvas');canvas.className='pdf';canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);canvas.setAttribute('role','img');canvas.setAttribute('aria-label',attachment.name+', página '+number);
            await page.render({canvasContext:canvas.getContext('2d'),viewport}).promise;
            if(request!==this.requestId)return;preview.append(canvas);page.cleanup();
          }
          if(pdf.numPages>10){const note=document.createElement('p');note.textContent='Se muestran las primeras 10 páginas. Descarga el PDF para verlo completo.';preview.append(note);}
        }
      }catch(_){if(request!==this.requestId)return;preview.textContent='No se pudo mostrar la vista previa. Disponible para imágenes y PDF de hasta 5 MB.';}
    }
  }
  async openMessage(entry,id,recipient) {
    const request=this.requestId=(this.requestId||0)+1;
    this.clearPDF();
    this.$('subject').textContent='Mensaje';this.$('sender').textContent='';this.$('body').replaceChildren(this.loader('Cargando mensaje'));this.$('attachments').replaceChildren();
    const dialog=this.shadowRoot.querySelector('dialog');if(!dialog.open) dialog.showModal();
    try {
      const m=await this._hass.callWS({type:'casvi/message',entry_id:entry,message_id:id,recipient_id:recipient});
      if(request!==this.requestId) return;
      for(const account of this.accounts)if(account.entry_id===entry)for(const row of account.messages)if(row.id===id&&row.id_para===recipient){row.excerpt=m.excerpt;if(m.read)row.read=true;}
      if(this.currentAccount()?.entry_id===entry)for(const row of this.page?.messages||[])if(row.id===id&&row.id_para===recipient){row.excerpt=m.excerpt;if(m.read)row.read=true;}
      this.render();
      this.$('subject').textContent=m.subject;const sourceDate=m.date||this.accounts.find(a=>a.entry_id===entry)?.messages.find(row=>row.id===id&&row.id_para===recipient)?.date||this.page?.messages.find(row=>row.id===id&&row.id_para===recipient)?.date;
      const dateLabel=this.messageDate(sourceDate);
      this.$('sender').textContent=[m.sender,this.recipientLabel(m),dateLabel].filter(Boolean).join(' · ');this.renderMessageBody(m.content,m.content_nodes);
      if(m.read===false){const warning=document.createElement('p');warning.className='error';warning.textContent='El mensaje se ha abierto, pero Casvi no ha confirmado que quede leído. Vuelve a abrirlo para reintentar.';this.$('body').append(warning);}
      this.renderAttachments(m.attachments||[],entry,id,recipient,request);
    } catch (_) {if(request===this.requestId)this.$('body').textContent='No se pudo abrir el mensaje. Puede haber salido de la lista reciente. Inténtalo de nuevo o entra en la intranet.';}
  }
}
if(!customElements.get('casvi-school-panel')) customElements.define('casvi-school-panel',CasviSchoolPanel);
