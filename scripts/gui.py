import tkinter as tk
from PIL import ImageTk, Image
import os
from datetime import datetime
try:
    from value import getFruitValue
    from bloxfruit import getFruitProperty
    from trade import trade
except:
    from .value import getFruitValue
    from .bloxfruit import getFruitProperty
    from .trade import trade

#Fonts
#Cascadia Code
#Liberation Mono
#Lucida Console
#Malgun gothic


def fruitLabel(root, fruitName = "rocket", width = 75, height = 75, relief = "ridge", usePrice = True, permanent = False) -> tk.Frame:
    global fruitIcon
    fruitName = fruitName.lower()

    frame = tk.Frame(root, borderwidth=2, relief=relief)

    fruitIcon = ImageTk.PhotoImage(Image.open("assets/"+fruitName+".png").resize( (width,height) ))

    if usePrice and not getFruitProperty(fruitName, "price") == None:
        fruitPrice = getFruitProperty(fruitName, "price")
        fruitPriceString = "$"+f'{fruitPrice:,}'

    else:
        fruitPrice = getFruitValue(fruitName)
        fruitPriceString = "$"+f'{fruitPrice:,}'



    picLabel = tk.Label(frame, image=fruitIcon)
    picLabel.image = fruitIcon
    fruitNameText = fruitName.capitalize()
    if permanent: fruitNameText += " (Perm)"
    nameLabel = tk.Label(frame, text=fruitNameText)
    priceLabel = tk.Label(frame, text=fruitPriceString, fg="green")
 
    picLabel.pack()
    nameLabel.pack()
    priceLabel.pack()

    return frame


def tradeLabel(root, trade:trade, relief = "ridge", font = ("Cascadia Code", 10)) -> tk.Frame:
    global authorPfp

    mainframe = tk.Frame(root, borderwidth=2, relief=relief)

    authorframe = tk.Frame(mainframe, relief="flat")

    authorPfp = ImageTk.PhotoImage(trade.getAutorPfp().resize( (40,40) ))
    pfpLabel = tk.Label(authorframe, image=authorPfp)
    pfpLabel.grid(row=0,column=0, rowspan=2, sticky=tk.W+tk.N)

    authorNameLabel = tk.Label(authorframe, text=trade.author, font=font, anchor=tk.W)
    authorNameLabel.grid(row=0, column=1, sticky=tk.W+tk.N, padx=(3,0))

    timeSpanLabel = tk.Label(authorframe, text=trade.getPrettyTimeSincePost(), font=font, anchor=tk.W)
    timeSpanLabel.grid(row=1,column=1, sticky=tk.W+tk.N, padx=(3,0))

    authorframe.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.N)

    viewTradeCommand = "start "+trade.tradeLink
    viewTradeButton = tk.Button(mainframe, text="View Trade", command=lambda:os.system(viewTradeCommand))

    viewTradeButton.grid(row=0, column=2, columnspan=2, sticky=tk.E+tk.N,padx=7,pady=5)


    hasframe = tk.Frame(mainframe, borderwidth=1, relief="solid")
    hasframe.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    tk.Label(hasframe, text="Has", padx=5).grid(row=0, column=0, sticky=tk.W)

    for i, fruit in enumerate(trade.HAS):
        fLabel = fruitLabel( hasframe, str(fruit), width=35, height=35, relief="groove", permanent=fruit.permanent)
        fLabel.grid(row=1, column=i, padx=4, pady=(0,4))

    wantsframe = tk.Frame(mainframe, borderwidth=1, relief="solid")
    wantsframe.grid(row=1, column=2, columnspan=2, padx=5, pady=5)

    tk.Label(wantsframe, text="Wants", padx=5).grid(row=0, column=0, sticky=tk.W)

    for i, fruit in enumerate(trade.WANTS):
        fLabel = fruitLabel( wantsframe, str(fruit), width=35, height=35, relief="groove", permanent=fruit.permanent)
        fLabel.grid(row=1, column=i, padx=4, pady=(0,4))
    
    

    pfpLabel.image = authorPfp

    return mainframe