import tkinter as tk
from PIL import ImageTk, Image
try:
    from value import getFruitValue
    from bloxfruit import getFruitProperty
    from trade import trade
except:
    from .value import getFruitValue
    from .bloxfruit import getFruitProperty
    from .trade import trade


def fruitLabel(root, fruitName = "rocket", width = 75, height = 75, relief = "ridge", usePrice = True) -> tk.Frame:
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
