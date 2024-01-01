import requests
from bs4 import BeautifulSoup
from bloxfruit import bloxfruit
from selenium import webdriver
import dateutil.parser as dateparser
from value import getFruitValue
from config import getConfig
from PIL import Image
from io import BytesIO


URL = getConfig("tradesurl")

class trade():
    def __init__(self, HAS, WANTS, author, postTime, authorLink, tradeLink, authorsrc):
        self.HAS = HAS
        self.WANTS = WANTS
        self.author = author
        self.postTime = postTime
        self.authorlink = authorLink
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
        return self.evaluateHas() > self.evaluateWants()
    
    def getAutorPfp(self) -> Image:
        content = requests.get(self.authorsrc).content
        return Image.open(BytesIO(content))


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

        if authorsrc.startswith("/static"): authorsrc = "https://fruityblox.com"+authorsrc
        if authorsrc.startswith("https://cdn.discordapp.com"): authorsrc = "https://fruityblox.com/static/img/profile-pic.png"

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

        TRADES.append(trade(HAS=HAS, 
                            WANTS=WANTS, 
                            author=author, 
                            postTime=postTime, 
                            authorLink=authorLink, 
                            tradeLink=tradeLink,
                            authorsrc=authorsrc))
    
    return TRADES