import tkinter as tk
from math import floor
from scripts.gui import *
from scripts.stock import *
from scripts.value import saveFruitValues
from scripts.bloxfruit import *
from tkscrolledframe import ScrolledFrame

#Segoe UI
#90A4AE

#Create main window
root = tk.Tk()
root.geometry("900x800")
root.iconbitmap("assets/kitsune.ico")
root.title("Blox Fruits")
root.resizable(0,0)

#Update fruit values when starting
saveFruitValues()


############ STOCK FRAME ############
############ STOCK FRAME ############
############ STOCK FRAME ############
def stockLoop():
    global CFRUITS, LFRUITS, BLFRUITS

    timeTillRestock = getTimeTillRestock()
    timeTillRestockLabel.config(text="Time till restock: "+str(timeTillRestock).split(".")[0])

    if int(timeTillRestock.total_seconds()) % (60*5) == 0:
        print("Updating fruit stock")

        CFRUITS = getCurrentFruits()
        LFRUITS = getLastFruits()
        BLFRUITS = getBeforeLastFruits()

        updateStockFrame()

    root.after(1, stockLoop)


def updateStockFrame():
    global CFRUITLABELS

    for fl in CFRUITLABELS:
            fl.destroy()

    CFRUITLABELS = list()

    for fruit in CFRUITS:
        CFRUITLABELS.append(fruitLabel(stockFrame, fruit.name, usePrice=True))

    for i, fl in enumerate(CFRUITLABELS):
        fl.grid(row=floor(i/2)+1, column=int((not i%2 == 0)), pady=(0,5))


def toggleLastStock():
    global LFRUITLABELS, lastVisible

    lFrame = tk.Frame(stockFrame, bg=STOCKBG)

    #Toggle on
    if not lastVisible:
        lastVisible = True

        #Delete previous fruit labels
        for fl in LFRUITLABELS:
                fl.destroy()

        LFRUITLABELS = list()

        #Create fruit labels for fruits in LFRUITS
        for fruit in LFRUITS:
            LFRUITLABELS.append(fruitLabel(lFrame, fruit.name, usePrice=True))
        
        for i, fl in enumerate(LFRUITLABELS):
            fl.grid(row=floor(i/2)+1, column=int((not i%2 == 0)), padx=7, pady=(5,1))

        #Place lFrame
        lFrame.columnconfigure(0, weight=1, uniform="lframe")
        lFrame.columnconfigure(1, weight=1, uniform="lframe")

        lFrame.grid(row=101, column=0, columnspan=2, sticky=tk.W)

    elif lastVisible:
        #Delete widget in row 101 and column = 0
        for widget in stockFrame.grid_slaves():
            row = int(widget.grid_info()["row"])
            column = int(widget.grid_info()["column"])
            if row == 101 and column == 0:
                widget.destroy()

        #Place lFrame
        lFrame.grid(row=101, column=0, columnspan=2, sticky=tk.W)
        lastVisible = False


def toggleBLastStock():
    global BLFRUITLABELS
    global blastVisible

    blFrame = tk.Frame(stockFrame, bg=STOCKBG)

    #Toggle on
    if not blastVisible:
        blastVisible = True

        #Delete previous fruit labels
        for fl in BLFRUITLABELS:
            fl.destroy()

        BLFRUITLABELS = list()

        #Create fruit labels for fruits in BLFRUITS
        for fruit in BLFRUITS:
            BLFRUITLABELS.append(fruitLabel(blFrame, fruit.name, usePrice=True))
        
        for i, fl in enumerate(BLFRUITLABELS):
            fl.grid(row=floor(i/2)+1, column=int((not i%2 == 0)), padx=7, pady=(5,1))

        #Place blFrame
        blFrame.columnconfigure(0, weight=1, uniform="blframe")
        blFrame.columnconfigure(1, weight=1, uniform="blframe")

        blFrame.grid(row=103, column=0, columnspan=2, sticky=tk.W)
    
    #Toggle off
    elif blastVisible:
        #Delete widget in row 103 and column = 0
        for widget in stockFrame.grid_slaves():
            row = int(widget.grid_info()["row"])
            column = int(widget.grid_info()["column"])
            if row == 103 and column == 0:
                widget.destroy()

        #Place blFrame
        blFrame.grid(row=103, column=0, columnspan=2, sticky=tk.W)
        blastVisible = False

def initStockFrame():
    global timeTillRestockLabel

    timeTillRestockLabel = tk.Label(stockFrame, text="", anchor=tk.W, font=("Segoe UI", 10), bg="white", relief="ridge", borderwidth=2, padx=5, pady=2)
    timeTillRestockLabel.grid(row=0, column=0, sticky=tk.W+tk.E, padx=6, columnspan=2, pady=5)

    lastStockButton = tk.Button(stockFrame, text="Toggle Last Stock", command=toggleLastStock, padx=100, bg="white")
    lastStockButton.grid(row=100, columnspan=2, column=0, padx=7, pady=0, sticky=tk.W)
    blastStockButton = tk.Button(stockFrame, text="Toggle Before Last Stock", command=toggleBLastStock, padx=100, bg="white")
    blastStockButton.grid(row=102, columnspan=2, column=0, padx=7, pady=(5,0), sticky=tk.W)

    updateStockFrame()


#----FRUIT STOCK--------~
STOCKBG = "#90A4AE"

CFRUITLABELS = list()
LFRUITLABELS = list()
BLFRUITLABELS = list()
CFRUITS = getCurrentFruits()
#FRUITS = [bloxfruit("kitsune"),bloxfruit("shadow"),bloxfruit("leopard"),bloxfruit("buddha"),bloxfruit("gravity"),bloxfruit("pain"),bloxfruit("sound"),bloxfruit("kitsune"),bloxfruit("shadow"),bloxfruit("leopard"),bloxfruit("buddha"),bloxfruit("gravity"),bloxfruit("pain"),bloxfruit("sound")]
LFRUITS = getLastFruits()
BLFRUITS = getBeforeLastFruits()
lastVisible = False
blastVisible = False

#Gui elements
scrollableStockFrame = ScrolledFrame(root, relief="solid", scrollbars="vertical", width=200)
scrollableStockFrame.grid(column=0, row=0, sticky=tk.N+tk.W+tk.S)

stockFrame = scrollableStockFrame.display_widget(tk.Frame, fit_width=True)
stockFrame.config(borderwidth=3, background=STOCKBG, height=1500)
stockFrame.grid_propagate(False)
stockFrame.columnconfigure(0, weight=1, uniform="stockframe")
stockFrame.columnconfigure(1, weight=1, uniform="stockframe")

#Lets column 0 and row 0 in root stretch
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

initStockFrame()

############ STOCK FRAME ############
############ STOCK FRAME ############
############ STOCK FRAME ############

#Start loops
stockLoop()

root.update_idletasks()
root.mainloop()