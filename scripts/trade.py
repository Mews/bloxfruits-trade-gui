import requests
from bs4 import BeautifulSoup
from bloxfruit import bloxfruit
from selenium import webdriver
import dateutil.parser as dateparser


URL = "https://fruityblox.com/trading"

class trade():
    def __init__(self, HAS, WANTS, author, postTime, authorLink, tradeLink, authorsrc):
        self.HAS = HAS
        self.WANTS = WANTS
        self.author = author
        self.postTime = postTime
        self.authorlink = authorLink
        self.tradelink = tradeLink
        self.authorsrc = authorsrc

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
        authorlink = "https://fruityblox.com"+authorDiv.get("href")

        authorpfpDiv = tradeDiv.find("img", {"alt": "Profile image"})
        authorsrc = authorpfpDiv.get("src")

        if authorsrc.startswith("/static"): authorsrc = "https://fruityblox.com"+authorsrc
        if authorsrc.startswith("https://cdn.discordapp.com"): authorsrc = "https://fruityblox.com/static/img/profile-pic.png"

        #Get trade link
        tradeButtonDiv = tradeDiv.find("a", {"class": "btn bg-transparent w-100 brand-button"})
        tradeLink = "https://fruityblox.com"+tradeButtonDiv.get("href")
        
        

        

downloadTradeFeed()