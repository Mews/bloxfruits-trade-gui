import requests
from bs4 import BeautifulSoup
from datetime import datetime

restockHours = [4,8,12,16,20,0]
URL = "https://blox-fruits.fandom.com/wiki/Blox_Fruits_%22Stock%22"

class fruit:
    def __init__(self,name,priceString):
        self.name = name
        self.priceString = priceString
        self.price = int(priceString.replace(",",""))


def textToFruits(text):
    array = text.split("\n")
    
    #remove '' elements from array
    while "" in array:
        array.remove("")
    
    #remove spaces and commas from array elements
    for i, e in enumerate(array):
        array[i] = array[i].replace(" ", "")
        #array[i] = array[i].replace(",", "")
    
    #remove first array element
    array.pop(0)

    #remove duplicates from array
    array = list(set(array))

    fruits = []

    for fruitText in array:
        fruitTextList = list(fruitText)
        for i, letter in enumerate(fruitTextList):
            try:
                if fruitTextList[i+1].isdigit() and letter.isalpha():
                    fruitName = ""
                    for letter in fruitTextList[:i+1]: fruitName += letter
                    fruitPrice = ""
                    for letter in fruitTextList[i+1:]: fruitPrice += letter
                    #fruitPrice = int(fruitPrice)

                    fruits.append(fruit( fruitName, fruitPrice ) )

            except:
                pass
    
    #sort list of fruits by price
    fruits.sort(key=lambda x: x.price, reverse=False)

    return fruits


def getTimeTillRestock():

    nextRestockHour = int()
    for restockHour in restockHours:
        if datetime.now().hour < restockHour:
            nextRestockHour = restockHour
            break
    restockDay = datetime.now().day
    if datetime.now().hour > nextRestockHour: restockDay+=1

    restockTime = datetime( datetime.now().year , datetime.now().month, restockDay, nextRestockHour, 0, 0 ,0)

    return restockTime - datetime.now()
    

def getCurrentFruits():
    content = requests.get(URL).content

    soup = BeautifulSoup(content, features="html.parser")

    currentText = soup.find("div", {"id": "mw-customcollapsible-current"}).get_text()

    return textToFruits(currentText)


def getLastFruits():
    content = requests.get(URL).content

    soup = BeautifulSoup(content, features="html.parser")

    lastText = soup.find("div", {"id": "mw-customcollapsible-last"}).get_text()

    return textToFruits(lastText)


def getBeforeLastFruits():
    content = requests.get(URL).content

    soup = BeautifulSoup(content, features="html.parser")

    blastText = soup.find("div", {"id": "mw-customcollapsible-beforelast"}).get_text()

    return textToFruits(blastText)