# hyggeland

Mine rocks, chop trees, loot corpses, battle rogue werewolves, berate the town drunk. All is permitted in Hyggeland.
Player starts with a few test things in inventory, manually put there towards end of main.py (going to change name to name.py)

Game Items:

Tree, Spire, Log, Apple, Pumpkin, Wheat, Corpse, Rocks, Stone, Sap, Pond, WheatPatch, 
PumpkinPatch, Water, Fish, Iron, Vines, Cart, goldCoin, CoinPurse, Hide, RatTail,
Grave, Bones

Craftable Items:

Spade, Knife, Axe, Pickaxe, Spear, Hammer, FirePit, Bucket, Rod, Furnace, Charcoal, IronIngot, 
Scythe, IronSword, Whip, Anvil, Rope, String, Bow, Arrow, HideVest, Flour, PieCrust, Bowl, 
AppleFilling, ApplePie, PumpkinFilling, PumpkinPie

Player commands:

"equip [toEquip]" (equip Spear)
"unequip [item]" (unequip Knife)
"commands" (lists available commands)
"status" (player health and other stats)
"myStats" (different format status with other stuff)
"attack [target]" (attack Troll)
"trade [npcToEngage]" (trade Merchant)
"talk [npcToTalk]" (talk John)
"buy [Item]" (buy Iron (do while trading npc))
"inv" (list what's in player inventory)
"look" (examine the area around you)
"who" (lists npcs and monsters nearby)
"scout" (scout area for resources and items)
"examine [target]" (examine Tree)
"take [itemName]" (take Axe)
"put [Thing] [target]" (put Axe Tree)
"gather [Resource] [target]" (gather Vines Tree)
"cook [itemName]" (cook Fish)
"drop [itemName]" (drop Log)
"eat [foodName]" (eat Apple)
"move [moveTo]" (move n (moves north))
"revive" (must be in same area as a Spire)

Adding Rooms:

roomX = Place()
roomX.gridLoc = [x,y]
roomX.exits = [array of exits 'n', 's', 'e', and/or 'w'] (must manually link to connected rooms and add corresponding exit)
roomX.description = "just info about the area"
roomX.objects.append(gameObject()) loop through randomly generated items and append to room.objects
                                   you can do the same adding to trees/rocks/corpses etc .resources (to be looted/harvested etc)

Items:

There are a few different types of items:
    resources (vines, rocks, sap etc)
    craftable items (spear, anvil, bow etc)
    immovable items (anvil, tree, rocks etc)
    edible items (apple, fish, wheat etc)\
    
They all share the following attributes:
    name
    description
    resources []
    canBeTaken bool
    toolTypeNeeded []

Edible stuff has an attr .edible [bool, int[hp it heals]
Cookable stuff has cooked bool and a cook function (fxn changes cooked bool and description)
Movable items (most of them) have a .price attr for trading
Weapons and most craftables have the following attrs:
    waste [list of materials to craft item]
    craftTool [list of tools needed in inventory to craft item] (I think at current it only works with one req'd item?)
    equipTo [hand, body etc]
    stats {"strength":2,"defense":0}
beyond that pretty much just make sure if you're making a new game obj that all the attributes are there
just copy one as a template and fill in the blanks and it should work
NOTE: some craftable items require a certain item be on the ground (i.e. anvil for sword)
      so give it the .groundTool = [array of ground tools needed] (again I think only 1 ground tool at a time works for now)

room1 (starting room) has a spire so if you get killed by the werewolf or something
just find your walk back there and type "revive"
There's an axe laying around in one of the first rooms, pick it up and 
get ready to fight the werewolf, it'll find you eventually
quests working but not really scalable, everything else is somewhat solid

    
