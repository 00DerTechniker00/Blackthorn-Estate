# In der richtigen Dimension ausführen; Koordinaten beziehen sich auf das Anwesen.
# Erzeugt nur fehlende, eindeutig markierte Rüstungsständer. Erneutes Ausführen setzt ihre Ausrüstung zurück.
execute unless entity @e[type=minecraft:armor_stand,tag=blackthorn_display_leather,limit=1] run summon minecraft:armor_stand -743.5 126 764.5 {Tags:["blackthorn_display_leather"],ShowArms:1b,NoGravity:1b,Rotation:[180f,0f]}
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_leather,limit=1] armor.head with minecraft:leather_helmet
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_leather,limit=1] armor.chest with minecraft:leather_chestplate
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_leather,limit=1] armor.legs with minecraft:leather_leggings
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_leather,limit=1] armor.feet with minecraft:leather_boots
execute unless entity @e[type=minecraft:armor_stand,tag=blackthorn_display_diamond,limit=1] run summon minecraft:armor_stand -741.5 126 764.5 {Tags:["blackthorn_display_diamond"],ShowArms:1b,NoGravity:1b,Rotation:[180f,0f]}
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_diamond,limit=1] armor.head with minecraft:diamond_helmet
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_diamond,limit=1] armor.chest with minecraft:diamond_chestplate
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_diamond,limit=1] armor.legs with minecraft:diamond_leggings
item replace entity @e[type=minecraft:armor_stand,tag=blackthorn_display_diamond,limit=1] armor.feet with minecraft:diamond_boots
# Regale nach dem Strukturimport bestücken; setzt die sechs vorgesehenen Fächer neu.
item replace block -694 106 778 container.0 with minecraft:book
item replace block -694 106 778 container.1 with minecraft:air
item replace block -694 106 778 container.2 with minecraft:air
item replace block -694 106 778 container.3 with minecraft:air
item replace block -694 106 778 container.4 with minecraft:air
item replace block -694 106 778 container.5 with minecraft:air
item replace block -691 106 778 container.0 with minecraft:book
item replace block -691 106 778 container.1 with minecraft:book
item replace block -691 106 778 container.2 with minecraft:air
item replace block -691 106 778 container.3 with minecraft:air
item replace block -691 106 778 container.4 with minecraft:air
item replace block -691 106 778 container.5 with minecraft:air
item replace block -688 106 778 container.0 with minecraft:book
item replace block -688 106 778 container.1 with minecraft:book
item replace block -688 106 778 container.2 with minecraft:book
item replace block -688 106 778 container.3 with minecraft:book
item replace block -688 106 778 container.4 with minecraft:air
item replace block -688 106 778 container.5 with minecraft:air
item replace block -691 106 781 container.0 with minecraft:book
item replace block -691 106 781 container.1 with minecraft:book
item replace block -691 106 781 container.2 with minecraft:book
item replace block -691 106 781 container.3 with minecraft:book
item replace block -691 106 781 container.4 with minecraft:book
item replace block -691 106 781 container.5 with minecraft:book
