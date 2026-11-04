import {floorAtY} from './data.js';
export function createStore(model){
 const key='blackthorn-progress-v5';let progress={};try{progress=JSON.parse(localStorage.getItem(key)||'{}')||{}}catch{progress={}}
 let current={view:'overview',renderMode:'3d',displayMode:'floor',group:'all',floorY:129,layerY:129,yaw:-.68,zoom:1,panX:0,panY:0,
  planFloorY:129,planGroup:'all',planMode:'floor',planLayerY:130,planZoom:1,planPanX:0,planPanY:0,showMarkers:true,
  materialGroup:'all',materialSearch:'',materialSort:'count',coordinateSearch:'',selected:null,progress};
 const subscribers=new Set;
 return {
  get:()=>current,
  patch(patch){const previous=current;current={...current,...patch};const changed=Object.keys(patch).filter(k=>current[k]!==previous[k]);if(changed.length)for(const fn of subscribers)fn(current,previous,changed);},
  subscribe(fn){subscribers.add(fn);return ()=>subscribers.delete(fn)},
  toggleGroup(group,done){const next={...current.progress,[group]:done};try{localStorage.setItem(key,JSON.stringify(next))}catch(e){console.warn('Baufortschritt konnte nicht gespeichert werden',e)}this.patch({progress:next})},
  floorAt(y){return floorAtY(model,y)}
 };
}
