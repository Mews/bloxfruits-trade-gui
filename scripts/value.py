import requests
from bs4 import BeautifulSoup
import json

URLS = ["common", "uncommon", "rare", "legendary", "mythical", "gamepass"]
FILEDIR = "data/values.json"

for i, url in enumerate(URLS):
    URLS[i] = "https://www.bloxfruitsvalues.com/"+url

values = dict()

def listToString(list):
    string = str()

    for char in list:
        string += char

    return string

def getFruitNameFromText(fruitText):
    fruitTextList = list(fruitText)
    splitIndexes = list()
    splitTextList = list()

    #Find indexes of upper case letters to split
    for i, char in enumerate(fruitTextList):
        if char.isupper() or char.isdigit() or char == "+":
            splitIndexes.append(i)

    #Split text at split indexes
    splitTextList = fruitTextList[splitIndexes[1]:splitIndexes[-1]]

    return listToString(splitTextList).lower()

def getFruitValueFromText(fruitText):
    fruitTextList = list(fruitText)
    splitTextList = list()
    
    #Remove commas
    while "," in fruitTextList: fruitTextList.remove(",")

    #Split list at first number
    for i, char in enumerate(fruitTextList):
        if char.isdigit():
            splitTextList = fruitTextList[i:]
            break
    
    return int(listToString(splitTextList))

def downloadFruitValues():
    for url in URLS:
        content = requests.get(url).content

        soup = BeautifulSoup(content, features="html.parser")

        DIVS = soup.find_all("div", {"class": "flex flex-col w-[334px]"})

        if url == "https://www.bloxfruitsvalues.com/gamepass":
            for div in DIVS:
                fruitNameDiv = div.find("div", {"class": "flex flex-row justify-between items-start"})
                fruitName = getFruitNameFromText(fruitNameDiv.get_text())
                fruitValueDiv = div.find("div", {"class": "text-sm font-medium text-[#f2f2f2] mt-px"})
                fruitValue = getFruitValueFromText(fruitValueDiv.get_text())

                values[fruitName] = fruitValue

        else:
            for div in DIVS:
                fruitNameDiv = div.find("div", {"class": "relative flex flex-col justify-end ml-px pt-2 gap-1 items-end cursor-pointer"})
                fruitName = getFruitNameFromText(fruitNameDiv.get_text())
                fruitValueDiv = div.find("div", {"class": "text-sm font-medium text-[#f2f2f2] mt-px"})
                fruitValue = getFruitValueFromText(fruitValueDiv.get_text())

                values[fruitName] = fruitValue

    return values

def saveFruitValues(fileDir = FILEDIR):
    with open(fileDir, "w") as f:
        f.write(json.dumps(downloadFruitValues(), indent=2))

def readFruitValues(fileDir = FILEDIR):
    with open(fileDir) as f:
        return json.loads(f.read())
    
def getFruitValue(fruitName, fileDir = FILEDIR):
    with open(fileDir) as f:
        return json.loads(f.read())[fruitName.lower()]
    
saveFruitValues()