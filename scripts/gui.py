import tkinter as tk
from PIL import ImageTk, Image
import os
from datetime import datetime
from tkscrolledframe import ScrolledFrame
from multiprocessing.dummy import Process, Queue
try:
    from value import getFruitValue
    from bloxfruit import getFruitProperty
    from trade import trade
    from config import getConfig
    from stock import getFruitStockInParalel, getTimeTillRestock
except:
    from .value import getFruitValue
    from .bloxfruit import getFruitProperty, bloxfruit
    from .trade import trade
    from .config import getConfig
    from .stock import getFruitStockInParalel, getTimeTillRestock

#Fonts
#Cascadia Code
#Liberation Mono
#Lucida Console
#Malgun gothic


def fruitLabel(root, 
               fruitName = "rocket", 
               width = 75, height = 75, 
               relief = "ridge", 
               usePrice = True, 
               permanent = False, 
               font=("Segoe UI", 9), 
               useRarityColors = True,
               background="#D2D2D2") -> tk.Frame:
    global fruitIcon
    fruitName = fruitName.lower()

    frame = tk.Frame(root, borderwidth=2, relief=relief, bg=background)

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

    if useRarityColors: fg = getConfig("raritycolors")[getFruitProperty(fruitName, "rarity")]
    else: fg = "black"

    nameLabel = tk.Label(frame, text=fruitNameText, font=font, fg=fg)
    priceLabel = tk.Label(frame, text=fruitPriceString, fg="green", font=font)
    
    for child in frame.winfo_children():
        child.config(bg=background)

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






class StockFrame(ScrolledFrame):
    BG = "#373737"
    SBG = "#606060"
    BPBG = "#959595"

    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        #Set canvas background color
        self._canvas.config(bg=self.BG)

        #Set scrollbar background color
        self._y_scrollbar.config(bg=self.SBG)

        #Create variables
        self.lVisible = False
        self.blVisible = False

        self.cFruitLabels = list()
        self.lFruitLabels = list()
        self.blFruitLabels = list()

        self.cFruits = list()
        self.lFruits = list()
        self.blFruits = list()
        self.cFruits, self.lFruits, self.blFruits = getFruitStockInParalel()

        #Create queues and process for threading
        self.QUEUES = [Queue() for i in range(3)]
        #self.p = Process(target=)

        #Create Frame inside parent ScrolledFrame
        self.mainFrame = self.display_widget(tk.Frame, fit_width=True)
        self.mainFrame.config(borderwidth=3, background=self.BG)
        self.mainFrame.grid_propagate(False)
        self.mainFrame.columnconfigure(0, weight=1, uniform="mainframe")
        self.mainFrame.columnconfigure(1, weight=1, uniform="mainframe")

        #Create and place Label that displays time till restock
        self.timeTillRestockLabel = tk.Label(self.mainFrame, text="", anchor=tk.W, font=("Segoe UI", 10), bg=self.SBG, relief="ridge", borderwidth=2, padx=5, pady=2, fg="white")
        self.timeTillRestockLabel.grid(row=0, column=0, sticky=tk.W+tk.E, padx=6, columnspan=2, pady=5)

        #Create and place Buttons that toggle last and before last stock
        self.lButton = tk.Button(self.mainFrame, text="Toggle Last Stock", command=self.toggleLastStock, padx=100, bg=self.SBG, activebackground=self.BPBG, fg="white")
        self.lButton.grid(row=100, columnspan=2, column=0, padx=7, pady=0, sticky=tk.W)

        self.blButton = tk.Button(self.mainFrame, text="Toggle Before Last Stock", command=self.toggleBlastStock, padx=100, bg=self.SBG, activebackground=self.BPBG, fg="white")
        self.blButton.grid(row=102, columnspan=2, column=0, padx=7, pady=(5,0), sticky=tk.W)

        #Create lFrame and blFrame
        self.lFrame = tk.Frame(self.mainFrame, bg=self.BG)
        self.lFrame.columnconfigure(0, weight=1, uniform="lframe")
        self.lFrame.columnconfigure(1, weight=1, uniform="lframe")

        self.blFrame = tk.Frame(self.mainFrame, bg=self.BG)
        self.blFrame.columnconfigure(0, weight=1, uniform="blframe")
        self.blFrame.columnconfigure(1, weight=1, uniform="blframe")

        #Start loops
        self.mainLoop()
        self.timeRemainingLoop()

#Loops
    def mainLoop(self):
        #Update fruit labels
        self.updateCurrentFruits()
        self.updatelFrame()
        self.updateblFrame()

        #Update main frame height
        self.after(0, self.updateHeight)

        #Bing all new widgets to scroll wheel
        self.bindAllToScrollWheel(self)

        #Start loop again after 5 minutes
        self.after(5*60*1000, self.mainLoop)


    def timeRemainingLoop(self):
        #Updates time till restock label constantly
        self.timeTillRestockLabel.config(text="Time till restock: "+str(getTimeTillRestock()).split(".")[0])

        self.after(1, self.timeRemainingLoop)


    def bindAllToScrollWheel(self, parent):
        #Recursively bind all widgets in parent to scroll wheel
        for widget in parent.winfo_children():
            self.bindAllToScrollWheel(widget)
        self.bind_scroll_wheel(parent)


    def updateHeight(self):
        #Updates mainFrame height
        self.mainFrame.grid_propagate(True)

        self.mainFrame.update_idletasks()

        reqHeight = self.mainFrame.winfo_reqheight()
        if reqHeight < self.winfo_height(): reqHeight = self.winfo_height()-2

        self.mainFrame.grid_propagate(False)

        self.mainFrame.config(height=reqHeight)

#Fruit labels
    def updateCurrentFruits(self):
        #Destroy previous fruit labels
        for fl in self.cFruitLabels: 
            fl.destroy()

        self.cFruitLabels.clear()

        #Create new fruit labels and place them
        for fruit in self.cFruits:
            self.cFruitLabels.append(fruitLabel(self.mainFrame, fruit.name, usePrice=True))

        for i, fl in enumerate(self.cFruitLabels):
            fl.grid(row=(i//2)+1, column=int((not i%2 == 0)), pady=(0,5))
    
    def updatelFrame(self):
        #Destroy previous fruit labels in lFrame
        for fl in self.lFruitLabels: 
                fl.destroy()

        self.lFruitLabels.clear()

        #Create new fruit labels and place them
        for fruit in self.lFruits:
            self.lFruitLabels.append(fruitLabel(self.lFrame, fruit.name, usePrice=True))

        for i, fl in enumerate(self.lFruitLabels):
            fl.grid(row=(i//2)+1, column=int((not i%2 == 0)), padx=7, pady=(5,1))

    def updateblFrame(self):
        #Destroy previous fruit labels in blFrame
        for fl in self.blFruitLabels: 
            fl.destroy()

        self.blFruitLabels.clear()

        #Create new fruit labels and place them
        for fruit in self.blFruits:
            self.blFruitLabels.append(fruitLabel(self.blFrame, fruit.name, usePrice=True))

        for i, fl in enumerate(self.blFruitLabels):
            fl.grid(row=(i//2)+1, column=int((not i%2 == 0)), padx=7, pady=(5,1))


#Toggle last and before last stocks
    def toggleLastStock(self):
        if not self.lVisible:
            self.lVisible = True
            self.lFrame.grid(row=101, column=0, columnspan=2, sticky=tk.W)

        elif self.lVisible:
            self.lVisible = False
            self.lFrame.grid_forget()
    
        self.updateHeight()
        
    def toggleBlastStock(self):
        if not self.blVisible:
            self.blVisible = True
            self.blFrame.grid(row=103, column=0, columnspan=2, sticky=tk.W)

        elif self.blVisible:
            self.blVisible = False
            self.blFrame.grid_forget()

        self.updateHeight()