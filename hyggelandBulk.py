import time
import random
import copy

mainScreen = """
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
0000          #  # #   #  ##    ##  #### #     ###  #   # ###               0000
0000          #  #  # #  #     #    #    #    #   # ##  # #  #              0000
0000          ####   #  #  ## #  ## ###  #    ##### # # # #  #              0000
0000          #  #   #   #  #  #  # #    #    #   # #  ## #  #              0000
0000          #  #   #    ##    ##  #### #### #   # #   # ###               0000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000

"""

class World:
    def __init__(self, gameReference):
        self.game = gameReference
        self.timeOfDay = 0
        self.currentSeason = 0
        self.currentWeather = 0
        self.temperature = 50
        self.currentMoon = 0
        self.moonCounter = 0
        self.timePassed = 0
        self.daysPassed = 0
        self.tick = 0
        self.seasonCount = 0
        #
        self.weatherTypes = ["rainy", "clear", "cloudy", "snow"]
        self.Seasons =      ["Spring", "Summer", "Autumn", "Winter"]
        self.moonPhases =   ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon",
                             "Waning Gibbous", "Last Quarter", "Waning Crescent"]

        self.Places = []
        self.NPCs = []
                        
    def weatherChange(self):
        if self.currentSeason != 3:
            self.currentWeather = random.randrange(1, 3)
        else:
            self.currentWeather = random.randrange(0,len(self.weatherTypes)-1)
        if self.currentSeason == 0 or self.currentSeason == 2:
            self.temperature = random.randrange(35, 75)
        elif self.currentSeason == 1:
            self.temperature = random.randrange(75, 110)
        else:
            self.temperature = random.randrange(0, 32)#make temp weighted differently as season progresses
        #adjust temp with weather
        if self.weatherTypes[self.currentWeather] == "rainy" or self.weatherTypes[self.currentWeather] == "snow":
            self.temperature-=random.randrange(0, 15)
        elif self.weatherTypes[self.currentWeather] == "clear":
            self.temperature+=random.randrange(0, 5)
        else:
            self.temperature-=random.randrange(0, 5)
        #adjust temp with time of day
        if self.timeOfDay<=11:
            self.temperature+=random.randrange(0, 5)
        else:
            self.temperature-=random.randrange(0, 5)

    def nextMoonPhase(self):
        if self.currentMoon<=7:
            self.currentMoon+=1
        else:
            self.curretMoon=0
            
    def seasonChange(self):
        if self.currentSeason < 3:
            self.currentSeason += 1
        else:
            self.currentSeason = 0

    def incrementTime(self):
        time.sleep(0.1)
        self.timePassed += 1
        if self.timeOfDay < 239:
            self.timeOfDay += 1
            self.moonCounter+=1
        else:
            self.timeOfDay = 1
            self.daysPassed +=1
            self.seasonCount +=1
            self.game.displayText+="You have survived " + str(self.daysPassed) + " days in Hyggeland...\n"

    def worldStatus(self):
        self.game.displayText+="Time: " + str(int(self.timeOfDay/10)) + "\n"
        if self.timeOfDay < 11:
            self.game.displayText+="Daytime\n"
        else:
            self.game.displayText+="Nighttime\n"
        self.game.displayText+="Season: " + self.Seasons[self.currentSeason] + "\n"
        self.game.displayText+="Weather: " + self.weatherTypes[self.currentWeather] + "\n"
        self.game.displayText+="Temp: " + str(self.temperature) + " degrees" + "\n"
        self.game.displayText+="Moon: " + self.moonPhases[self.currentMoon] + "\n"
        self.game.displayText+="You have survived " + str(self.daysPassed) + " days in Hyggeland...\n"

    def run(self):#this is probably going to be what threading is based on, so it needs like a timestamp or something?
        #incrementTime(), check seasonChange(), check nextMoonPhase(), weatherChange(), tempChange()
        #print("moon counter" + str(self.moonCounter))
        if self.tick < 10:
            time.sleep(0.1)
            self.tick+=1
        else:#wait does it need to sleep here?
            self.game.threadQueue.append(self.incrementTime())
            self.tick = 0
        if self.seasonCount==900:
            self.game.threadQueue.append(self.seasonChange())
            self.seasonCount = 0
        if self.moonCounter>=270:
            self.game.threadQueue.append(self.nextMoonPhase())
            self.moonCounter = 0
        if self.timeOfDay%8==0:
            self.game.threadQueue.append(self.weatherChange())


class playerCraft:
    def __init__(self):
        #pass
        self.game = gameReference
    
    def burn(self, toBurn):#you do this to get charcoal, but you can also just craft it... 
        firepitInRoom = False
        for item in self.currentRoom[0].objects:
            if item.name =="Firepit":
                firepitInRoom = True
                break
        if firepitInRoom == True:
            for item in self.inventory:
                if item.name == toBurn:
                    self.craft("Charcoal", burn=True)
                    break    
        else:
            self.game.displayText+="There is no firepit nearby\n"

    def smelt(self, toSmelt):#at this point smelt and burn, passing burn=True to self.craft, is just making the groundCraft check?
        furnaceInRoom = False
        for item in self.currentRoom[0].objects:
            if item.name == "Furnace":
                furnaceInRoom = True
                break
        if furnaceInRoom == True:
            for item in self.inventory:
                if item.name == toSmelt:
                    self.craft(str(toSmelt + "Ingot"), burn = True)
                    break
        else:
            self.game.displayText+="There is no furnace nearby\n"

    def smith(self, toSmith):
        anvilInRoom = False
        for item in self.currentRoom[0].objects:
            if item.name == "Anvil":
                anvilInRoom = True
                break
        if anvilInRoom == True:
            self.craft(toSmith, burn = True) 

    def craft(self, Creation, burn=False):#working thus far, will likely need to be rewritten due abnormalities deleting used mats from inventory
        burnables = ["Charcoal","IronIngot", "Anvil"]#try except pass thing and give craftables a burnable bool, this works for now
        if Creation in burnables:
            burn=True
        canBuild = False
        hasTool = False
        craftableCount = 0
        for craftable in self.craftableItems:
            if craftable.name == Creation:
                canBuild = True
                break
            craftableCount+=1
        if canBuild == True:
            #see if player has tool in inventory to craft item
            for item in self.inventory:
                try:
                    if item.name == self.craftableItems[craftableCount].craftTool[0]:
                        hasTool = True
                        break
                except:
                    hasTool = True#because nothing in craftTool
        if hasTool == True:
            #see if player has materials in inventory to craft item
            needCount=len(self.craftableItems[craftableCount].waste)
            haveCount=0
            matList = []
            needList = []
            for item in self.craftableItems[craftableCount].waste:
                needList.append(item)
            tempList = copy.deepcopy(self.inventory)
            for mat in self.inventory:
                matList.append(mat.name)
            for item in self.craftableItems[craftableCount].waste:
                if item in matList:
                    haveCount+=1
            groundFound = False
            if haveCount == needCount:
                for item in self.currentRoom[0].objects:
                    try:
                        if item.name ==  self.craftableItems[craftableCount].groundTool[0]:
                            groundFound = True
                            break
                    except:
                        pass
                for item in burnables:
                    if item == Creation:
                        if burn==False and groundFound == False:#specific instance of charcoal, needs to be rewritten
                            burn = True
                            break
                if  burn == True and groundFound == True or burn == False and groundFound == False:
                    self.game.displayText+="You made " + self.craftableItems[craftableCount].name + "\n"
                    self.inventory.append(self.craftableItems[craftableCount])
                    #now del materials from inventory
                    delPosCount = 0#position in tempList
                    foundDel = False
                    while haveCount>0:
                        for item in needList:
                            for thing in self.inventory:
                                if thing.name == item:
                                    foundDel = True
                                    break
                                else:
                                    delPosCount+=1
                            if foundDel == True:
                                del needList[0]
                                del self.inventory[delPosCount]
                                delPosCount=0
                                haveCount-=1
                                break
                            else:
                                delPosCount+=1
        else:
            self.game.displayText+="You can't craft that...\n"
        print("got to the end")
