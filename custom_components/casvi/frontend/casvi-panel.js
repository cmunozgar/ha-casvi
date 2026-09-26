/* Bundled school panel. Private text is inserted with textContent, never HTML. */
class CasviSchoolPanel extends HTMLElement {
  constructor() {
    super(); this.attachShadow({mode: 'open'}); this.accounts = []; this.loading = false; this.view='home'; this.offset=0;
    this.shadowRoot.innerHTML = `
      <style>
        :host {display:block;height:100%;overflow:auto;background:var(--primary-background-color,#f6f8fb);color:var(--primary-text-color,#203344);font:16px/1.5 var(--paper-font-body1_-_font-family,system-ui,sans-serif)}
        *{box-sizing:border-box} main{max-width:1160px;margin:auto;padding:28px 30px 64px} header{display:flex;align-items:center;gap:16px;margin-bottom:28px} h1{font-size:34px;font-weight:650;letter-spacing:-1px;margin:0} .subtitle{color:var(--secondary-text-color,#526575);margin:2px 0 0} .spacer{flex:1} button,select,a{font:inherit} button,select{border:1px solid var(--divider-color,#bcc9d1);border-radius:8px;padding:10px 14px;background:var(--card-background-color,white);color:inherit} button{cursor:pointer} button:hover{border-color:#12677b} button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #d79a25;outline-offset:3px} button:disabled{opacity:.6;cursor:wait} a{color:var(--primary-color,#12677b)} .grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:28px;align-items:start} h2{font-size:21px;font-weight:650;margin:0 0 16px} .menu{background:var(--card-background-color,white);border-top:6px solid #12677b;border-radius:4px;padding:24px;margin-bottom:30px}.date{color:var(--secondary-text-color,#526575);font-size:14px}.menu p{white-space:pre-wrap;line-height:1.85;margin-bottom:0} .row{display:block;width:100%;text-align:left;border:0;border-bottom:1px solid var(--divider-color,#dce3e8);border-radius:0;padding:18px 8px;background:transparent}.row:hover{background:var(--secondary-background-color,#edf3f7)}.subject{display:block;font-weight:600;line-height:1.4}.meta{display:block;font-size:14px;color:var(--secondary-text-color,#526575);margin-top:6px}.badge{display:inline-block;font-size:12px;color:#09586c;background:#e2f3f6;border-radius:4px;padding:2px 7px;margin-bottom:7px}.toolbar{display:flex;gap:12px;align-items:center;margin-bottom:12px}.toolbar h2{margin:0;flex:1}.hint{font-size:14px;color:var(--secondary-text-color,#526575)}.error{border-left:4px solid #b74532;padding:12px;background:var(--card-background-color,white);margin-bottom:18px}.events{padding:0;list-style:none}.events li{padding:12px 0;border-bottom:1px solid var(--divider-color,#dce3e8)}.events strong{display:block} .empty{padding:20px 0;color:var(--secondary-text-color,#526575)}dialog{background:var(--card-background-color,white);color:inherit;border:0;border-radius:12px;max-width:720px;width:calc(100% - 32px);max-height:85vh;padding:26px;box-shadow:0 10px 60px #0004}dialog::backdrop{background:#10253588}.body{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.8}.dialog-head{display:flex;gap:15px;align-items:start}.dialog-head h2{flex:1}.links{margin-top:24px} [hidden]{display:none!important}.menu-toggle{border:0;font-size:22px;padding:7px} @media(max-width:720px){main{padding:18px 18px 48px}.grid{grid-template-columns:1fr;gap:8px}h1{font-size:29px}header{gap:10px;flex-wrap:wrap}.toolbar{flex-wrap:wrap}.menu{margin-bottom:22px}.row{padding:16px 0}dialog{padding:20px}}

        nav{display:flex;gap:8px;overflow:auto;margin:0 0 24px;padding-bottom:8px}nav button{white-space:nowrap;border-color:transparent;background:transparent}nav button[aria-selected="true"]{background:#12677b;color:white} .school-logo{width:54px;height:54px;border-radius:8px}.grid.inbox{display:block}.recipient{display:block;font-size:13px;color:var(--primary-color,#12677b);margin-top:6px}.pager{display:flex;gap:12px;align-items:center;justify-content:space-between;margin:20px 0}.child-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:28px}.child-heading{margin-bottom:24px}.people{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0}.people li{background:var(--card-background-color,white);padding:6px 12px;border-radius:6px}.tutorial{border-bottom:1px solid var(--divider-color,#dce3e8);padding:16px 0}.tutorial h3{margin:0;font-size:17px}.tutorial p{white-space:pre-wrap}.document-list{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}.pdf{display:block;width:100%;height:auto;border:0;margin-top:12px;background:white}.pdf-link{display:block;margin:12px 0} @media(max-width:720px){.child-grid{grid-template-columns:1fr}.school-logo{width:42px;height:42px}.pager{flex-wrap:wrap}}

        .teachers{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:0 0 30px}.teacher{display:flex;gap:16px;padding:16px;background:var(--card-background-color,white);border:1px solid var(--divider-color,#dce3e8);border-radius:8px;min-width:0}.portrait{flex:0 0 80px;height:100px;display:flex;align-items:center;justify-content:center;background:var(--secondary-background-color,#edf3f7);border-radius:6px;overflow:hidden;color:var(--secondary-text-color,#526575);font-size:13px}.portrait img{width:100%;height:100%;object-fit:cover;object-position:top}.teacher h3{font-size:17px;margin:0 0 6px;overflow-wrap:anywhere}.teacher p{font-size:14px;color:var(--secondary-text-color,#526575);margin:0}.teacher-details{min-width:0}
      </style>
      <main>
        <header><button class="menu-toggle" aria-label="Abrir menú lateral">☰</button><img class="school-logo" src="/casvi-logo.png" alt="Casvi"><div><h1>Colegio</h1><p class="subtitle">La agenda de casa, al día.</p></div><span class="spacer"></span><select id="account" aria-label="Cuenta familiar" hidden></select><button id="reload">Actualizar panel</button></header>
        <nav id="tabs" aria-label="Secciones del colegio" role="tablist"></nav><div id="error" role="status" class="error" hidden></div><p id="loading" role="status">Cargando el colegio…</p>
        <div id="content" class="grid" hidden>
          <section id="overview-side"><div class="menu"><div id="date" class="date"></div><h2>Hoy en el comedor</h2><p id="menu"></p></div><h2>Próximos en la agenda</h2><ul id="events" class="events"></ul></section>
          <section><div class="toolbar"><h2 id="messages-title">Últimos mensajes</h2><button id="filter" aria-pressed="false">Solo pendientes</button></div><p id="count" class="hint"></p><div id="messages"></div><div id="pager" class="pager" hidden><button id="previous">Anterior</button><span id="page-label"></span><button id="next">Siguiente</button></div><p class="hint">Abrir un mensaje consulta su contenido en Casvi y podría cambiar su estado de lectura. Consultar este panel no abre los pendientes.</p><p id="notification-state" class="hint"></p><a href="/config/integrations/integration/casvi">Configurar avisos</a></section>
        </div>
        <section id="child-view" hidden><div class="child-heading"><h2 id="child-name"></h2><p id="child-group"></p><p id="child-tutor"></p><p id="child-status" role="status"></p></div><section id="teacher-section"><h2>Profesores</h2><div id="teachers" class="teachers"></div></section><div id="child-data" class="child-grid"><section><h2>Horario y documentos</h2><div id="documents" class="document-list"></div><h2>Tutorías</h2><div id="tutorials"></div></section><section><h2>Compañeros de clase</h2><ul id="classmates" class="people"></ul><h2>Próximos eventos</h2><ul id="child-events" class="events"></ul><h2>Mensajes recientes</h2><div id="child-messages"></div></section></div></section>
        <dialog><div class="dialog-head"><h2 id="subject"></h2><button id="close" aria-label="Cerrar">Cerrar</button></div><p id="sender" class="hint"></p><div id="body" class="body" role="status"></div><div id="attachments"></div><p class="links"><a id="intranet-link" href="https://intranet.casvi.es/pages/mensajes.php" target="_blank" rel="noopener noreferrer">Abrir la intranet de Casvi</a></p><p id="attachment-note" class="hint">Para descargar adjuntos, entra en la intranet con tu cuenta.</p></dialog>
      </main>`;
    this.$('reload').onclick = () => this.view==='messages'?this.loadPage(this.offset):this.view.startsWith('child:')?this.loadChild():this.load();
    this.$('account').onchange = () => {this.page=null;this.profile=null;this.view='home';this.render();};
    this.$('previous').onclick=()=>this.loadPage(Math.max(0,this.offset-20));
    this.$('next').onclick=()=>this.loadPage(this.offset+20);
    this.$('filter').onclick = () => {this.onlyUnread = !this.onlyUnread; this.render();};
    this.$('close').onclick = () => {this.requestId = (this.requestId || 0) + 1; this.shadowRoot.querySelector('dialog').close(); this.clearPDF();};
    this.shadowRoot.querySelector('.menu-toggle').onclick = () => this.dispatchEvent(new Event('hass-toggle-menu',{bubbles:true,composed:true}));
  }
  $(id) {return this.shadowRoot.getElementById(id);}
  set hass(value) {this._hass=value; if(this.isConnected && !this.started){this.started=true; this.load();} this.handleDeepLink();}
  set route(value) {this._route=value; this.handleDeepLink();}
  connectedCallback() {if(this._hass && !this.started){this.started=true;this.load();} this.timer=setInterval(()=>this.load(),30000);}
  disconnectedCallback() {clearInterval(this.timer);this.clearPDF();this.started=false;}
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
    this.$('content').hidden=!a || this.view.startsWith('child:');
    this.$('child-view').hidden=!a || !this.view.startsWith('child:');
    if(!a){this.$('error').textContent='Añade tu cuenta en Ajustes → Dispositivos y servicios → Casvi.';this.$('error').hidden=false;return;}
    this.renderTabs(a);
    if(this.view.startsWith('child:')) {this.renderChild(a);return;}
    this.$('content').classList.toggle('inbox',this.view==='messages');
    this.$('overview-side').hidden=this.view==='messages';
    this.$('messages-title').textContent=this.view==='messages'?'Todos los mensajes':'Últimos 10 mensajes';
    this.$('filter').hidden=this.view==='messages';
    this.$('pager').hidden=this.view!=='messages';
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
    this.$('count').textContent=this.view==='messages'?`${this.page?.total??a.total_messages} mensajes en el buzón`:`${a.messages.filter(m=>!m.read).length} pendientes entre los ${a.messages.length} mensajes consultados.`;
    this.$('previous').disabled=this.pageLoading||this.offset===0;
    this.$('next').disabled=this.pageLoading||!this.page||this.offset+20>=this.page.total;
    this.$('page-label').textContent=this.pageLoading?'Cargando…':`Página ${Math.floor(this.offset/20)+1} de ${Math.max(1,Math.ceil((this.page?.total||0)/20))}`;
    this.$('filter').setAttribute('aria-pressed',String(!!this.onlyUnread));
    this.$('filter').textContent=this.onlyUnread?'Mostrar todos':'Solo pendientes';
    this.$('messages').replaceChildren();
    const rows=this.view==='messages'?(this.page?.messages||[]):a.messages.slice(0,10).filter(m=>!this.onlyUnread||!m.read);
    this.renderMessages(rows,a,this.$('messages'));
    this.$('notification-state').textContent=a.notifications?'Avisos activados para los móviles seleccionados.':'Activa los avisos al móvil en las opciones de Casvi.';
  }
  currentAccount(){return this.accounts.find(a=>a.entry_id===this.$('account').value)||this.accounts[0];}
  recipientLabel(m){return (m.children||[]).map(c=>c.name).join(', ')||'Destinatario no indicado por Casvi';}
  renderTabs(a){
    const tabs=[['home','Inicio'],['messages','Todos los mensajes'],...(a.children||[]).map(c=>['child:'+c.id,c.name])];
    this.$('tabs').replaceChildren(...tabs.map(([value,label])=>{
      const b=document.createElement('button');b.textContent=label;b.setAttribute('role','tab');b.setAttribute('aria-selected',String(this.view===value));
      b.onclick=()=>{this.view=value;this.onlyUnread=false;this.$('error').hidden=true;if(value==='messages'){this.page=null;this.offset=0;this.loadPage(0);}else if(value.startsWith('child:')){this.profile=null;this.loadChild();}this.render();};return b;
    }));
  }
  renderMessages(rows,a,container){
    container.replaceChildren();
    rows.forEach(m=>{
      const b=document.createElement('button');b.className='row';
      if(!m.read){const badge=document.createElement('span');badge.className='badge';badge.textContent='Pendiente';b.append(badge);}
      const title=document.createElement('span');title.className='subject';title.textContent=m.subject||'Sin asunto';
      const meta=document.createElement('span');meta.className='meta';meta.textContent=`${m.sender} · ${m.date.slice(0,16)}`;
      const recipient=document.createElement('span');recipient.className='recipient';recipient.textContent=this.recipientLabel(m);
      b.append(title,meta,recipient);b.onclick=()=>this.openMessage(a.entry_id,m.id,m.id_para);container.append(b);
    });
    if(!rows.length){const empty=document.createElement('p');empty.className='empty';empty.textContent=this.pageLoading?'Cargando mensajes…':'No hay mensajes en esta vista.';container.append(empty);}
  }
  async loadPage(offset){
    const a=this.currentAccount();if(!a)return;
    const request=this.pageRequest=(this.pageRequest||0)+1;
    this.pageLoading=true;this.offset=offset;this.page=null;this.render();
    try{
      const page=await this._hass.callWS({type:'casvi/messages',entry_id:a.entry_id,start:offset,length:20});
      if(request!==this.pageRequest||this.currentAccount()?.entry_id!==a.entry_id)return;
      this.page=page;this.$('error').hidden=true;
    }catch(_){this.$('error').textContent='No se pudo cargar esta página. Pulsa Actualizar panel para reintentar.';this.$('error').hidden=false;}
    finally{if(request===this.pageRequest){this.pageLoading=false;this.render();}}
  }
  async loadChild(){
    const a=this.currentAccount();const id=this.view.slice(6);if(!a||!a.children.some(c=>c.id===id))return;
    const request=this.childRequest=(this.childRequest||0)+1;this.childLoading=true;this.profile=null;this.render();
    try{
      const profile=await this._hass.callWS({type:'casvi/child',entry_id:a.entry_id,child_id:id});
      if(request!==this.childRequest||this.currentAccount()?.entry_id!==a.entry_id||this.view!=='child:'+id)return;
      this.profile=profile;this.$('error').hidden=true;this.loadTeacherPhotos(a.entry_id,id,profile,request);
    }catch(_){this.$('error').textContent='No se pudo cargar la ficha. Pulsa Actualizar panel para reintentar.';this.$('error').hidden=false;}
    finally{if(request===this.childRequest){this.childLoading=false;this.render();}}
  }
  renderChild(a){
    const id=this.view.slice(6);const child=(a.children||[]).find(c=>c.id===id);const p=this.profile;
    this.$('child-name').textContent=child?.name||'Alumno';this.$('child-status').textContent=this.childLoading?'Cargando la ficha…':p?'':'La ficha todavía no está disponible.';
    this.$('child-group').textContent=p?.group||'';this.$('child-tutor').textContent=p?.tutor?'Tutor: '+p.tutor:'';this.$('child-data').hidden=!p;this.$('teacher-section').hidden=!p;if(!p)return;this.renderTeachers(p);
    this.$('classmates').replaceChildren(...p.classmates.map(name=>{const li=document.createElement('li');li.textContent=name;return li;}));
    if(!p.classmates.length)this.$('classmates').textContent='No hay compañeros disponibles.';
    this.$('documents').replaceChildren();
    [...p.documents].sort((x,y)=>Number(/horario/i.test(y.title))-Number(/horario/i.test(x.title))).forEach(d=>{const b=document.createElement('button');b.textContent=d.title||'Documento';b.onclick=()=>this.openDocument(a.entry_id,id,d);this.$('documents').append(b);});
    if(!p.documents.length)this.$('documents').textContent='No hay documentos publicados para la familia.';
    this.$('tutorials').replaceChildren();
    [...p.tutorials].sort((x,y)=>y.date.localeCompare(x.date)).forEach(t=>{
      const article=document.createElement('article');article.className='tutorial';const h=document.createElement('h3');h.textContent=t.reason||'Tutoría';const date=document.createElement('p');date.className='meta';date.textContent=t.date.slice(0,16)+' · '+t.teacher;article.append(h,date);
      for(const text of [t.summary,t.plan])if(text){const body=document.createElement('p');body.textContent=text;article.append(body);}this.$('tutorials').append(article);
    });
    if(!p.tutorials.length)this.$('tutorials').textContent='No hay tutorías registradas.';
    this.$('child-events').replaceChildren();
    a.events.filter(e=>e.child_id===id).slice(0,10).forEach(e=>{const li=document.createElement('li');li.textContent=e.title+' · '+new Date(e.start).toLocaleString('es-ES',{timeZone:'Europe/Madrid'});this.$('child-events').append(li);});
    if(!this.$('child-events').children.length)this.$('child-events').textContent='No hay próximos eventos.';
    this.renderMessages(a.messages.filter(m=>(m.children||[]).some(c=>c.id===id)).slice(0,10),a,this.$('child-messages'));
  }
  renderTeachers(profile){
    const container=this.$('teachers');container.replaceChildren();
    for(const teacher of profile.teachers||[]){
      const card=document.createElement('article');card.className='teacher';
      const portrait=document.createElement('div');portrait.className='portrait';
      if(teacher.photo){const img=document.createElement('img');img.src=teacher.photo;img.alt='Foto de '+teacher.name;img.loading='lazy';img.onerror=()=>{portrait.textContent='Sin foto';};portrait.append(img);}
      else portrait.textContent=teacher.photoState==='missing'?'Sin foto':'Cargando…';
      const details=document.createElement('div');details.className='teacher-details';const name=document.createElement('h3');name.textContent=teacher.name;const subjects=document.createElement('p');subjects.textContent=teacher.subjects.join(', ')||'Asignatura no indicada';details.append(name,subjects);card.append(portrait,details);container.append(card);
    }
    if(!(profile.teachers||[]).length)container.textContent=profile.teachers_available===false?'No se pudieron cargar los profesores. Pulsa Actualizar panel para reintentar.':'Casvi no ha publicado profesores para este grupo.';
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
  clearPDF(){if(this.pdfTask){this.pdfTask.destroy().catch(()=>{});this.pdfTask=null;}if(this.pdfURL){URL.revokeObjectURL(this.pdfURL);this.pdfURL=null;}this.shadowRoot.querySelectorAll('.pdf,.pdf-link').forEach(e=>e.remove());}
  async openDocument(entry,child,documentInfo){
    const request=this.requestId=(this.requestId||0)+1;this.clearPDF();this.$('attachment-note').hidden=true;this.$('intranet-link').href='https://intranet.casvi.es/pages/'+(documentInfo.kind==='documentoGrupo'?'infoGrupoDelAlumno.php':'infoDocumentosDelAlumno.php')+'?idAlumno='+encodeURIComponent(child);this.$('subject').textContent=documentInfo.title;this.$('sender').textContent='';this.$('body').textContent='Cargando PDF…';this.$('attachments').replaceChildren();
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
  async openMessage(entry,id,recipient) {
    const request=this.requestId=(this.requestId||0)+1;
    this.clearPDF();this.$('attachment-note').hidden=false;this.$('intranet-link').href='https://intranet.casvi.es/pages/mensajes.php';
    this.$('subject').textContent='Mensaje';this.$('sender').textContent='';this.$('body').textContent='Cargando mensaje…';this.$('attachments').replaceChildren();
    const dialog=this.shadowRoot.querySelector('dialog');if(!dialog.open) dialog.showModal();
    try {
      const m=await this._hass.callWS({type:'casvi/message',entry_id:entry,message_id:id,recipient_id:recipient});
      if(request!==this.requestId) return;
      this.$('subject').textContent=m.subject;this.$('sender').textContent=m.sender+' · '+this.recipientLabel(m);this.$('body').textContent=m.content||'Este mensaje no contiene texto.';
      if(m.attachments.length){const h=document.createElement('h3');h.textContent='Adjuntos';const ul=document.createElement('ul');m.attachments.forEach(name=>{const li=document.createElement('li');li.textContent=name;ul.append(li);});this.$('attachments').append(h,ul);}
    } catch (_) {if(request===this.requestId)this.$('body').textContent='No se pudo abrir el mensaje. Puede haber salido de la lista reciente. Inténtalo de nuevo o entra en la intranet.';}
  }
}
if(!customElements.get('casvi-school-panel')) customElements.define('casvi-school-panel',CasviSchoolPanel);
