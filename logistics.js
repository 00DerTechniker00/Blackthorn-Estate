/* Capacity/flow specification, deliberately not a Minecraft redstone simulator. */
(() => {
  'use strict';
  function bulk(amount,emptyBoxes=27,ready=0,storedBoxes=0) {
    for(const v of [amount,emptyBoxes,ready,storedBoxes])if(!Number.isSafeInteger(v)||v<0)throw Error('Nur nichtnegative ganze Zahlen verwenden.');
    if(ready>1728||storedBoxes>81)throw Error('Kapazität überschritten.');
    const refill=Math.min(amount,1728-ready);let rest=amount-refill;
    const completed=Math.min(Math.floor(rest/1728),emptyBoxes,81-storedBoxes);
    rest-=completed*1728;
    const partial=emptyBoxes>completed&&storedBoxes+completed<81?Math.min(rest,1727):0;
    rest-=partial;
    return {ready:ready+refill,refill,full_boxes:completed,stored_boxes:storedBoxes+completed,active_items:partial,
      unaccepted:rest,accepted:amount-rest,empty_remaining:emptyBoxes-completed-(partial>0?1:0),
      blocked:rest>0,reason:rest>0?(storedBoxes+completed>=81?'Shulker-Ausgang voll':'Leere Shulker fehlen'):''};
  }
  function rare(item,amount,targets) {
    if(!Number.isSafeInteger(amount)||amount<0)throw Error('Ungültige Menge');
    const target=targets.find(t=>t.seeds.includes(item));
    return {matched:!!target,target:target?.id||null,label:target?.label||'Manuell zuordnen',items:amount,
      trips:Math.ceil(amount/16),note:'Typ-/Kapazitätsmodell; keine Simulation von Golem-KI, Komponenten oder Redstone-Ticks.'};
  }
  window.Logistics={bulk,rare};
})();
