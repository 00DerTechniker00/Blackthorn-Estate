/* Small metal frame and a separate luminous core. Coordinates are sixteenths. */
function lanternParts(r) {
  const hanging=r.p.hanging==='true',offset=hanging?2:0;
  const frame=[.24,.26,.25],light=r.id==='soul_lantern'?[.27,.83,.9]:[1,.72,.27];
  const pieces=[
    {box:[5,offset,5,11,offset+1,11],color:frame},
    {box:[5.7,offset+1,5.7,10.3,offset+7,10.3],color:light},
    {box:[5,offset+7,5,11,offset+8,11],color:frame},
    ...[[5,5],[10.25,5],[5,10.25],[10.25,10.25]].map(([x,z])=>({box:[x,offset+1,z,x+.75,offset+7,z+.75],color:frame})),
    {box:[6,offset+8,7,7,offset+11,9],color:frame},
    {box:[9,offset+8,7,10,offset+11,9],color:frame},
    {box:[6,offset+10,7,10,offset+11,9],color:frame}
  ];
  if(hanging)pieces.push({box:[7,13,7,9,16,9],color:frame});
  return pieces;
}
