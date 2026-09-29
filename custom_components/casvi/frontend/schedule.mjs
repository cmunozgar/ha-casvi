/* Extract text tables only. Unsupported layouts fail closed; no OCR guesses. */
const DAYS=['lunes','martes','miercoles','jueves','viernes'];
const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
function lines(items){
  const result=[];
  for(const item of [...items].sort((a,b)=>b.y-a.y||a.x-b.x)){
    let line=result.find(l=>Math.abs(l.y-item.y)<2);
    if(!line){line={y:item.y,items:[]};result.push(line);}line.items.push(item);
  }
  return result.map(l=>({...l,text:l.items.sort((a,b)=>a.x-b.x).map(i=>i.text).join(' ').replace(/\s+/g,' ').trim()}));
}
const minutes=t=>{const [h,m]=t.split(':').map(Number);return h*60+m;};
export function parseSchedule(items){
  const text=items.filter(i=>i.str?.trim()&&i.transform).map(i=>({text:i.str.trim(),x:i.transform[4],y:i.transform[5],w:i.width||0}));
  const headers=DAYS.map(d=>text.find(i=>normalize(i.text)===d));
  if(headers.some(h=>!h)||Math.max(...headers.map(h=>h.y))-Math.min(...headers.map(h=>h.y))>3)throw Error('Unsupported weekday headings');
  const centers=headers.map(h=>h.x+h.w/2);
  if(centers.some((x,i)=>i&&x<=centers[i-1]))throw Error('Unsupported column order');
  const left=centers[0]-(centers[1]-centers[0])/2;
  const right=centers[4]+(centers[4]-centers[3])/2;
  const headerY=headers[0].y;
  const timeLines=lines(text.filter(i=>i.x<left&&i.y<headerY));
  const rows=[];let pending=null;
  for(const line of timeLines){
    const times=[...line.text.matchAll(/(\d{1,2})\s*:\s*(\d{2})/g)].map(m=>`${m[1].padStart(2,'0')}:${m[2]}`);
    if(times.length===2){rows.push({start:times[0],end:times[1],y:line.y});pending=null;}
    else if(times.length===1&&/^de\s*:/i.test(line.text)){pending={start:times[0],y:line.y};}
    else if(times.length===1&&/^a\s*:/i.test(line.text)&&pending){rows.push({start:pending.start,end:times[0],y:(pending.y+line.y)/2});pending=null;}
  }
  if(rows.length<3||rows.length>16||rows.some((r,i)=>minutes(r.start)>=minutes(r.end)||minutes(r.end)>24*60||(i&&minutes(r.start)<minutes(rows[i-1].end))))throw Error('Unsupported time rows');
  const gaps=rows.slice(1).map((r,i)=>rows[i].y-r.y).sort((a,b)=>a-b);
  const pitch=gaps[Math.floor(gaps.length/2)];
  for(const [index,row] of rows.entries()){
    const top=index?(rows[index-1].y+row.y)/2:headerY-3;
    const bottom=index<rows.length-1?(row.y+rows[index+1].y)/2:row.y-pitch/2;
    row.subjects=centers.map((center,day)=>{
      const min=day?(centers[day-1]+center)/2:left;
      const max=day<4?(center+centers[day+1])/2:right;
      const cell=lines(text.filter(i=>i.x+i.w/2>=min&&i.x+i.w/2<max&&i.y<top&&i.y>bottom));
      // In the supported primary-school template, mixed-case lines are staff names.
      const subject=cell.filter(l=>l.text===l.text.toLocaleUpperCase('es')&&/[A-ZÁÉÍÓÚÜÑ]/.test(l.text)).map(l=>l.text).join(' ');
      if(!subject)throw Error('Empty or unsupported subject cell');
      return subject;
    });

  }
  return {days:DAYS,rows:rows.map(({y,...row})=>row)};
}
export function daySchedule(schedule,weekday){
  const rows=weekday>=0&&weekday<5?schedule.rows.map(r=>({start:r.start,end:r.end,subject:r.subjects[weekday]})):[];
  const subjects=rows.map(r=>normalize(r.subject));
  const combined=false;
  return {rows,swimming:subjects.some(s=>/natacion|piscina|\bef\s*\/\s*nat\b/.test(s)),physical:subjects.some(s=>/e\.?\s*fisica|educacion fisica|gimnasia/.test(s)),psychomotor:subjects.some(s=>/psicomotricidad/.test(s)),combined};
}
