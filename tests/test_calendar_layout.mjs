import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
function element(){return {children:[],classList:{add(){}},append(...items){this.children.push(...items)},replaceChildren(...items){this.children=items}}}
function panel(events){
 let Panel;
 vm.runInNewContext(readFileSync(new URL('../custom_components/casvi/frontend/casvi-panel.js',import.meta.url),'utf8'),{HTMLElement:class{},customElements:{get(){},define(name,cls){Panel=cls}},matchMedia:()=>({matches:false}),document:{createElement:element},Intl,Date});
 const p=Object.create(Panel.prototype), nodes={};p.$=id=>nodes[id]??=element();p.eventCard=()=>element();p.emptyState=()=>element();
 p.renderEvents({entry_id:'test',date:'2026-11-02',events});return nodes;
}
test('Empty event month hides its grid',()=>{
 const nodes=panel([]);assert.equal(nodes['events-grid'].hidden,true);assert.equal(nodes['events-grid'].children.length,0);
});
test('Sunday-start month has no blank first weekday row',()=>{
 const nodes=panel([{start:'2026-11-02T09:00:00',title:'Class'}]);
 const cells=nodes['events-grid'].children;assert.equal(nodes['events-grid'].hidden,false);
 assert.equal(cells[5].children[0].dateTime,'2026-11-02');
 assert.equal(cells[9].children[0].dateTime,'2026-11-06');
});
