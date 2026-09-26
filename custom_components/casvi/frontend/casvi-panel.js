/* Bundled school panel. Private text is inserted with textContent, never HTML. */
class CasviSchoolPanel extends HTMLElement {
  constructor() {
    super(); this.attachShadow({mode: 'open'}); this.accounts = []; this.loading = false;
    this.shadowRoot.innerHTML = `
      <style>
        :host {display:block;height:100%;overflow:auto;background:var(--primary-background-color,#f6f8fb);color:var(--primary-text-color,#203344);font:16px/1.5 var(--paper-font-body1_-_font-family,system-ui,sans-serif)}
        *{box-sizing:border-box} main{max-width:1160px;margin:auto;padding:28px 30px 64px} header{display:flex;align-items:center;gap:16px;margin-bottom:28px} h1{font-size:34px;font-weight:650;letter-spacing:-1px;margin:0} .subtitle{color:var(--secondary-text-color,#526575);margin:2px 0 0} .spacer{flex:1} button,select,a{font:inherit} button,select{border:1px solid var(--divider-color,#bcc9d1);border-radius:8px;padding:10px 14px;background:var(--card-background-color,white);color:inherit} button{cursor:pointer} button:hover{border-color:#12677b} button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #d79a25;outline-offset:3px} button:disabled{opacity:.6;cursor:wait} a{color:var(--primary-color,#12677b)} .grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:28px;align-items:start} h2{font-size:21px;font-weight:650;margin:0 0 16px} .menu{background:var(--card-background-color,white);border-top:6px solid #12677b;border-radius:4px;padding:24px;margin-bottom:30px}.date{color:var(--secondary-text-color,#526575);font-size:14px}.menu p{white-space:pre-wrap;line-height:1.85;margin-bottom:0} .row{display:block;width:100%;text-align:left;border:0;border-bottom:1px solid var(--divider-color,#dce3e8);border-radius:0;padding:18px 8px;background:transparent}.row:hover{background:var(--secondary-background-color,#edf3f7)}.subject{display:block;font-weight:600;line-height:1.4}.meta{display:block;font-size:14px;color:var(--secondary-text-color,#526575);margin-top:6px}.badge{display:inline-block;font-size:12px;color:#09586c;background:#e2f3f6;border-radius:4px;padding:2px 7px;margin-bottom:7px}.toolbar{display:flex;gap:12px;align-items:center;margin-bottom:12px}.toolbar h2{margin:0;flex:1}.hint{font-size:14px;color:var(--secondary-text-color,#526575)}.error{border-left:4px solid #b74532;padding:12px;background:var(--card-background-color,white);margin-bottom:18px}.events{padding:0;list-style:none}.events li{padding:12px 0;border-bottom:1px solid var(--divider-color,#dce3e8)}.events strong{display:block} .empty{padding:20px 0;color:var(--secondary-text-color,#526575)}dialog{background:var(--card-background-color,white);color:inherit;border:0;border-radius:12px;max-width:720px;width:calc(100% - 32px);max-height:85vh;padding:26px;box-shadow:0 10px 60px #0004}dialog::backdrop{background:#10253588}.body{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.8}.dialog-head{display:flex;gap:15px;align-items:start}.dialog-head h2{flex:1}.links{margin-top:24px} [hidden]{display:none!important}.menu-toggle{border:0;font-size:22px;padding:7px} @media(max-width:720px){main{padding:18px 18px 48px}.grid{grid-template-columns:1fr;gap:8px}h1{font-size:29px}header{gap:10px;flex-wrap:wrap}.toolbar{flex-wrap:wrap}.menu{margin-bottom:22px}.row{padding:16px 0}dialog{padding:20px}}
      </style>
      <main>
        <header><button class="menu-toggle" aria-label="Abrir menú lateral">☰</button><div><h1>Colegio</h1><p class="subtitle">La agenda de casa, al día.</p></div><span class="spacer"></span><select id="account" aria-label="Cuenta familiar" hidden></select><button id="reload">Actualizar panel</button></header>
        <div id="error" role="status" class="error" hidden></div><p id="loading" role="status">Cargando el colegio…</p>
        <div id="content" class="grid" hidden>
          <section><div class="menu"><div id="date" class="date"></div><h2>Hoy en el comedor</h2><p id="menu"></p></div><h2>Próximos en la agenda</h2><ul id="events" class="events"></ul></section>
          <section><div class="toolbar"><h2>Mensajes</h2><button id="filter" aria-pressed="false">Solo pendientes</button></div><p id="count" class="hint"></p><div id="messages"></div><p class="hint">Abrir un mensaje consulta su contenido en Casvi y podría cambiar su estado de lectura. Consultar este panel no abre los pendientes.</p><p id="notification-state" class="hint"></p><a href="/config/integrations/integration/casvi">Configurar avisos</a></section>
        </div>
        <dialog><div class="dialog-head"><h2 id="subject"></h2><button id="close" aria-label="Cerrar mensaje">Cerrar</button></div><p id="sender" class="hint"></p><div id="body" class="body" role="status"></div><div id="attachments"></div><p class="links"><a href="https://intranet.casvi.es/pages/mensajes.php" target="_blank" rel="noopener noreferrer">Abrir la intranet de Casvi</a></p><p class="hint">Para descargar adjuntos, entra en la intranet con tu cuenta.</p></dialog>
      </main>`;
    this.$('reload').onclick = () => this.load();
    this.$('account').onchange = () => this.render();
    this.$('filter').onclick = () => {this.onlyUnread = !this.onlyUnread; this.render();};
    this.$('close').onclick = () => {this.requestId = (this.requestId || 0) + 1; this.shadowRoot.querySelector('dialog').close();};
    this.shadowRoot.querySelector('.menu-toggle').onclick = () => this.dispatchEvent(new Event('hass-toggle-menu',{bubbles:true,composed:true}));
  }
  $(id) {return this.shadowRoot.getElementById(id);}
  set hass(value) {this._hass=value; if(this.isConnected && !this.started){this.started=true; this.load();} this.handleDeepLink();}
  set route(value) {this._route=value; this.handleDeepLink();}
  connectedCallback() {if(this._hass && !this.started){this.started=true;this.load();} this.timer=setInterval(()=>this.load(),30000);}
  disconnectedCallback() {clearInterval(this.timer);this.started=false;}
  async load() {
    if(!this._hass || this.loading) return;
    this.loading=true; this.$('reload').disabled=true;
    try {
      this.accounts=await this._hass.callWS({type:'casvi/overview'});
      const previous=this.$('account').value;
      this.$('account').replaceChildren(...this.accounts.map(a=>{const o=document.createElement('option');o.value=a.entry_id;o.textContent=a.name;return o;}));
      if(this.accounts.some(a=>a.entry_id===previous)) this.$('account').value=previous;
      this.$('account').hidden=this.accounts.length<2;
      this.$('error').hidden=true; this.render();
      this.handleDeepLink();
    } catch (_) {this.$('error').textContent='No se pudo cargar el panel. Comprueba la conexión y que tu usuario sea administrador.';this.$('error').hidden=false;}
    finally {this.loading=false;this.$('reload').disabled=false;this.$('loading').hidden=true;}
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
    this.$('content').hidden=!a;
    if(!a){this.$('error').textContent='Añade tu cuenta en Ajustes → Dispositivos y servicios → Casvi.';this.$('error').hidden=false;return;}
    if(!a.available){this.$('error').textContent='Casvi no está disponible. Se muestran los últimos datos recibidos.';this.$('error').hidden=false;}
    this.$('date').textContent=new Date(a.date+'T12:00:00').toLocaleDateString('es-ES',{weekday:'long',day:'numeric',month:'long'});
    this.$('menu').textContent=a.menu||'No hay menú publicado para hoy.';
    this.$('events').replaceChildren();
    [...a.events].sort((x,y)=>x.start.localeCompare(y.start)).slice(0,12).forEach(e=>{
      const li=document.createElement('li'); const title=document.createElement('strong');title.textContent=e.title;
      const meta=document.createElement('span');meta.className='meta';meta.textContent=`${e.child} · ${new Date(e.start).toLocaleString('es-ES',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZone:'Europe/Madrid'})}`;
      li.append(title,meta);this.$('events').append(li);
    });
    if(!a.events.length) this.$('events').textContent='No hay próximos eventos en la agenda recibida.';
    this.$('count').textContent=`${a.messages.filter(m=>!m.read).length} pendientes entre los ${a.messages.length} mensajes recientes.`;
    this.$('filter').setAttribute('aria-pressed',String(!!this.onlyUnread));
    this.$('filter').textContent=this.onlyUnread?'Mostrar todos':'Solo pendientes';
    this.$('messages').replaceChildren();
    const rows=a.messages.filter(m=>!this.onlyUnread||!m.read);
    rows.forEach(m=>{
      const b=document.createElement('button');b.className='row';
      if(!m.read){const badge=document.createElement('span');badge.className='badge';badge.textContent='Pendiente';b.append(badge);}
      const title=document.createElement('span');title.className='subject';title.textContent=m.subject||'Sin asunto';
      const meta=document.createElement('span');meta.className='meta';meta.textContent=`${m.sender} · ${m.date.slice(0,16)}`;
      b.append(title,meta);b.onclick=()=>this.openMessage(a.entry_id,m.id,m.id_para);this.$('messages').append(b);
    });
    if(!rows.length){const empty=document.createElement('p');empty.className='empty';empty.textContent=this.onlyUnread?'No hay mensajes pendientes en esta lista.':'No hay mensajes recientes.';this.$('messages').append(empty);}
    this.$('notification-state').textContent=a.notifications?'Avisos activados para los móviles seleccionados.':'Activa los avisos al móvil en las opciones de Casvi.';
  }
  async openMessage(entry,id,recipient) {
    const request=this.requestId=(this.requestId||0)+1;
    this.$('subject').textContent='Mensaje';this.$('sender').textContent='';this.$('body').textContent='Cargando mensaje…';this.$('attachments').replaceChildren();
    const dialog=this.shadowRoot.querySelector('dialog');if(!dialog.open) dialog.showModal();
    try {
      const m=await this._hass.callWS({type:'casvi/message',entry_id:entry,message_id:id,recipient_id:recipient});
      if(request!==this.requestId) return;
      this.$('subject').textContent=m.subject;this.$('sender').textContent=m.sender;this.$('body').textContent=m.content||'Este mensaje no contiene texto.';
      if(m.attachments.length){const h=document.createElement('h3');h.textContent='Adjuntos';const ul=document.createElement('ul');m.attachments.forEach(name=>{const li=document.createElement('li');li.textContent=name;ul.append(li);});this.$('attachments').append(h,ul);}
    } catch (_) {if(request===this.requestId)this.$('body').textContent='No se pudo abrir el mensaje. Puede haber salido de la lista reciente. Inténtalo de nuevo o entra en la intranet.';}
  }
}
if(!customElements.get('casvi-school-panel')) customElements.define('casvi-school-panel',CasviSchoolPanel);
