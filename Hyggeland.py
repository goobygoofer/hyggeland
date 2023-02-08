#NOTE! hyggelandBulk import works! do this for other huge classes/etc, or maybe everything

import random
import copy
from threading import Thread
from tkinter import *
import time
from hyggelandBulk import *

class Place:
    def __init__(self):
        self.gridLoc = []#[x, y]
        self.exits = []#['n','s','e','w']
        self.terrain = [] #default grass field?
        self.objects = []
        self.description = ''
        self.NPCs = []

class NPCmove:#NPCs inherit this class, fxns they share go here. so far move() works!
    def __init__(self):
        pass#do you have to __init__ classes that only get inherited and never explicitly defined?
    
    def move(self):
        moveTo = self.currentRoom[0].exits[random.randrange(0,len(self.currentRoom[0].exits))]
        moveDict = {'n':[0,1],'s':[0,-1],'e':[1,0],'w':[-1,0]}
        moveCoord = [self.currentRoom[0].gridLoc[0]+moveDict[moveTo][0],self.currentRoom[0].gridLoc[1]+moveDict[moveTo][1]]
        count = 0
        for item in world.Places:
            if item.gridLoc == moveCoord:
                self.currentRoom.append(item)
                del self.currentRoom[0]
                break
            count+=1

class NPCfight:
    def __init__(self):
        pass
    
    def attack(self):
        if player.dead==False:
            game.displayText+="The " + self.name + " attacks you!\n\n"
            hit = random.randrange(0,self.stats["strength"])#again this will become more complex after engagement works
            game.threadQueue.append(player.getAttacked(hit))#change to target for relative reference(see self.update() notes)
        elif player.dead == True:
            self.aggro = False
            game.displayText+="The " + self.name + " senses your ghost...\n"

    def getAttacked(self, hit):
        #will have defense/armour/etc to mitigate hit
        defHit = hit-random.randrange(0,self.stats["defense"])
        if defHit<=0:
            game.displayText+="The " + self.name + " dodged your attack!\n\n"
        elif defHit>0:
            game.displayText+="You hit the " + self.name + " for " + str(defHit) + " damage!"
            self.health-=defHit
        #checking health at self.update will change dead bool to True, but might have to do that here depending on how threading acts

class NPCfetchQuest:
    def __init__(self):
        pass
    def checkComplete(self):
        #check if even have that many items
        haveCount=0
        self.checking=False
        for item in player.inventory:
            if item.name == self.toFetch.name:
                haveCount+=1
        if haveCount>=self.numToFetch:
            self.npcQuest = [False, True]#Person doesn't have quest, quest is complete
            #now del materials from inventory
            delPosCount = 0#position in tempList
            foundDel = False
            while self.numToFetch>0:
                for thing in player.inventory:
                    if thing.name == self.toFetch.name:
                        foundDel = True
                        break
                    else:
                        delPosCount+=1
                if foundDel == True:
                    #del needList[0]
                    del player.inventory[delPosCount]
                    delPosCount=0
                    self.numToFetch-=1
            self.npcQuest = [False, True]
    
       

class Cat(NPCmove):#NPC model
    def __init__(self):#so far it can "be" in a room and "know" what rooms it's in. needs autonomy without breaking threading/freezing
        self.currentRoom = []
        self.inventory = []
        self.health = 1000
        self.lastHealth = 1000
        self.lastTime = world.timePassed
        self.thisTime = None
        self.name = "Cat"
        self.description = "A feral cat that doesn't seems to mind humans..."
        self.greeted = False
        self.dead = False
        self.stats = {"strength":100,"defense":1}
        self.gotAttacked = False
        
    def getAttacked(self, hit):
        #will have defense/armour/etc to mitigate hit
        self.gotAttacked = True
        defHit = hit-random.randrange(0,self.stats["defense"])
        if defHit<=0:
            game.displayText+="The " + self.name + " dodged your attack!\n\n"
        elif defHit>0:
            game.displayText+="You hit the " + self.name + " for " + str(defHit) + " damage!"
            self.health-=defHit
        #checking health at self.update will change dead bool to True, but might have to do that here depending on how threading acts

    def update(self):#this is pretty much it's autonomy and AI?
        #called at main game loop
        #print(world.timePassed)
        if world.timePassed >= self.lastTime+5:
            game.threadQueue.append(self.move())
            self.lastTime = world.timePassed
        else:
            if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:
                if self.greeted == False:
                    game.displayText+="The cat, noticing your presence, meows politely\n\n"
                    self.greeted = True
            elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
                self.greeted = False
        if self.greeted == True and self.gotAttacked == True:
            player.catGrudge+=1
            self.gotAttacked = False
            self.health = 1000
            game.displayText+="a disembodied voice booms: DO YOU KNOW WHAT HAPPENS TO PEOPLE THAT HURT CATS?!\n"
            game.displayText+="The cat becomes a furious furor of fur and fangs as he shreds your cruel face to ribbons...\n"
            player.getAttacked(100)
            game.displayText+="disembodied voice: DO NOT hurt the cat...\n"
            game.threadQueue.append(self.move())
            
           

class Deer(NPCmove, NPCfight):
    def __init__(self):
        self.currentRoom = []
        self.inventory = []#maybe randomize inventory in monster NPCs, player.take("Coin", target)
                           #should take all coins from target, or maybe target has a coinPurse?
        self.resources = [] #had to use this for looting after killing it
        self.health = 10
        self.lastTime = world.timePassed
        self.name = "Deer"
        self.description = "A timid deer"
        self.greeted = False#in the same room @ self.update()
        self.aggro = False#not sure to use this for deer
        self.dead = False
        #stats
        self.stats = {"strength":0, "defense":2}
        #self.strength = 8#might not need this one, but will need defense when implemented?
        self.waitTime = 5
        self.previousHealth=self.health
        self.aggroCounter = 3

    def update(self):
        #print(self.currentRoom[0].gridLoc)
        if self.dead == False:
            if world.timePassed >= self.lastTime+self.waitTime and self.aggro == False:
                game.threadQueue.append(self.move())
                self.lastTime = world.timePassed
            elif self.aggro == True:
                self.aggroCounter-=1
                game.threadQueue.append(self.move())
        if self.aggroCounter<=0:
            self.aggro = False
            self.aggroCounter = 3
        if self.health<self.previousHealth:
            self.previousHealth = self.health
            self.aggro = True
            self.aggroCount = 3
        if self.health<=0:
            self.dead = True
            self.currentRoom[0].objects.append(self)

class Rat(NPCmove, NPCfight):#might be wise to use this as mould for monster NPCs, inheriting class and adding specifics?
    def __init__(self):
        self.currentRoom = []
        self.inventory = []#maybe randomize inventory in monster NPCs, player.take("Coin", target)
                           #should take all coins from target, or maybe target has a coinPurse?
        self.resources = [] #had to use this for looting after killing it
        for i in range(0,2):
            self.resources.append(goldCoin())
        self.resources.append(RatTail())
        self.health = 5
        self.lastTime = world.timePassed
        self.name = "Rat"
        self.description = "A flea infested rat! Careful not to catch the plague...\n\n"
        self.greeted = False#in the same room @ self.update()
        self.dead = False
        #stats
        self.stats = {"strength":3,"defense":1}#defense can't be 0 because error

    def update(self):
        #use the random move function if not aggro? only move within x # of rooms of origin room?
        if world.timePassed >= self.lastTime+5 and self.greeted==False:
            game.threadQueue.append(self.move())
            self.lastTime = world.timePassed
        #may first need to check health, needs way to stay permanently dead/decay/etc
        if self.health<=0:
            self.dead = True
            self.currentRoom[0].objects.append(self)
        if self.dead == False:
            if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc and player.dead==False:#can this not be done relatively? maybe scan currentRoom.whosThere, if aPlayer etc etc...
                if self.greeted == False:
                    self.greeted = True#initial greetings/warnings here?
            elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
                self.greeted = False
                #self.aggro = False #? Aggro might not even be necessary, unless monster NPC can chase player or something
            if self.greeted == True:
                if world.timePassed >= self.lastTime+3:
                    self.lastTime = world.timePassed
                    game.threadQueue.append(self.attack())

class Werewolf(NPCmove, NPCfight):
    def __init__(self):
        self.currentRoom = []
        self.inventory = []#maybe randomize inventory in monster NPCs, player.take("Coin", target)
                           #should take all coins from target, or maybe target has a coinPurse?
        self.resources = [] #had to use this for looting after killing it
        self.health = 25
        self.lastTime = world.timePassed
        self.name = "Werewolf"
        self.description = "A snarling, grotesque werewolf in tattered pants..."
        self.greeted = False#in the same room @ self.update()
        self.aggro = False#stays aggro until player is more than one move away
        self.dead = False
        #stats
        self.stats = {"strength":10,"defense":1}
        #self.strength = 8#get engagement working then make more complex
        self.waitTime = 10
        for i in range(0,3):
            self.resources.append(Hide())
        for i in range(0,random.randrange(0,2)):
            self.resources.append(IronSword())
        
    def update(self):
        #use the random move function if not aggro? only move within x # of rooms of origin room?
        if self.aggro == True:
            self.waitTime=1
        if world.timePassed >= self.lastTime+self.waitTime and self.greeted==False:
            if self.aggro == False:
                self.waitTime = 10
                game.threadQueue.append(self.move())
                self.lastTime = world.timePassed
            elif self.aggro == True and player.currentRoom[0].gridLoc!=self.currentRoom[0].gridLoc and player.dead==False:#aggro follow should be class NCPaggro, maybe classNPCfollow(friendly) should be separate
                #if player more than 2 moves away, self.aggro = False. compare currentRoom[0].gridLoc to player.currentRoom[0].gridLoc, check exits exist etc
                    #the exception being if player is 1 away but its in a diagonal direction, n/s/e/w only for now
                self.waitTime = 1
                doMove = False
                toCheck = [[1,0],[0,1],[-1,0],[0,-1]]#this checks nsew, need checks for ne/nw/se/sw
                possibleMoves = []
                for check in toCheck:
                    tempMove = []
                    tempMove.append(self.currentRoom[0].gridLoc[0]+check[0])
                    tempMove.append(self.currentRoom[0].gridLoc[1]+check[1])
                    possibleMoves.append(tempMove)
                if player.currentRoom[0].gridLoc in possibleMoves:
                    #move to player
                    print("went to player!")
                    self.currentRoom.append(player.currentRoom[0])
                    del self.currentRoom[0]
                else:
                    print("unaggroed!")
                    self.aggro = False
                #elif player 1 move away, move to player 
        #may first need to check health, needs way to stay permanently dead/decay/etc
        if self.health<=0:
            self.dead = True
            self.currentRoom[0].objects.append(self)
        if self.dead == False:
            if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:#can this not be done relatively? maybe scan currentRoom.whosThere, if aPlayer etc etc...
                if self.greeted == False:
                    self.greeted = True#initial greetings/warnings here?
                    self.aggro = True
            elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
                self.greeted = False
                #self.aggro = False #? Aggro might not even be necessary, unless monster NPC can chase player or something
            if self.greeted == True:
                if world.timePassed >= self.lastTime+1:
                    self.lastTime = world.timePassed
                    game.threadQueue.append(self.attack())

        

class Skeleton(NPCmove, NPCfight):#might be wise to use this as mould for monster NPCs, inheriting class and adding specifics?
    def __init__(self):
        self.currentRoom = []
        self.inventory = []#maybe randomize inventory in monster NPCs, player.take("Coin", target)
                           #should take all coins from target, or maybe target has a coinPurse?
        self.resources = [] #had to use this for looting after killing it
        for i in range(0,5):
            self.resources.append(goldCoin())
        if random.randrange(0,2)==1:
            self.resources.append(IronIngot())
        self.health = 25
        self.lastTime = world.timePassed
        self.name = "Skeleton"
        self.description = "An angry animated Skeleton. They only seem to attack if you get near them..."
        self.greeted = False#in the same room @ self.update()
        self.dead = False
        #stats
        self.stats = {"strength":5,"defense":2}
        #self.strength = 5#get engagement working then make more complex
        

    def update(self):
        #use the random move function if not aggro? only move within x # of rooms of origin room?
        if world.timePassed >= self.lastTime+5 and self.greeted==False:
            game.threadQueue.append(self.move())
            self.lastTime = world.timePassed
        #may first need to check health, needs way to stay permanently dead/decay/etc
        if self.health<=0:
            self.dead = True
            self.currentRoom[0].objects.append(self)
        if self.dead == False:
            if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc and player.dead==False:#can this not be done relatively? maybe scan currentRoom.whosThere, if aPlayer etc etc...
                if self.greeted == False:
                    self.greeted = True#initial greetings/warnings here?
            elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
                self.greeted = False
                #self.aggro = False #? Aggro might not even be necessary, unless monster NPC can chase player or something
            if self.greeted == True:
                if world.timePassed >= self.lastTime+3:
                    self.lastTime = world.timePassed
                    game.threadQueue.append(self.attack())
        #else:
            #for now it drops all loot to currentRoom[0] and removes itself from world.NPCs
            #pass#code here to stop updating/add to currentRoom inventory so it can be a looted item?

class Merchant:
    def __init__(self):
        self.currentRoom = []
        self.inventory = []
        self.health = 100
        self.lastTime = world.timePassed
        self.thisTime = None
        self.name = "Merchant"
        self.description = "A travelling merchant with a sack of goods.\n\nMaybe they have something good to sell..."
        self.greeted = False
        self.trading = False
        self.talking = False
        self.bought = False
        self.dead = False
        
    def update(self):
        if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:#not good because it's not relative, instead of player.whatever, self.engagedBy.whatever
            if self.greeted == False:
                game.displayText+="A merchant with a peculiarly large sack of goods is here...\n\n"
                self.greeted = True
        elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
            self.greeted = False
        if self.greeted == True:#check for player engagement etc
            if self.trading == True:
                self.trading = False
                game.displayText+="What would you like to buy?\n\n"
                game.displayText+="The merchant displays their goods:\n\n"
                for item in self.inventory:
                    game.displayText+=item.name + " : " + str(item.price) + "\n\n"
            if self.talking == True:
                self.talking = False
                game.displayText+="Hello, traveller... I've goods to sell if you have coin...\n\n"
        if self.bought == True:
            game.displayText+="It's a deal!\n\n"
            self.bought = False

    def sell(self, goods):
        #just deletes item from inventory
        itemCount = 0
        isThere = False
        for item in self.inventory:
            if item.name == goods:
                isThere=True
                break
            itemCount+=1
        if isThere == True:
            del self.inventory[itemCount]
        self.bought = True


class Person(NPCfetchQuest):#,NPCgreetPlayer):#fetchQuest NPC
    def __init__(self, name, description):
        self.currentRoom = []
        self.inventory = []
        self.health = 100
        self.lastTime = world.timePassed
        self.thisTime = None
        self.name = name
        self.description = description
        self.greeted = False
        self.talking = False
        self.bought = False
        self.dead = False
        self.npcTalk = "Sorry, I haven't got anything for you..."#default
        #             [hasQuest,questDone,accepted]
        self.npcQuest = [True, False]
        ##quest stuff? inheritance didn't work
        self.toFetch = None#just apples for now, change to randomly chosen game item
        self.numToFetch = random.randrange(1,6)
        #self.questInfo = "Could you bring me " + str(self.numToFetch) + " " + self.toFetch.name + " please?"
        self.reward = [goldCoin()]
        self.rewardAmt = random.randrange(5,10)
        #for i in range(0,random.randrange(5,10)):
        #   self.reward.append(goldCoin())#doesn't necessarily have to be actual coins
        self.completeText = "Thank you! Here, take this...\n\n"# + str(len(self.reward)) + " coins..."
        self.checking=False
        
    def update(self):
        self.questInfo = "Could you bring me " + str(self.numToFetch) + " " + self.toFetch.name + " please?"
        if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:#not good because it's not relative, instead of player.whatever, self.engagedBy.whatever
            if self.greeted == False:
                game.displayText+=self.name + " is here...\n\n"
                self.greeted = True
        elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
            self.greeted = False
        if self.greeted == True:
            if self.talking == True:
                if self.npcQuest[0]==False:
                    self.talking = False
                    game.displayText+=self.npcTalk + "\n\n"
                elif self.npcQuest[0]==True and self.checking==False:
                    self.talking = False
                    game.displayText+=self.questInfo + "\n\n"
                    self.checking=True
                    game.threadQueue.append(self.checkComplete())
        if self.npcQuest[0]==False and self.npcQuest[1]==True:
            self.npcQuest[1]=False
            game.displayText+=self.completeText + "\n\n"
            for i in range(0,self.rewardAmt):
                if self.reward[0].name=="Coin":
                    player.coinPurse.inventory.append(goldCoin())
                else:
                    player.inventory.append(self.reward[0])


class Troll(NPCmove, NPCfight):
    def __init__(self):
        self.currentRoom = []
        self.inventory = []#maybe randomize inventory in monster NPCs, player.take("Coin", target)
                           #should take all coins from target, or maybe target has a coinPurse?
        self.resources = [] #had to use this for looting after killing it
        self.health = 25
        self.lastTime = world.timePassed
        self.name = "Troll"
        self.description = "A massive, hairy troll... If he see's you he'll chase you down!"
        self.greeted = False#in the same room @ self.update()
        self.aggro = False#stays aggro until player is more than one move away
        self.dead = False
        #stats
        self.stats = {"strength":8,"defense":5}
        #self.strength = 8#get engagement working then make more complex
        self.waitTime = 3
        for i in range(0,3):
            self.resources.append(Hide())
        for i in range(0,random.randrange(0,1)):
            self.resources.append(IronSword())
        
    def update(self):
        #use the random move function if not aggro? only move within x # of rooms of origin room?
        if world.timePassed >= self.lastTime+self.waitTime and self.greeted==False:
            if self.aggro == False:
                self.waitTime = 3
                game.threadQueue.append(self.move())
                self.lastTime = world.timePassed
            elif self.aggro == True and player.currentRoom[0].gridLoc!=self.currentRoom[0].gridLoc and player.dead==False:#aggro follow should be class NCPaggro, maybe classNPCfollow(friendly) should be separate
                #if player more than 2 moves away, self.aggro = False. compare currentRoom[0].gridLoc to player.currentRoom[0].gridLoc, check exits exist etc
                    #the exception being if player is 1 away but its in a diagonal direction, n/s/e/w only for now
                self.waitTime = 2
                doMove = False
                toCheck = [[1,0],[0,1],[-1,0],[0,-1]]#this checks nsew, need checks for ne/nw/se/sw
                possibleMoves = []
                for check in toCheck:
                    tempMove = []
                    tempMove.append(self.currentRoom[0].gridLoc[0]+check[0])
                    tempMove.append(self.currentRoom[0].gridLoc[1]+check[1])
                    possibleMoves.append(tempMove)
                if player.currentRoom[0].gridLoc in possibleMoves:
                    #move to player
                    self.currentRoom.append(player.currentRoom[0])
                    del self.currentRoom[0]
                else:
                    self.aggro = False
                #elif player 1 move away, move to player 
        #may first need to check health, needs way to stay permanently dead/decay/etc
        if self.health<=0:
            self.dead = True
            self.currentRoom[0].objects.append(self)
        if self.dead == False:
            if player.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:#can this not be done relatively? maybe scan currentRoom.whosThere, if aPlayer etc etc...
                if self.greeted == False:
                    self.greeted = True#initial greetings/warnings here?
                    self.aggro = True
            elif player.currentRoom[0].gridLoc != self.currentRoom[0].gridLoc:
                self.greeted = False
                #self.aggro = False #? Aggro might not even be necessary, unless monster NPC can chase player or something
            if self.greeted == True:
                if world.timePassed >= self.lastTime+3:
                    self.lastTime = world.timePassed
                    game.threadQueue.append(self.attack())

#player
class Player(playerCraft):
    def __init__(self, gameReference):
        self.game=gameReference
        self.currentRoom = []
        self.inventory = []#objects, food, resources etc go here
        self.health = 100
        self.energy = 100
        self.craftableItems = []
        self.lastCommand = ''
        self.trading = False
        self.npcEngaged = []
        #stats
        self.stats = {"strength":5,"defense":5}#dictionary of stats
        #self.strength = 5
        self.hand = []#for equipping
        self.torso = []
        self.equippedItems = [[self.hand, "Hand"],[self.torso, "Torso"]]
        self.dead = False
        self.recalcStats = False
        self.lastTime = world.timePassed
        self.doingQuest = False
        self.previousRoom = []
        self.catGrudge = 0
        self.informedDead = False

    def update(self):#check health, equipped stuff to change stats, etc
        if self.health <= 0 or self.catGrudge>=2:
            self.dead=True
            if self.informedDead == False:
                self.catGrudge = 0
                self.informedDead = True
                game.displayText+="You have perished...\nFind a graveyard or a necromancer\n"
                self.dead = True
        if self.dead == False:
            #do stuff you can do when not dead
            if self.energy<100 and world.timePassed>=self.lastTime+10:
                self.energy+=1
            try:
                if self.npcEngaged[0].currentRoom[0].gridLoc == self.previousRoom[0].gridLoc:
                    self.npcEngaged = []
            except:
                pass
            
        
    def updateStats(self, toUpdate, equipUnequip):
        #toUpdate is the item object, equipUnequip
        if equipUnequip == True:
            #equip so add stat
            #have to change weapon/item stats to dicts, change attack/getattacked fxns to look up data in dicts...
            for item in self.stats:
                self.stats[item]+=toUpdate.stats[item]
        elif equipUnequip == False:
            #unequip equip so minus stat
            for item in self.stats:
                self.stats[item]-=toUpdate.stats[item]
        print(player.stats)

    def equip(self, toEquip):#would make sense to be able to "drop" something in your hand, but for simplicity's sake, you must unequip(item)
        invCount = 0
        hasToEquip = False
        for item in self.inventory:
            if item.name == toEquip:
                hasToEquip = True
                break
            invCount+=1#invCount position of item in inv
        equipWhereCount = 0
        if hasToEquip == True:
            for equippedItem in self.equippedItems:
                if equippedItem[1]==self.inventory[invCount].equipTo:
                    break
                equipWhereCount+=1#equipWhereCount is position in equipped items
        availableToEquip = False
        if len(self.equippedItems[equipWhereCount][0]) == 0:
            availableToEquip = True
        #print("availableToEquip " + str(availableToEquip))
        if availableToEquip == True:
            #equip it
            #self.recalcStats = True
            #print("this threadQueue is messed up")
            #print(invCount)
            updateItem = self.inventory[invCount]
            #game.threadQueue.append(self.updateStats(updateItem, True))
            self.equippedItems[equipWhereCount][0].append(self.inventory[invCount])
            del self.inventory[invCount]
            game.displayText+="You equip the " + toEquip + "...\n\n"
            game.threadQueue.append(self.updateStats(updateItem, True))
        else:
            game.displayText+="You can't do that...\n\n"
        #print("won't get here")

    def unequip(self, item):
        whereEquippedCount = 0
        canUnequip = False
        for equippedItem in self.equippedItems:
            if len(equippedItem[0])!=0:
                if equippedItem[0][0].name==item:
                    canUnequip = True
                    break
            whereEquippedCount+=1
        if canUnequip == True:
            updateItem = self.equippedItems[whereEquippedCount][0][0]
            #game.threadQueue.append(self.updateStats(updateItem, False))
            game.displayText+="You unequip the " + item + "...\n\n"
            self.inventory.append(self.equippedItems[whereEquippedCount][0][0])
            del self.equippedItems[whereEquippedCount][0][0]
            game.threadQueue.append(self.updateStats(updateItem, False))
        else:
            game.displayText+="You can't do that..."


    def commands(self):
        game.displayText+="status, chkInv, look, scout, examine, take, put, gather, cook, drop, eat, move, burn, smelt, smith, craft\n\n"

    def status(self):
        game.displayText+="You take a moment to check yourself...\n\n"
        game.displayText+="Health: " + str(self.health) + "\n\n"
        game.displayText+="Energy: " + str(self.energy) + "\n\n"
        game.displayText+="Position: " + str(self.currentRoom[0].gridLoc) + "\n\n"
        game.displayText+="Time: " + str(int(world.timeOfDay/10)) + "\n\n"

    def myStats(self):
        game.displayText+=str(self.stats)

    def attack(self, target):
        #player needs a lastTime world.timePassed check
        canAttack=False
        hit = random.randrange(0, self.stats["strength"])
        for monsters in world.NPCs:
            if monsters.name == target and monsters.currentRoom[0].gridLoc==self.currentRoom[0].gridLoc:
                if self.energy>=10:
                    self.energy-=10
                    game.displayText+="You attack the " + target + " for " + str(hit) + "damage!\n\n"
                    game.displayText+="The " + target + " has " + str(monsters.health) + " health left...\n\n"
                    canAttack = True
                    game.threadQueue.append(monsters.getAttacked(hit))
                else:
                    game.displayText+="You must catch your breath first...\n\n"
                break
                
        if canAttack==False:
            game.displayText+="You attack the air like a fool...\n\n"

    def getAttacked(self, hit):
        defHit = hit-random.randrange(0,self.stats["defense"])
        if defHit<=0:
            self.energy -= 1
            game.displayText+="You dodge a blow!\n\n"
        elif defHit>0:
            self.energy -= 10
            self.health-=defHit
            game.displayText+="You were hit for " + str(defHit) + " damage!\n\n"

    def trade(self, npcToEngage):#maybe change name to engage for general use, npcs engage fxns are different
        for npcs in world.NPCs:
            if npcs.name == npcToEngage and npcs.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc and len(npcs.inventory)!=0:
                self.npcEngaged.append(npcs)
                npcs.trading=True
                self.trading=True
        if self.trading==False:
            game.displayText="You fail to engage " + npcToEngage + "\n\n"

    def talk(self, npcToTalk):
        for npcs in world.NPCs:
            if npcs.name == npcToTalk and npcs.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:
                self.npcEngaged.append(npcs)
                npcs.talking=True
                break
        if self.npcEngaged[0].talking==True and self.npcEngaged[0].npcQuest[0]==True:
            #npc has an uncompleted quest
            pass
        

    def buy(self, itemInquiry):
        if self.trading==True:
            for item in self.npcEngaged[0].inventory:
                if item.name == itemInquiry:
                    #at this point need general fxn to add/remove items
                    #player inv.append item
                    if self.coinPurse.spendCoin(item.price) == True:
                        self.inventory.append(item)
                        self.trading=False
                        game.threadQueue.append(self.npcEngaged[0].sell(itemInquiry))
                    else:
                        print("not enough coins")
                    break
        self.npcEngaged = []

    def inv(self):
        game.displayText+="You take a look in  your backpack...\n\n"
        for item in self.inventory:
            game.displayText+=item.name + ","
        game.displayText+="\n\n"
        game.displayText+="You glance in your coinpurse...\n\n"
        game.displayText+="Looks to be about " + str(len(self.coinPurse.inventory)) + " coins...\n\n"
        wearing = ''
        for item in self.equippedItems:
            try:
                wearing+=item[0][1] + ": " + item[0][0].name + "\n"
            except:
                pass
        game.displayText+="You are wearing: \n" + wearing
        
    def look(self):
        game.displayText+="You see: " + self.currentRoom[0].description + "\n\n"
        world.worldStatus()

    def who(self):
        game.displayText+="You can the area for living things and see:...\n\n"
        for npcs in world.NPCs:
            if npcs.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:
                game.displayText+=npcs.name
        game.displayText+="\n\n"

    def scout(self):#scout should have to take time/world.run()
        game.displayText+="Potential resources and items: "
        for item in self.currentRoom[0].objects:
            game.displayText+=item.name + ", "
        game.displayText+="\n\n"

    def examine(self, target):#examines /everything/ with target name, needs refining
        for item in self.inventory:
            if item.name == target:
                game.displayText+=item.description + "\n\n"
                try:
                    for subItem in item.inventory:# item x number for multiple items?
                        game.displayText+=subItem.name
                except:
                    pass
        for item in self.currentRoom[0].objects:
            if item.name == target:
                game.displayText+=item.description + "\n\n"
                game.displayText+="It might contain: \n\n"
                for thing in item.resources:
                    game.displayText+=thing.name + ", "
                game.displayText+="\n\n"

        for npcs in world.NPCs:
            if npcs.name == target and npcs.currentRoom[0].gridLoc == self.currentRoom[0].gridLoc:
                game.displayText+=npcs.description
              
    def take(self, itemName):
        #for an object that doesn't require a tool to take
        count = 0
        taken = False
        for item in self.currentRoom[0].objects:
            if itemName == item.name and item.canBeTaken == True:
                game.displayText+="You take the " + item.name + "\n\n"
                if itemName=="Coin":#make this to where if something goes in another container or stack its relative etc
                    self.coinPurse.inventory.append(item)
                else:
                    self.inventory.append(item)
                taken = True
                break
            count+=1
        if not taken:
            game.displayText+="Not sure you can take that...\n\n"
        else:
            del self.currentRoom[0].objects[count]

    def put(self, Thing, target):
        objectCount = 0
        for item in self.currentRoom[0].objects:
            if item.name == target:
                break
            objectCount+=1
        tempList = copy.deepcopy(self.currentRoom[0].objects[objectCount].resources)
        thingsCount = 0
        itemExists = False
        for things in self.inventory:
            if things.name == Thing:
                itemExists = True
                break
            thingsCount+=1
        if itemExists == True:
            tempList.append(self.inventory[thingsCount])
            self.currentRoom[0].objects[objectCount].resources = []
            for item in tempList:
                self.currentRoom[0].objects[objectCount].resources.append(item)
            del self.inventory[thingsCount]
        else:
            game.displayText+="You can't do that...\n\n"
            
    def gather(self, Resource, target):#seems to be working
        objectCount = 0
        resourceCount = 0
        tempRsrcList = []
        foundResource = False
        needTool = False
        didNotGet = False
        
        for item in self.currentRoom[0].objects:
            if item.name == target:
                for resources in item.resources:
                    if resources.name == Resource:
                        if len(resources.toolTypeNeeded)==0:
                            foundResource = True
                            tempRsrcList = copy.deepcopy(item.resources)#have to copy.deepcopy because list = anotherList only makes reference to anotherList
                                                                        #so any changes to list affect anotherList
                            break#break if found resource
                        else:
                            toolList = []
                            for potentialTool in self.inventory:
                                toolList.append(potentialTool.name)
                            if resources.toolTypeNeeded[0] in toolList:
                                foundResource = True
                                needTool = False
                                tempRsrcList = copy.deepcopy(item.resources)
                            else:
                                needTool = True
                    if foundResource == True:
                        break#break out of inner loop-this one might not be necessary?
                    else:
                        resourceCount+=1
            if foundResource == True:
                break#break from outer loop
            else:
                objectCount+=1
                resourceCount=0
        if foundResource == True and needTool == False:
            #see if this is actually where it gets put in the inv idk it needs displayText
            game.displayText+="You gather " + Resource + " from the " + target + "\n\n"
            if Resource == "Coin":#again relativity, for other items that get stacked/containered
                player.coinPurse.inventory.append(tempRsrcList[resourceCount])
            else:
                self.inventory.append(tempRsrcList[resourceCount])
            del tempRsrcList[resourceCount]
            self.currentRoom[0].objects[objectCount].resources = copy.deepcopy(tempRsrcList)#not sure if this deepcopy necessary
            didNotGet=True
        if didNotGet==False:
            game.displayText+="You fail to gather the " + Resource + " from the " + target + "\n\n"

    
    def cook(self, itemName):
        try:
            count = 0
            exists = True
            for item in self.inventory:
                if itemName == item.name:
                    break
                count+=1
            pitInRoom = False
            for item in self.currentRoom[0].objects:
                if item.name == "Firepit":
                    pitInRoom = True
            if pitInRoom == True:
                game.displayText+="You cook the " + itemName + "\n\n"
                self.inventory[count].cook()
            else:
                game.displayText+="Can't seem to do that..." + "\n\n"
        except:
            game.displayText+="I don't think you can cook that...\n\n"
            
    def drop(self, itemName):
        count = 0
        dropped = False
        for item in self.inventory:
            if itemName == item.name:
                game.displayText+="You drop the " + item.name + "\n\n"
                self.currentRoom[0].objects.append(item)
                dropped = True
                break
            count += 1
        if dropped:
            del self.inventory[count]

    def eat(self, foodName):
        count = 0
        ateIt = False
        for item in self.inventory:
            if item.name == foodName:
                if item.edible[0]:
                    game.displayText+="You attempt to eat the " + item.name + "\n\n"
                    if player.health > 0 and player.health < 100:
                        ateIt = True
                        player.health += item.edible[1]
                        del player.inventory[count]
                        break
                    else:
                        game.displayText+="You decide not to since your health is full...\n\n"
            count += 1
        #if not ateIt:
        #    print("Can't eat that...")#bit redundant, maybe if other conditions are met
                    

    def move(self, moveTo):
        y=0
        x=0
        if moveTo in self.currentRoom[0].exits:
            #exit exists
            if moveTo=='n':
                y = 1
            elif moveTo=='s':
                y = -1
            elif moveTo=='e':
                x = 1
            elif moveTo=='w':
                x = -1
            moveCoord = [self.currentRoom[0].gridLoc[0]+x,self.currentRoom[0].gridLoc[1]+y]
            for item in world.Places:
                if item.gridLoc == moveCoord:
                    self.previousRoom.append(self.currentRoom[0])
                    if len(self.previousRoom)>1:
                        del self.previousRoom[0]
                    self.currentRoom.append(item)
                    del self.currentRoom[0]
                    break
        else:
            game.displayText+="You can't go that way!\n\n"
        game.displayText+=self.currentRoom[0].description + "\n\n"

    def revive(self):
        foundSpire=False
        if self.dead==True:
            for item in self.currentRoom[0].objects:
                if item.name == "Spire":
                    foundSpire=True
                    self.dead=False
                    self.health=100
                    game.displayText+="You touch the spire with your ghostly fingers and are revived!\n"
                    break
            if foundSpire==False:
                game.displayText+="There is no spire here...\n"
        else:
            game.displayText+="You are alive! You can't revive any farther!\n"


class Tree:#the example object!
    def __init__(self):
        self.name = "Tree"
        self.description = "A common tree"
        self.resources = []#probably logs(that are class objects), maybe randomize amount at init, objects w/out resources still get resources slot
        self.canBeTaken = False #resources/objects can be inventoried, trees and shit can't. if you take it, del from place and add to player.inv?
        self.toolTypeNeeded = []#objects get toolTypeNeeded to get resources from it, craft it, split it, etc
        self.edible = [False, 0] #[not edible, 0 hp], I suppose like a poison apple could be negative hp! edible=drinkable
        for i in range(0, random.randrange(1,4)):
            self.resources.append(Log())
        for i in range(0, random.randrange(1,3)):
            self.resources.append(Apple())
        for i in range(0, random.randrange(1,2)):
            self.resources.append(Sap())
        for i in range(0, random.randrange(1,3)):
            self.resources.append(Vines())

class Spire:
    def __init__(self):
        self.name = "Spire"
        self.description = "A stone spire. If you are dead it will revive you...\n"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []

class Log:
    def __init__(self):
        self.name = "Log"
        self.description = "A log cut from a common tree"
        self.resources = []
        self.canBeTaken = True#only if axe in inventory
        self.toolTypeNeeded = ["Axe"]#axe to make it firewood, knife to whittle it etc...need to make these objects
        self.price = 1

class Apple:
    def __init__(self):
        self.name = "Apple"
        self.description = "A shiny, red apple."
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 10]

class Pumpkin:
    def __init__(self):
        self.name = "Pumpkin"
        self.description = "A big, orange pumpkin. Good for making jack-o-lanterns and pie...\n\n"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 20]

class Wheat:
    def __init__(self):
        self.name = "Wheat"
        self.description = "Freshly reaped wheat ready for grinding into flour...\n\n"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Scythe"]
        self.edible = [True, 1]

class Corpse:
    def __init__(self):
        self.name = "Corpse"
        self.description = "A stinking corpse, bloated and covered in flies...\n\n"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []

class Rocks:
    def __init__(self):
        self.name = "Rocks"
        self.description = "A rocky outcrop, possibly containing resources..."
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        for i in range(0, random.randrange(1,4)):
            self.resources.append(Stone())
        for i in range(0, random.randrange(1,3)):
            self.resources.append(Iron())
        vine = random.randrange(0,1)
        if vine == 1:
            for i in range(0,random.randrange(1,2)):
                self.resources.append(Vines())

class Stone:
    def __init__(self):
        self.name = "Stone"
        self.description = "A uniform chunk of stone"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Pickaxe"]
        self.price = 1

class Sap:
    def __init__(self):
        self.name = "Sap"
        self.description = "A sticky wad of sap from a gash in a tree"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Axe"]
        self.edible = [True, 1]
        self.price = 1

class Pond:
    def __init__(self):
        self.name = "Pond"
        self.description = "A small fishing pond"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        for i in range(0,12):
            self.resources.append(Water())
        for i in range(0,random.randrange(3,6)):
            self.resources.append(Fish())

class WheatPatch:
    def __init__(self):
        self.name = "WheatPatch"
        self.description = "A patch of golden wheat"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        for i in range(0,12):
            self.resources.append(Wheat())

class PumpkinPatch:
    def __init__(self):
        self.name = "PumpkinPatch"
        self.description = "A patch of lumpy pumpkins"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        for i in range(0,12):
            self.resources.append(Pumpkin())

class Water:
    def __init__(self):
        self.name = "Water"
        self.description = "Some fresh water"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = ["Bucket"]
        self.edible = [True, 2]

class Fish:
    def __init__(self):
        self.name = "Fish"
        self.description = "A freshly caught fish"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Rod"]
        self.cooked = False
        edible = [True, 20]
        self.price = 3

    def cook(self):
        self.cooked = True
        self.description = "A delicious fish filet"

class Iron:
    def __init__(self):
        self.name = "Iron"
        self.description = "Some grubby ore that needs refining..."
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Pickaxe"]
        self.price = 2

class Vines:
    def __init__(self):
        self.name = "Vines"
        self.description = "Some thin vines, useful for crafting..."
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Knife"]
        self.price = 1

class Cart:
    def __init__(self):
        self.name = "Cart"
        self.description = "A wooden cart used for carrying goods"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []

class goldCoin:
    def __init__(self):
        self.name = "Coin"
        self.description = "A shiny gold coin"
        self.canBeTaken = True
        self.toolTypeNeeded = []

class CoinPurse:
    def __init__(self):
        self.name = "CoinPurse"
        self.description = "A leather coin pouch with a cinch"
        self.inventory = []

    def spendCoin(self, amountSpent):
        if len(self.inventory)>=amountSpent:
            for i in range(0,amountSpent):
                del self.inventory[0]
            game.displayText+="You spend " + str(amountSpent) + " coins\n\n"
            return True
        else:
            game.displayText+="You don't have enough coins!\n\n"
            return False

class Hide:
    def __init__(self):
        self.name = "Hide"
        self.description = "Some hide made from the skin of a beast, useful for crafting"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Knife"]
        self.price = 1

class RatTail:
    def __init__(self):
        self.name = "Rattail"
        self.description = "A leathery tail cut from a rat..."
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Knife"]
        self.price = 1

class Grave:
    def __init__(self):
        self.name = "Grave"
        self.description = "An old grave with a weather-worn headstone...\n"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        self.resources.append(Bones())
        self.resources.append(Corpse())

class Bones:
    def __init__(self):
        self.name = "Bones"
        self.description = "A pile of bones picked clean by bugs and bacteria...\n"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = ["Spade"]
        self.price = 5
        
        
###
#craftable Items
class Spade:
    def __init__(self):
        self.name = "Spade"
        self.description = "A dirty old spade"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log","IronIngot","Sap","Charcoal","Water"]
        self.craftTool = ["Hammer"]
        self.price = 10
        self.equipTo = "Hand"
        self.stats = {"strength":3,"defense":1}


class Knife:
    def __init__(self):
        self.name = "Knife"
        self.description = "A sharp stone knife"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log", "Stone", "Sap"]
        self.craftTool = []
        self.price = 1
        self.equipTo = "Hand"
        self.stats = {"strength":1,"defense":0}

class Axe:
    def __init__(self):
        self.name = "Axe"
        self.description = "A sharp woodcutting axe"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log", "Stone", "Sap"]
        self.craftTool = ["Knife"]
        self.price = 5
        self.equipTo = "Hand"
        self.stats = {"strength":2,"defense":0}

class Pickaxe:
    def __init__(self):
        self.name = "Pickaxe"
        self.description = "A pickaxe for mining stone and ore"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log", "Stone", "Sap"]
        self.craftTool = ["Axe"]
        self.price = 5
        self.equipTo = "Hand"
        self.stats = {"strength":3,"defense":0}

class Spear:
    def __init__(self):
        self.name = "Spear"
        self.description = "A pointy stone spear"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log", "Stone", "Sap"]
        self.craftTool = ["Axe"]
        self.price = 2
        self.equipTo = "Hand"
        self.stats = {"strength":4,"defense":0}

class Hammer:
    def __init__(self):
        self.name = "Hammer"
        self.description = "A stone hammer for building things"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log", "Stone", "Sap"]
        self.craftTool = ["Axe"]
        self.price = 2
        self.equipTo = "Hand"
        self.stats = {"strength":2,"defense":0}

class FirePit:
    def __init__(self):
        self.name = "Firepit"
        self.description = "A simple stone firepit. Once you place it, it's there forever..."
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        self.waste = ["Stone", "Stone", "Stone", "Log"]
        self.craftTool = []
        self.price = 3

class Bucket:
    def __init__(self):
        self.name = "Bucket"
        self.description = "A crude wooden bucket, good for carrying water"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Log","Log","Sap", "Sap"]
        self.craftTool = ["Axe"]
        self.price = 3
        
class Rod:
    def __init__(self):
        self.name = "Rod"
        self.description = "A simple fishing rod"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Log","Log","String"]
        self.craftTool = ["Knife"]
        self.price = 5

class Furnace:
    def __init__(self):
        self.name = "Furnace"
        self.description = "A crude stone furnace"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        self.waste = ["Charcoal", "Charcoal", "Stone", "Stone", "Stone", "Stone", "Bucket", "Hammer", "Water"]
        self.craftTool = ["Hammer"]
        self.price = 7

class Charcoal:
    def __init__(self):
        self.name = "Charcoal"
        self.description = "Charred wood -- useful as fuel"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Log"]
        self.craftTool = []
        self.groundTool = ["Firepit"]
        self.price = 1

class IronIngot:
    def __init__(self):
        self.name = "IronIngot"
        self.descriptioin = "An iron ingot, ready for smithing"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Iron","Iron","Iron","Charcoal"]
        self.craftTool = []
        self.groundTool = ["Furnace"]
        self.price = 4

class Scythe:
    def __init__(self):
        self.name = "Scythe"
        self.description = "A peculiar blade made for harvesting wheat"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Log", "Log", "IronIngot", "IronIngot", "Sap", "String", "Water"]
        self.craftTool = ["Hammer"]
        self.groundTool = ["Anvil"]
        self.price = 10
        self.equipTo = "Hand"
        self.stats = {"strength":7,"defense":1}

class IronSword:
    def __init__(self):
        self.name = "IronSword"
        self.description = "A sword smithed from smelted iron"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["IronIngot","IronIngot","Log","Sap","Water"]
        self.craftTool = ["Hammer"]
        self.groundTool = ["Anvil"]
        self.price = 10
        self.equipTo = "Hand"
        self.stats = {"strength":5,"defense":0}

class Whip:#add if 5 or more rats in a room they form a rat king!
    def __init__(self):
        self.name = "Whip"
        self.description = "A nasty whip made from rat tails...\nEffective against Rat Kings and werewolves..."
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Rattail","Rattail","Rattail","Rattail","Rattail","Sap","Log","Hide"]
        self.craftTool = ["Knife"]
        self.groundTool = []
        self.price = 10
        self.equipTo = "Hand"
        self.stats = {"strength":12,"defense":-1}

class Anvil:
    def __init__(self):
        self.name = "Anvil"
        self.description = "A crudely cast anvil"
        self.resources = []
        self.canBeTaken = False
        self.toolTypeNeeded = []
        self.waste = ["IronIngot","IronIngot","Stone","Stone","Bucket","Water"]
        self.craftTool = ["Hammer"]
        self.groundTool = ["Furnace"]
        self.price = 10

class Rope:
    def __init__(self):
        self.name = "Rope"
        self.description = "A length of rope made from vines"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Vines","Vines","Vines"]
        self.craftTool = ["Knife"]
        self.price = 4

class String:
    def __init__(self):
        self.name = "String"
        self.description = "A length of string, strengthened with tree sap"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Vines","Sap"]
        self.craftTool = ["Knife"]
        self.price = 2

class Bow:
    def __init__(self):
        self.name = "Bow"
        self.description = "A simple hunting bow"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Vines","Vines","Log","Log","Sap"]
        self.craftTool = ["Knife"]
        self.price = 5
        self.equipTo = "Hand"

class Arrow:
    def __init__(self):
        self.name = "Arrow"
        self.description = "A crudely fashioned arrow"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Log","String","Sap","Stone"]
        self.craftTool = ["Knife"]
        self.price = 2

class HideVest:
    def __init__(self):
        self.name = "Hidevest"
        self.description = "A crudely constructed hide vest that provides some protection"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.waste = ["Hide","String"]
        self.craftTool = ["Knife"]
        self.price = 15
        self.equipTo = "Torso"
        self.stats = {"strength":0,"defense":3}
        
class Flour:
    def __init__(self):
        self.name = "Flour"
        self.description = "Flour made from ground wheat"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 1]
        self.waste = ["Wheat"]
        self.craftTool = ["Stone"]
        self.price = 3

class PieCrust:
    def __init__(self):
        self.name = "Piecrust"
        self.description = "A simple pie crust. Add filling and bake it!"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 1]
        self.waste = ["Flour","Water"]
        self.craftTool = ["Bowl"]
        self.price = 5

class Bowl:
    def __init__(self):
        self.name = "Bowl"
        self.description = "A simple wooden bowl carved from a log"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [False, 0]
        self.waste = ["Log"]
        self.craftTool = ["Knife"]
        self.price = 3

class AppleFilling:
    def __init__(self):
        self.name = "AppleFilling"
        self.description = "Delicious apple pie filling"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 1]
        self.waste = ["Apple","Apple"]
        self.craftTool = ["Bowl"]
        self.price = 2

class ApplePie:
    def __init__(self):
        self.name = "ApplePie"
        self.description = "An uncooked apple pie"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 1]
        self.cooked = False
        self.waste = ["Piecrust","AppleFilling"]
        self.craftTool = ["Bowl"]
        self.price = 4

    def cook(self):
        self.description = "A delicious apple pie"
        self.cooked = True
        self.edible = [True, 20]

class PumpkinFilling:
    def __init__(self):
        self.name = "PumpkinFilling"
        self.description = "Delicious apple pie filling"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 1]
        self.waste = ["Pumpkin","Pumpkin"]
        self.craftTool = ["Bowl"]
        self.price = 2

class PumpkinPie:
    def __init__(self):
        self.name = "PumpkinPie"
        self.description = "An uncooked pumpkin pie"
        self.resources = []
        self.canBeTaken = True
        self.toolTypeNeeded = []
        self.edible = [True, 1]
        self.cooked = False
        self.waste = ["Piecrust","PumpkinFilling"]
        self.craftTool = ["Bowl"]
        self.price = 4

    def cook(self):
        self.description = "A delicious pumpkin pie"
        self.cooked = True
        self.edible = [True, 25]



#player = Player()
#player.craftableItems= [Spear(),Hammer(),Axe(),Pickaxe(),Knife(),FirePit(),
#                        Bucket(),Rod(),Furnace(),Charcoal(),IronIngot(),IronSword(),
#                        Anvil(), Rope(), String(), Bow(), Arrow(), HideVest()]

class Game:
    def __init__(self):
        self.window = Tk()
        self.window.title("Hyggeland")
        self.window.configure(bg="black")
        #self.window.attributes('-fullscreen', True) #overrideredirect(1) (below) unnecessary when use this, or so it seems
        #self.window.overrideredirect(1) #could be useful for fullscreen, takes away window borders/min/max/exit buttons, player can toggle
        v = Scrollbar(self.window, orient = 'vertical')
        v.pack(side=RIGHT, fill='y')
        self.display = Text(self.window, yscrollcommand=v.set)
        v.config(command=self.display.yview)
        self.display.pack()
        self.usrEntry = Entry(self.window)
        self.usrEntry.pack()
        self.queueButton = Button(self.window, command = self.textReady, text="Enter")
        self.queueButton.pack()
        self.ready = False
        self.window.bind("<Return>",lambda event: self.readyText())#change to readyText if it doesn't work, uncomment readyText
        self.window.bind("<Escape>",lambda event: self.fullscreen())
        self.isFullscreen = False
        self.threadQueue = []
        self.displayText = ''

    def fullscreen(self):#works!
        if self.isFullscreen == False:
            self.window.attributes('-fullscreen', True)
            self.isFullscreen = True
        elif self.isFullscreen == True:
            self.window.attributes('-fullscreen', False)
            self.isFullscreen = False

    def readyText(self):
        self.threadQueue.append(self.textReady())
    
    def textReady(self):
        self.ready = True

    def interpreter(self):#if self.ready == True, run this (or put it in queue to be run?)
        try:
            spltInput = self.usrEntry.get()#.split()#now a list of individual words
            print(spltInput)
            if spltInput == "last":
                spltInput = player.lastCommand.split()
            else:
                player.lastCommand = spltInput
                spltInput = spltInput.split()
            func = getattr(player, spltInput[0])
            args=[]
            for i in spltInput[1:]:
                args.append(i)
            
            self.threadQueue.append(func(*args))
        except:
            #need to display error msg here because input was invalid
            pass

    def runGame(self):#some fxns are passed by default, other determined by usrInput or objects in world (world objects get sent to, usrInput is checked by)
        #check usrInput and game.window.update() always passed to threadQueue
        while True:#might have to put this loop back if self.runGame() at end doesn't work
                #default fxns passed to threadQueue
            self.threadQueue.append(world.run())
            self.threadQueue.append(self.gameUpdate())
            #for npcs in world - npcs.update() (things theyre waiting to do (oldTime vs newTime) and things they always check for)
            self.threadQueue.append(player.update())
            for npcs in world.NPCs:#maybe turn this whole block into its own fxn, runGame getting long...
                if npcs.dead == False:
                    self.threadQueue.append(npcs.update())
                #elif npcs.dead == True:
                #    npcs.currentRoom[0].objects.append(copy.deepcopy(npcs))#then delete all dead NPCs from world.NPCs
            numDeadNPCs = 0
            for npcs in world.NPCs:
                if npcs.dead == True:
                    numDeadNPCs+=1
            while numDeadNPCs>0:
                npcCount = 0
                for npcs in world.NPCs:
                    if npcs.dead == True:
                        del world.NPCs[npcCount]
                        numDeadNPCs-=1
                        npcCount=0#might not need this?
                        break
                    npcCount+=1
                npcCount=0
            
            if player.dead==False:   
                if self.usrEntry.get()!='' and self.ready!=False:#ignore and run commands in threadQueue
                    #game.threadQueue.append(player.command(gameWin.usrEntry.get()))
                    self.threadQueue.append(self.interpreter())#might have to add this to queue to work?
                    self.usrEntry.delete(0,'end')
                    self.ready = False
            elif player.dead==True:
                deadCommands=["move n","move s","move e","move w","revive"]
                if self.usrEntry.get() in deadCommands and self.ready!=False:
                    self.threadQueue.append(self.interpreter())
                    self.usrEntry.delete(0,'end')
                    self.ready = False
            if self.ready==True:
                self.ready = False
            for toRun in self.threadQueue:
                t = Thread(target = toRun)
                #t.setDaemon(True) #prob not necessary
                t.start()
                t.join()
            self.threadQueue= []
        #self.runGame()#this causes a recursion error, but is there a way to override that?(just for future reference
            
    def gameUpdate(self):
        colorText = self.displayText
        if colorText != '':
            colorText+="\n\n"
        self.display.tag_add("start", "1.0", "end")#this >>         (because you have to keep track of positions in displayText to highlight text/change color etc)
        self.display.tag_config("start", background = "black", foreground = "green")#<< and this need to be sent args, like skeleton txt should be red?
        self.display.insert(END, colorText)
        if self.displayText != '':
            self.display.see("end")
        self.displayText=''
        self.window.update()
        self.usrEntry.focus_set()


#########EVERYTHING AFTER THIS POINT is setting up the game, need to rework how this is done for readability and creating the world
#put craftableItems in player.craftableItems for reference when building
game = Game()
world = World(game)

player = Player(game)
player.craftableItems = [Spear(),Hammer(),Axe(),Pickaxe(),Knife(),FirePit(),
                         Bucket(),Rod(),Furnace(),Charcoal(),IronIngot(),IronSword(),
                         Anvil(), Rope(), String(), Bow(), Arrow(), HideVest(),
                         Flour(), PieCrust(), Bowl(), AppleFilling(), ApplePie(),
                         Scythe(), PumpkinFilling(), PumpkinPie()]



#rooms -- prob turn this whole thing into an import
#room1
room1 = Place()
room1.gridLoc = [0,0]
room1.exits = ['n']
room1.description = "A grassy clearing in the woods."
room1.objects.append(Spire())
#room2
room2 = Place()
room2.gridLoc = [0,1]
room2.exits = ['s', 'e']
room2.description = "A dusty trail."
for i in range(0,3):#put some trees in the room
    room2.objects.append(Tree())#prob have some rooms with permanent/set amt of logs
#room3
room3 = Place()
room3.gridLoc = [1,1]
room3.exits = ['w', 'e']
room3.description = "The trail continues, getting wider. It looks like someone may have camped here recently."
room3.objects.append(Axe())
#room4
room4 = Place()
room4.gridLoc = [2,1]
room4.exits = ['n', 'e', 'w']
room4.description = "The trail continues. A corpse is pinned to the ground with the blade it died by."
room4.objects.append(Corpse())
room4.objects[0].resources.append(Apple())
#room5
room5 = Place()
room5.gridLoc = [3,1]
room5.exits = ['w']
room5.description = "The trail comes to a dead end here, the trees are too thick to pass through..."
room5.objects.append(Apple())
for i in range(0,3):
    room5.objects.append(Rocks())
#room6
room6 = Place()
room6.gridLoc = [2,2]
room6.exits = ['n','s']
room6.description = "The trail ends, leading out of the forest into a big, grassy field. It looks like there is a village far to the North..."
room6.objects.append(Tree())
room6.objects.append(Pickaxe())
#room7
room7 = Place()
room7.gridLoc = [2,3]
room7.exits = ['n','s']
room7.description = "Well out of the forest, a small pond is situated between a tree and a pile of rubble on a small hill."
room7.objects.append(Tree())
room7.objects.append(Pond())
#room8
room8 = Place()
room8.gridLoc = [2,4]
room8.exits = ['n','s','e','w']
room8.description = "The grassy field is dotted with small trees and rocks."
for i in range(0,4):
    room8.objects.append(Tree())
for i in range(0,4):
    room8.objects.append(Rocks())
#room9
room9 = Place()
room9.gridLoc = [1,4]
room9.exits = ['n','e']
room9.description = "There is a small hill here and a few rocks."
for i in range(0,2):
    room9.objects.append(Rocks())
#room10
room10 = Place()
room10.gridLoc = [3,4]
room10.exits = ['w']
room10.description = "A rather desolate section of the field. A small tree looms in the middle"
room10.objects.append(Tree())
room10.objects[0].resources.append(Knife())
#room11
room11 = Place()
room11.gridLoc = [2,5]
room11.exits = ['n','s','e','w']
room11.description = "A worn dirt path starts here. Refuse litters the area, folk from the village to the north must frequent this area..."
room11.objects.append(Tree())
room11.objects.append(Rocks())
room11.objects[1].resources.append(Rope())
room11.objects.append(Spear())
for i in range(0,6):
    room11.objects.append(Stone())
room11.objects.append(Apple())
room11.objects.append(Log())
room11.objects.append(Cart())
putCart = 0
for item in room11.objects:
    if item.name == "Cart":
        break
    putCart+=1
for i in range(0,10):
    room11.objects[putCart].resources.append(Apple())
room11.objects[putCart].resources.append(Knife())
#room12
room12 = Place()
room12.gridLoc = [1,5]
room12.exits = ['s','e']
room12.description = "A large, sprawling hill. From the top you get a clear view of the village to the North..."
room12.objects.append(Tree())
room12.objects.append(Rocks())
#room13
room13 = Place()
room13. gridLoc = [3,5]
room13.exits = ['n','s','w']
room13.description = "A large, empty portion of the field. A single rock sits in the middle."
room13.objects.append(Rocks())
#room14
room14 = Place()
room14.gridLoc = [2,6]
room14.exits = ['s','e']
room14.description = "The path cuts through a small wood just to the south of the village.\n\nYou see the wooden gate to the village at the end of the path...\n\n"
for i in range(0,8):
    room14.objects.append(Tree())
for i in range(0,3):
    room14.objects.append(Rocks())
#room15
room15 = Place()
room15.gridLoc = [3,6]
room15.exits = ['s','e','w']
room15.description = "A small garden is here between the village wall and the woods.\n\nA run-down shack leans against the wall\n\n"
room15.objects.append(WheatPatch())
room15.objects.append(PumpkinPatch())
#room16
room16 = Place()
room16.gridLoc = [4,6]
room16.exits = ['w']
room16.description = "A small graveyard dotted with lopsided headstones...\nIn the middle is a small spire -- revive here when you die!\n"
room16.objects.append(Tree())
for i in range(0,6):
    room16.objects.append(Grave())




#put player in starting room and put rooms in world.Places
player.currentRoom.append(room1)#starting position
#cat1.currentRoom.append(room1)
player.inventory.append(Knife())
#put rooms in world.Places
roomList = [room1, room2, room3, room4, room5, room6, room7,
            room8, room9, room10, room11, room12, room13, room14,
            room15, room16]

for room in roomList:
    world.Places.append(room)

player.coinPurse=CoinPurse()
#TESTING STUFFv##########################
player.coinPurse.inventory.append(goldCoin())

for i in range(0,5):
    player.inventory.append(Apple())

player.inventory.append(HideVest())
player.inventory.append(Whip())
player.inventory.append(Spade())

world.NPCs.append(Cat())#need better way to put npcs in rooms, npc generators, etc
world.NPCs.append(Merchant())
world.NPCs.append(Skeleton())
world.NPCs.append(Troll())
world.NPCs.append(Deer())
world.NPCs.append(Werewolf())
world.NPCs[5].currentRoom.append(room2)
world.NPCs[4].currentRoom.append(room1)
world.NPCs[3].currentRoom.append(room12)
world.NPCs[2].resources.append(Axe())
world.NPCs[0].currentRoom.append(room1)
world.NPCs[1].currentRoom.append(room11)
world.NPCs[2].currentRoom.append(room12)
world.NPCs[1].inventory.append(Log())
world.NPCs[1].inventory.append(Stone())
world.NPCs[1].inventory.append(HideVest())
world.NPCs[1].inventory.append(IronSword())
#for i in range(0,6):
#    world.NPCs.append(Rat())
#for npcs in world.NPCs:
#    if npcs.name == "Rat":
#        npcs.currentRoom.append(room1)
for npcs in world.NPCs:
    print(npcs.name)
    print(npcs.currentRoom)

#test people
Jane = Person("Jane","A traveller in heavily patched clothing...\n\nShe wields a sword but doesn't look aggressive...")#name and descript
Jane.npcTalk = "Fok off, traveller...\n\nI've no more use for you...\n\n"#do this to change default talk, changes to this when quest done
Jane.toFetch=HideVest()#default apples
Jane.numToFetch = 1#default random num
Jane.rewardAmt = 1#default random num
Jane.reward = [Scythe()]#you have to do all this stuff to customize fetch quest#
world.NPCs.append(Jane)#put in world
Jane.currentRoom.append(room8)#currentRoom

John = Person("John","A grubby vagrant. He reeks of cheap spirits...")
John.npcTalk = "*hic* Spare a coin would ya? *hic* I'm down on my *hic* luck...\n\n"
John.toFetch = Apple()
world.NPCs.append(John)
John.currentRoom.append(room15)
#end test people
#TESTING STUFF^############################

game.displayText=mainScreen + "\n"
#start window then run game!
game.window.after(2000,game.runGame)
game.window.mainloop()
