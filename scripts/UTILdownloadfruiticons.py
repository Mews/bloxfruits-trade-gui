import requests
from bs4 import BeautifulSoup
import os
from config import getConfig

IMAGES = list()

#get fruits src
content = requests.get("https://blox-fruits.fandom.com/wiki/Blox_Fruits").content

soup = BeautifulSoup(content, features="html.parser")

DIVS = soup.find_all("div", {"class": "GunBox StandBoxs"})

for i, div in enumerate(DIVS):
    fruitName = div.get_text().replace("\n","").lower()
    img = div.find("img")
    fileDir = "assets/"+fruitName+".png"
    if i == 0:
        src = img.get("src")
        IMAGES.append( (src, fileDir) )
    else:
        src = img.get("data-src")
        IMAGES.append( (src, fileDir) )

#get gamepass src
content = requests.get("https://blox-fruits.fandom.com/wiki/Shop").content

soup = BeautifulSoup(content, features="html.parser")

MDIVS = soup.find_all("div", {"class": "wds-tab__content"})
banWords = ["Robux", "Shard", "Fragment", "MoneyIcon", "Money1", "Money2", "Money3", "Money4", "Money5"]
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

            src = DIVS[i+1].find("img").get("data-src")
            fileDir = "assets/"+passName+".png"

            IMAGES.append( (src, fileDir) )
        
    
#download images
for src, fileDir in IMAGES:
    print("Downloading image from", src)
    image_data = requests.get(src).content
    print("Saving image to", fileDir)
    with open(fileDir, "wb") as file:
        file.write(image_data)
