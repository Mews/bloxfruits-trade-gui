import tkinter as tk
from PIL import ImageTk, Image
from scripts.value import getFruitValue
from scripts.bloxfruit import getFruitProperty

def fruitLabel(root, fruitName = "rocket", width = 75, height = 75, relief = "ridge", usePrice = True):
    global fruitIcon
    fruitName = fruitName.lower()

    frame = tk.Frame(root, borderwidth=2, relief=relief)

    fruitIcon = ImageTk.PhotoImage(Image.open("assets/"+fruitName+".png").resize( (width,height) ))

    if usePrice:
        fruitPrice = getFruitProperty(fruitName, "price")
        fruitPriceString = "$"+f'{fruitPrice:,}'

    else:
        fruitPrice = getFruitValue(fruitName)
        fruitPriceString = "$"+f'{fruitPrice:,}'


    picLabel = tk.Label(frame, image=fruitIcon)
    picLabel.image = fruitIcon
    nameLabel = tk.Label(frame, text=fruitName.capitalize())
    priceLabel = tk.Label(frame, text=fruitPriceString, fg="green")
 
    picLabel.pack()
    nameLabel.pack()
    priceLabel.pack()

    return frame