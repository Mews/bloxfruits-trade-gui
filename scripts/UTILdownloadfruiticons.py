import requests
from bs4 import BeautifulSoup

content = requests.get("https://blox-fruits.fandom.com/wiki/Blox_Fruits").content

soup = BeautifulSoup(content, features="html.parser")

DIVS = soup.find_all("div", {"class": "GunBox StandBoxs"})
IMAGES = list()

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

for src, fileDir in IMAGES:
    print("Downloading image from", src)
    image_data = requests.get(src).content
    print("Saving image to", fileDir)
    with open(fileDir, "wb") as file:
        file.write(image_data)