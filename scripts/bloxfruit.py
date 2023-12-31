import requests
from bs4 import BeautifulSoup
import json

URL = "https://blox-fruits.fandom.com/wiki/Blox_Fruits"
FILEDIR = "data/fruitdata.json"


class bloxfruit():
    def __init__(self, name, rarity=None, type=None, price=None, robux=None, awakening=None):
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

    def __str__(self):
        return self.name.capitalize()



def downloadFruitData():

    FRUITDATA = dict()

    content = requests.get(URL).content

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

        FRUITDATA[fruitName] = dict()
        FRUITDATA[fruitName]["rarity"] = fruitRarity
        FRUITDATA[fruitName]["type"] = fruitType
        FRUITDATA[fruitName]["price"] = fruitPrice
        FRUITDATA[fruitName]["robux"] = fruitPriceRobux
        FRUITDATA[fruitName]["awakening"] = fruitAwakening

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
    
