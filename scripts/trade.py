import requests
from bs4 import BeautifulSoup
from bloxfruit import bloxfruit
from selenium import webdriver


URL = "https://fruityblox.com/trading"

class trade():
    def __init__(self, HAS, WANTS, author, postTime, authorlink, tradelink, authorpfp):
        self.HAS = HAS
        self.WANTS = WANTS
        self.author = author
        self.postTime = postTime
        self.authorlink = authorlink

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
        authorDiv = tradeDiv.find("a", {"class": "text-decoration-none text-light"})
        author = authorDiv.get_text().replace(" ","").replace("\n","")
        authorlink = "https://fruityblox.com/"+authorDiv.get("href")

        print(authorlink)
        

downloadTradeFeed()