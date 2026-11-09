"""Convert block states to placeable items and keep the terrain budget explicit."""
from collections import Counter

OUTDOOR={'v6_ankunftsweg','v6_stall','v6_stallweg','v6_gartenpflege','v6_pool','v6_garten','zufahrt','terrasse','pool','gartendeko','poolboegen','klippenfuesse','kaskaden','klippenvegetation','gartentreppe','stall_remise','orangerie','gartenlicht','steglicht','ruestungsnischen','weinberg','klippenpfad','bootshaus'}

def items_for_block(block,state):
    if block in ('air','water','bubble_column','piston_head') or block.endswith('_door') and 'half=upper' in state or block.endswith('_bed') and 'part=head' in state:return []
    if block.startswith('potted_'):return [('flower_pot',1),(block.removeprefix('potted_'),1)]
    aliases={'water_cauldron':'cauldron','redstone_wall_torch':'redstone_torch','wall_torch':'torch','soul_wall_torch':'soul_torch'}
    item=aliases.get(block,block.replace('_wall_banner','_banner').replace('_wall_hanging_sign','_hanging_sign').replace('_wall_sign','_sign'))
    return [(item,2 if block.endswith('_slab') and 'type=double' in state else 1)]

def stack_size(item):
    if item.endswith('_bed') or item.endswith('shulker_box') or item.endswith('_bucket'):return 1
    if item.endswith(('_banner','_sign')) or item=='armor_stand':return 16
    return 64

def scopes(gcounts):
    output={key:{'label':label,'counts':Counter()} for key,label in [('house','Haus und Keller'),('outdoor','Außenanlagen und Nebengebäude'),('terrain','Gelände und Auffüllung')]}
    for group,counts in gcounts.items():
        key='terrain' if (group.startswith('terraform_') or group in ('v6_gelaendepflege','v6_stall_rueckbau')) else 'outdoor' if group in OUTDOOR else 'house'
        output[key]['counts'].update(counts)
    return {key:{'label':value['label'],'counts':dict(value['counts'])} for key,value in output.items()}
