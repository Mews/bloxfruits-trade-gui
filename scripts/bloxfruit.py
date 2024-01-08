import requests
from bs4 import BeautifulSoup
import json
try:
    from config import getConfig
except:
    from .config import getConfig

FRUITURL = getConfig("fruitdataurl")
GPURLS = getConfig("gamepassdataurl")
FILEDIR = "data/fruitdata.json"


class bloxfruit():
    def __init__(self, name:str, permanent=False, rarity=None, type=None, price=None, robux=None, awakening=None):
        if name == None: name = "Rocket"
        self.name = name.lower()

        if rarity == None: self.rarity = getFruitProperty(name, "rarity")
        else: self.rarity = rarity

        if type == None: self.type = getFruitProperty(name, "type")
        else: self.type = type
        
        if price == None: self.price = getFruitProperty(name, "price")
        else: self.price = price

        if robux == None: self.robux = getFruitProperty(name, "robux")
        else: self.robux = robux

        if awakening == None: self.awakening = getFruitProperty(name, "awakening")
        else: self.awakening = awakening

        self.permanent = permanent

        if self.price == None: self.price = self.robux

    def __str__(self):
        return self.name.capitalize()
    
    def __eq__(self, other):
        equal = True
        selfVars = vars(self)
        otherVars = vars(other)

        for var in selfVars:
            if not selfVars[var] == otherVars[var]:
                equal = False
        
        return equal

    def __lt__(self, other):
        return self.price < other.price
    
    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def deserialize(self, serializedData:str):
        data = json.loads(serializedData)
        self.name=data["name"]
        self.rarity=data["rarity"]
        self.type=data["type"] 
        self.price=data["price"] 
        self.robux=data["robux"]
        self.awakening=data["awakening"] 
        self.permanent=data["permanent"]


def downloadFruitData():
    #FRUITS
    FRUITDATA = dict()

    content = requests.get(FRUITURL).content

    soup = BeautifulSoup(content, features="html.parser")

    DIVS = soup.find_all("table", {"class": "mobileonly fandom-table"})

    for div in DIVS: 
        divList = div.get_text().split("\n")
        while "" in divList: divList.remove("")
        
        try:
            fruitName = divList[0].replace(" ","").lower()
            fruitRarity = divList[1].lower()
            fruitType = divList[2].split(":")[1].replace(" ","").lower()
            fruitPrice = int(divList[3].split("or")[0].split(":")[1].replace(" ","").replace(",",""))
            fruitPriceRobux = int(divList[3].split("or")[1].replace(" ","").replace(",",""))
            fruitAwakening = divList[4].split(":")[1].replace(" ","").replace(",","")
        except Exception as e:
            fruitPrice = None
            fruitPriceRobux = None

        if not fruitAwakening == "None":
            fruitAwakening = int(fruitAwakening)

        #Apply special names from config
        specialNames = getConfig("specialnames")
        for sn in specialNames:
            fruitName = fruitName.replace(sn[0], sn[1])
        
        FRUITDATA[fruitName] = dict()
        FRUITDATA[fruitName]["rarity"] = fruitRarity
        FRUITDATA[fruitName]["type"] = fruitType
        FRUITDATA[fruitName]["price"] = fruitPrice
        FRUITDATA[fruitName]["robux"] = fruitPriceRobux
        if fruitAwakening == "None":
            FRUITDATA[fruitName]["awakening"] = None
            continue
        FRUITDATA[fruitName]["awakening"] = fruitAwakening

    #GAMEPASSES
    content = requests.get(GPURLS).content

    soup = BeautifulSoup(content, features="html.parser")

    MDIVS = soup.find_all("div", {"class": "wds-tab__content"})
    
    for mdiv in MDIVS:
        DIVS = mdiv.find_all("tr")
        for i, div in enumerate(DIVS):

            lineList = div.get_text().split("\n")
            while "" in lineList: lineList.remove("")

            if len(lineList) == 2 and lineList[1].replace(" ","").replace(",","").isdigit():
                passName = lineList[0].lower()

                #Apply special names from config
                specialNames = getConfig("specialnames")
                for sn in specialNames:
                    passName = passName.replace(sn[0], sn[1])

                passRobux = int(lineList[1].replace(" ","").replace(",",""))

                FRUITDATA[passName] = dict()
                FRUITDATA[passName]["rarity"] = "premium"
                FRUITDATA[passName]["type"] = None
                FRUITDATA[passName]["price"] = None
                FRUITDATA[passName]["robux"] = passRobux
                FRUITDATA[passName]["awakening"] = None


    return FRUITDATA


def saveFruitData(fileDir = FILEDIR):
    with open(fileDir, "w") as f:
        f.write(json.dumps(downloadFruitData(), indent=2))

def readFruitData(fileDir = FILEDIR):
    with open(fileDir) as f:
        return json.loads(f.read())
    
def getFruitProperty(fruitName, property, fileDir = FILEDIR):
    with open(fileDir) as f:
        FRUITDATA = json.loads(f.read())
        return FRUITDATA[fruitName.lower()][property.lower()]
    
def fruitFromSerialized(serializedData:str) -> bloxfruit:
    data = json.loads(serializedData)
    return bloxfruit(name=data["name"], 
                     rarity=data["rarity"], 
                     type=data["type"], 
                     price=data["price"], 
                     robux=data["robux"], 
                     awakening=data["awakening"], 
                     permanent=data["permanent"])