import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import dateutil.parser as dateparser
from PIL import Image, ImageOps, ImageDraw, UnidentifiedImageError
from io import BytesIO
from datetime import datetime, timedelta
import json
try:
    from bloxfruit import bloxfruit, fruitFromSerialized
    from value import getFruitValue
    from config import getConfig
except:
    from .bloxfruit import bloxfruit, fruitFromSerialized
    from .value import getFruitValue
    from .config import getConfig


URL = getConfig("tradesurl")

class Trade():
    def __init__(self, HAS:list, WANTS:list, author:str, postTime:datetime, authorLink:str, tradeLink:str, authorsrc:str):
        self.HAS = HAS
        self.WANTS = WANTS
        self.author = author
        self.postTime = postTime
        self.authorLink = authorLink
        self.tradeLink = tradeLink
        self.authorsrc = authorsrc

    def evaluateHas(self) -> int:
        value = int()
        for fruit in self.HAS:
            value += getFruitValue(fruit.name)
        
        return value
    
    def evaluateWants(self) -> int:
        value = int()
        for fruit in self.WANTS:
            value += getFruitValue(fruit.name)
        
        return value
    
    def isValuable(self) -> bool:
        #Get inventory from config
        inventory = getConfig("INVENTORY")
        for i, fruitData in enumerate(inventory):
            inventory[i] = fruitFromSerialized(fruitData)

        wantsInInventory = True
        hasInInventory = False

        for fruit in self.WANTS:
            if not fruit in inventory:
                wantsInInventory = False

        for fruit in self.HAS:
            if fruit in inventory:
                hasInInventory = True


        if wantsInInventory and not hasInInventory:
            return self.evaluateHas() > self.evaluateWants()
        else:
            return False
    
    def getAutorPfp(self, circle = True) -> Image:
        try:
            content = requests.get(self.authorsrc).content

            image = Image.open(BytesIO(content))
        except UnidentifiedImageError:
            content = requests.get(getConfig("staticpfpsrc")).content

            image = Image.open(BytesIO(content))

        if circle:
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0,0) + image.size, fill=255)

            image = ImageOps.fit(image, mask.size, centering=(0.5,0.5))
            image.putalpha(mask)

        return image
    
    def getGain(self) -> int:
        return self.evaluateHas() - self.evaluateWants()
    
    def getTimeSincePost(self) -> timedelta:
        naivePostTime = self.postTime.replace(tzinfo=None)
        timeDelta = datetime.now()-naivePostTime
        
        totalSeconds = int(timeDelta.total_seconds())
        days = totalSeconds // (24*60*60)
        totalSeconds -= days*24*60*60
        hours = totalSeconds // (60*60)
        totalSeconds -= hours*60*60
        minutes = totalSeconds // 60
        totalSeconds -= minutes*60
        seconds = totalSeconds

        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=0, milliseconds=0)
    
    def getPrettyTimeSincePost(self) -> str:
        naivePostTime = self.postTime.replace(tzinfo=None)
        timeDelta = datetime.now()-naivePostTime
        
        totalSeconds = int(timeDelta.total_seconds())
    
        days = totalSeconds // (24*60*60)
        totalSeconds -= days*24*60*60
        hours = totalSeconds // (60*60)
        totalSeconds -= hours*60*60
        minutes = totalSeconds // 60
        totalSeconds -= minutes*60
        seconds = totalSeconds

        if days == 0:
            if hours == 0:
                if minutes == 0:
                    return str(seconds)+" seconds ago"
                return str(minutes)+" minutes ago"
            return str(hours)+" hours ago"
        return str(days)+" days ago"
    

    def serialize(self):
        ATRIBUTES = vars(self)
        data = dict()

        for atribute in ATRIBUTES:
            if not atribute == None:
                try:
                    json.dumps(ATRIBUTES[atribute])
                    data[atribute] = ATRIBUTES[atribute]
                except:
                    if atribute == "HAS" or atribute == "WANTS":
                        data[atribute] = list()
                        for fruit in ATRIBUTES[atribute]:
                            data[atribute].append(fruit.serialize())
                    if atribute == "postTime":
                        data[atribute] = str(self.postTime)
        
        return json.dumps(data)
            
    


def downloadTradeFeed():
    TRADES = list()

    #Create headless edge driver
    OPTIONS = webdriver.EdgeOptions()
    OPTIONS.add_argument("headless")
    DRIVER = webdriver.Edge(options=OPTIONS)

    #Open url in driver
    DRIVER.get(URL)
    
    #Scrape driver page source
    soup = BeautifulSoup(DRIVER.page_source, features="html.parser")

    TRADEDIVS = soup.find_all("div", {"class": "card rounded-4 mb-3 border-0 text-light bg-cards"})

    for tradeDiv in TRADEDIVS:
        #Parse time of posting as datetime.datetime
        unparsedTime = tradeDiv.get("data-time")
        postTime = dateparser.parse(unparsedTime, fuzzy=True)

        #Get author information
        authorDiv = tradeDiv.find("a", {"class": "text-decoration-none text-light"})
        author = authorDiv.get_text().replace(" ","").replace("\n","")
        authorLink = "https://fruityblox.com"+authorDiv.get("href")

        authorpfpDiv = tradeDiv.find("img", {"alt": "Profile image"})
        authorsrc = authorpfpDiv.get("src")

        if authorsrc.startswith("/static") or authorsrc.startswith("https://cdn.discordapp.com"): authorsrc = getConfig("staticpfpsrc")


        #Get trade link
        tradeButtonDiv = tradeDiv.find("a", {"class": "btn bg-transparent w-100 brand-button"})
        tradeLink = "https://fruityblox.com"+tradeButtonDiv.get("href")
        

        #Get trades
        #HAS
        HAS = list()

        hasdiv = tradeDiv.find("div", {"id": "trade-has-col"})
        FRUITDIVS = hasdiv.find_all("p")

        for fruitDiv in FRUITDIVS:
            fruitName = fruitDiv.get_text().lower()
            fruitPermanent = False

            #Skip "has" <p> tag
            if fruitName == "has":
                continue
            
            if "(perm)" in fruitName:
                fruitPermanent = True
                fruitName = fruitName.split(" ")[0]

            HAS.append(bloxfruit(fruitName, permanent=fruitPermanent))


        #WANTS
        WANTS = list()

        wantsdiv = tradeDiv.find("div", {"id": "trade-wants-col"})
        FRUITDIVS = wantsdiv.find_all("p")

        for fruitDiv in FRUITDIVS:
            fruitName = fruitDiv.get_text().lower()
            fruitPermanent = False

            #Skip "has" <p> tag
            if fruitName == "wants":
                continue
            
            if "(perm)" in fruitName:
                fruitPermanent = True
                fruitName = fruitName.split(" ")[0]

            WANTS.append(bloxfruit(fruitName, permanent=fruitPermanent))

        TRADES.append(Trade(HAS=HAS, 
                            WANTS=WANTS, 
                            author=author, 
                            postTime=postTime, 
                            authorLink=authorLink, 
                            tradeLink=tradeLink,
                            authorsrc=authorsrc))
    
    return TRADES

def tradeFromSerialized(serializedData:str) -> Trade:
    data = json.loads(serializedData)
    
    for atribute in data:
        value = data[atribute]
        HAS = list()
        WANTS = list()

        if atribute == "HAS":
            for fruitData in value:
                newFruit = bloxfruit(None)
                newFruit.deserialize(fruitData)
                HAS.append(newFruit)
        
        
        
        elif atribute == "WANTS":
            for fruitData in value:
                newFruit = bloxfruit(None)
                newFruit.deserialize(fruitData)
                WANTS.append(newFruit)

        elif atribute == "postTime": postTime = dateparser.parse(value, fuzzy=True)

        elif atribute == "author": author = value
        elif atribute == "tradeLink": tradeLink = value
        elif atribute == "authorLink": authorLink = value
        elif atribute == "authorsrc": authorsrc = value

    return Trade(HAS=HAS, WANTS=WANTS, author=author, postTime=postTime, authorLink=authorLink, tradeLink=tradeLink, authorsrc=authorsrc)

        


""" t = trade(HAS=[bloxfruit("rocket"), bloxfruit("gravity")],
          WANTS=[bloxfruit("blizzard"), bloxfruit("sound")],
          author="Mews",
          postTime=datetime.now(),
          tradeLink="https://fruityblox.com/trade/65931283920bba3c155c62cc",
          authorLink="https://fruityblox.com/player/658c17401deedde35408bc1e",
          authorsrc="https://tr.rbxcdn.com/30DAY-AvatarHeadshot-5AD9D35C0B30400153BE8A997D3FC16F-Png/352/352/AvatarHeadshot/Png/noFilter") """