import requests
from bs4 import BeautifulSoup
import json
import config

FRUITURL = "https://blox-fruits.fandom.com/wiki/Blox_Fruits"
GPURLS = "https://blox-fruits.fandom.com/wiki/Shop"
FILEDIR = "data/fruitdata.json"


class bloxfruit():
    def __init__(self, name, permanent=False, rarity=None, type=None, price=None, robux=None, awakening=None):
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

    def __str__(self):
        return self.name.capitalize()



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

        specialNames = config.getConfig("specialnames")
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

                specialNames = config.getConfig("specialnames")
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