import test from 'node:test';
import assert from 'node:assert/strict';
import {parseSchedule,daySchedule} from '../custom_components/casvi/frontend/schedule.mjs';
function fixture(split=false){
 const item=(str,x,y,width=50)=>({str,transform:[1,0,0,1,x,y],width});
 const items=['LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES'].map((d,i)=>item(d,130+i*100,700));
 for(let r=0;r<3;r++){
  const y=660-r*60;
  if(split){items.push(item(`De: 0${9+r}:00`,20,y+10),item(`a: ${10+r}:00`,20,y-10));}
  else items.push(item(`${9+r}:00-${10+r}:00`,20,y));
  for(let d=0;d<5;d++){
   items.push(item(d===1&&r===0?'NATACIÓN':d===4&&r===1?'EF/NAT':r===2?'PSICOMOTRICIDAD':'LENGUA',130+d*100,y));
   if(split)items.push(item('Docente Ejemplo',130+d*100,y-12));
  }
 }
 return items;
}
test('Extracts five columns and ignores staff names in split time template',()=>{
 for(const split of [false,true]){
  const result=parseSchedule(fixture(split));
  assert.equal(result.rows.length,3);assert.equal(result.rows[0].start,'09:00');
  assert.equal(result.rows[0].subjects[1],'NATACIÓN');
  assert.equal(result.rows[1].subjects[4],'EF/NAT');
  assert.ok(result.rows.every(r=>r.subjects.every(s=>!s.includes('Docente'))));
 }
});
test('EF/NAT means swimming, weekends empty and psychomotor separate',()=>{
 const schedule=parseSchedule(fixture());
 assert.equal(daySchedule(schedule,1).swimming,true);
 const friday=daySchedule(schedule,4);
 assert.equal(friday.combined,false);assert.equal(friday.swimming,true);assert.equal(friday.physical,false);assert.equal(friday.psychomotor,true);
 assert.equal(daySchedule(schedule,5).rows.length,0);
});
test('Missing weekdays and cells fail closed',()=>{
 assert.throws(()=>parseSchedule([]));
 assert.throws(()=>parseSchedule(fixture().filter(i=>i.str!=='NATACIÓN')));
});
