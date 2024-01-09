import tkinter as tk
from tkinter import messagebox as tkmessagebox
from PIL import ImageTk, Image
import os
from datetime import datetime
from tkscrolledframe import ScrolledFrame
from multiprocessing.dummy import Process
import queue
try:
    from value import getFruitValue
    from bloxfruit import getFruitProperty, readFruitData, bloxfruit, fruitFromSerialized
    from trade import Trade
    from config import getConfig, changeConfig
    from stock import getFruitStockInParalel, getTimeTillRestock
except:
    from .value import getFruitValue
    from .bloxfruit import getFruitProperty, readFruitData, bloxfruit, fruitFromSerialized
    from .trade import Trade
    from .config import getConfig, changeConfig
    from .stock import getFruitStockInParalel, getTimeTillRestock

#Fonts
#Cascadia Code
#Liberation Mono
#Lucida Console
#Malgun gothic

guiColors = getConfig("guicolors")
BG = guiColors["bg"]
SBG = guiColors["secondarybg"]
ACTIVEBG = guiColors["activebuttonbg"]
SELECTEDBG = guiColors["selectedbg"]
FLBG = guiColors["fruitlabelbg"]


def fruitLabel(root,
               fruitName = "rocket", 
               width = 75, height = 75, 
               relief = "ridge", 
               usePrice = True,
               useValue = False, 
               permanent = False, 
               font=("Segoe UI", 9), 
               useRarityColors = True,
               background=FLBG) -> tk.Frame:
    global fruitIcon
    fruitName = fruitName.lower()

    frame = tk.Frame(root, borderwidth=2, relief=relief, bg=background)

    fruitIcon = ImageTk.PhotoImage(Image.open("assets/"+fruitName+".png").resize( (width,height) ))

    if usePrice and not getFruitProperty(fruitName, "price") == None:
        fruitPrice = getFruitProperty(fruitName, "price")
        fruitPriceString = "$"+f'{fruitPrice:,}'

    elif usePrice and getFruitProperty(fruitName, "price") == None:
        fruitPriceString = "N/A"

    if useValue:
        fruitPrice = getFruitValue(fruitName)
        fruitPriceString = "$"+f'{fruitPrice:,}'



    picLabel = tk.Label(frame, image=fruitIcon)
    picLabel.image = fruitIcon

    fruitNameText = fruitName.capitalize()
    if permanent: fruitNameText += " (Perm)"

    if useRarityColors: fg = getConfig("raritycolors")[getFruitProperty(fruitName, "rarity")]
    else: fg = "black"

    nameLabel = tk.Label(frame, text=fruitNameText, font=font, fg=fg, wraplength=picLabel.winfo_reqwidth())
    if not (not usePrice and not useValue): 
        priceLabel = tk.Label(frame, text=fruitPriceString, fg="green", font=font)
    
    for child in frame.winfo_children():
        child.config(bg=background)

    picLabel.pack()
    nameLabel.pack()
    if not (not usePrice and not useValue): 
        priceLabel.pack()

    return frame












def tradeLabel(root, trade:Trade, relief = "ridge", font = ("Cascadia Code", 10)) -> tk.Frame:
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
    def __init__(self, master, **kw):
        super().__init__(master=master, **kw)

        #Set canvas background color
        self._canvas.config(bg=BG)

        #Set scrollbar background color
        self._y_scrollbar.config(bg=SBG)

        #Create variables
        self.lVisible = False
        self.blVisible = False

        self.cFruitLabels = list()
        self.lFruitLabels = list()
        self.blFruitLabels = list()

        self.cFruits = list()
        self.lFruits = list()
        self.blFruits = list()

        #Create queues for threading
        self.resultQueues = [queue.Queue() for i in range(3)]

        #Create Frame inside parent ScrolledFrame
        self.mainFrame = self.display_widget(tk.Frame, fit_width=True)
        self.mainFrame.config(borderwidth=3, background=BG)
        self.mainFrame.grid_propagate(False)
        self.mainFrame.columnconfigure(0, weight=1, uniform="mainframe")
        self.mainFrame.columnconfigure(1, weight=1, uniform="mainframe")

        #Create and place Label that displays time till restock
        self.timeTillRestockLabel = tk.Label(self.mainFrame, text="", anchor=tk.W, font=("Segoe UI", 10), bg=SBG, relief="ridge", borderwidth=2, padx=5, pady=2, fg="white")
        self.timeTillRestockLabel.grid(row=0, column=0, sticky=tk.W+tk.E, padx=6, columnspan=2, pady=5)

        #Create and place Buttons that toggle last and before last stock
        self.lButton = tk.Button(self.mainFrame, text="Toggle Last Stock", command=self.toggleLastStock, padx=15, bg=SBG, activebackground=ACTIVEBG, fg="white")
        self.lButton.grid(row=100, columnspan=2, column=0, padx=7, pady=0, sticky=tk.W+tk.E)

        self.blButton = tk.Button(self.mainFrame, text="Toggle Before Last Stock", command=self.toggleBlastStock, padx=15, bg=SBG, activebackground=ACTIVEBG, fg="white")
        self.blButton.grid(row=102, columnspan=2, column=0, padx=7, pady=(5,0), sticky=tk.W+tk.E)

        #Create lFrame and blFrame
        self.lFrame = tk.Frame(self.mainFrame, bg=BG)
        self.lFrame.columnconfigure(0, weight=1, uniform="lframe")
        self.lFrame.columnconfigure(1, weight=1, uniform="lframe")

        self.blFrame = tk.Frame(self.mainFrame, bg=BG)
        self.blFrame.columnconfigure(0, weight=1, uniform="blframe")
        self.blFrame.columnconfigure(1, weight=1, uniform="blframe")

        #Create labels to signal worker function is still running
        self.waitingLabel = tk.Label(self.mainFrame, text="Waiting for data...", anchor=tk.CENTER, bg=BG, fg="white")

        #Start loops
        self.mainLoop()
        self.timeRemainingLoop()

#Loops
    def mainLoop(self):
        #Update fruit stock in paralel
        self.startThread()

        #Update main frame height
        self.after(0, self.updateHeight)

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
    
#Threading functions
    def worker(self, resultQueues):
        cFruits, lFruits, blFruits = getFruitStockInParalel()
        resultQueues[0].put(cFruits)
        resultQueues[1].put(lFruits)
        resultQueues[2].put(blFruits)

    def startThread(self):
        Process(target=self.worker, args=(self.resultQueues, )).start()
        self.waitForResults()

    def waitForResults(self):
        try:
            #Get data from queues
            self.cFruits = self.resultQueues[0].get_nowait()
            self.lFruits = self.resultQueues[1].get_nowait()
            self.blFruits = self.resultQueues[2].get_nowait()

            #Hide waiting label
            self.waitingLabel.grid_forget()

            #Re-enable buttons
            self.lButton.config(state=tk.NORMAL)
            self.blButton.config(state=tk.NORMAL)

            #Update fruit labels with new data
            self.updateCurrentFruits()
            self.updatelFrame()
            self.updateblFrame()

            #Bind all new widgets to scroll wheel
            self.bindAllToScrollWheel(self)

        except queue.Empty:
            #Check if there is no fruit data
            if self.cFruits == []:
                #Display waiting label
                self.waitingLabel.grid(row=1, column=0, columnspan=2, pady=10, padx=10)
                
                #Disable buttons
                self.lButton.config(state=tk.DISABLED)
                self.blButton.config(state=tk.DISABLED)

            self.after(100, self.waitForResults)
            

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


















class FruitSelector(ScrolledFrame):
    INVALIDNAMES = getConfig("invalidnames")

    def __init__(self, master, columns=3, picWidth=100, picHeight=100, **kw):
        super().__init__(master=master, **kw)

        self.columns = columns
        self.picWidth = picWidth
        self.picHeight = picHeight

        #Set canvas background color
        self.config(bg=BG)

        #Set scrollbar background color
        self._y_scrollbar.config(bg=SBG)

        #Create variables
        self.fruitData = readFruitData()
        self.fruitLabels = list()
        self.mainFrame = self.display_widget(tk.Frame, fit_width=True, bg=BG)

        #for i in range(self.columns): self.mainFrame.columnconfigure(i, weight=1)

        self.selectedFrame = None

        self.checkbox = None
        self.permanent = tk.BooleanVar()

        #Create fruit label for each fruit in fruit data
        for fruitName in self.fruitData:
            if not fruitName in self.INVALIDNAMES:
                self.fruitLabels.append(fruitLabel(self.mainFrame, fruitName, usePrice=False, width=self.picWidth, height=self.picHeight, font=("Segoe UI", 0)))


        #Place fruit labels
        for i, fl in enumerate(self.fruitLabels):
            row, column = divmod(i, self.columns)

            fl.grid(row=row, column=column, padx=5, pady=5)

            self.bindChildrenToButton1(fl)

            fl.update_idletasks()

        #Create dummy button
        self.button = tk.Button(self, text="Add Fruit", bg=SBG, activebackground=ACTIVEBG, fg="white", padx=25)
        self.button.grid(row=1000, column=0, sticky=tk.S+tk.W, padx=5, pady=3)

        self.normalizeLabelSize()

        #Start loop
        self.mainLoop()


    def mainLoop(self):
        self.bindAllToScrollWheel(self)
        self.after(100, self.mainLoop)

    
    def normalizeLabelSize(self):
        #Figure out fruit label with most width
        maxWidth = int()
        for fl in self.fruitLabels:
            if fl.winfo_width() > maxWidth:
                maxWidth = fl.winfo_width()

        #Change all fruit labels to have width of maxWidth
        for fl in self.fruitLabels:
            fl.config(padx=(maxWidth-fl.winfo_width())/2)

        #Change height of fruit label based on tallest fruit label in row
        for i in range(0, len(self.fruitLabels), self.columns):
            rowLabels = self.fruitLabels[i:i+self.columns]
            maxHeight = int()

            #Find tallest label in row
            for fl in rowLabels:
                if fl.winfo_height() > maxHeight:
                    maxHeight = fl.winfo_height()
            
            #Configure label height
            for fl in rowLabels:
                fl.config(pady=(maxHeight-fl.winfo_height())/2)


    def bindChildrenToButton1(self, parent):
        for child in parent.winfo_children():
            self.bindChildrenToButton1(child)
        parent.bind("<Button-1>", self.onButton1Click)

    def changeFrameColor(self, frame, color):
        if not frame == None:
            for child in frame.winfo_children():
                self.changeFrameColor(child, color)
            frame.config(bg=color)

    def onButton1Click(self, event):
        widgetClicked = event.widget
        fl = widgetClicked

        if isinstance(widgetClicked, tk.Label):
            fl = widgetClicked.winfo_parent()
            fl = self.nametowidget(fl)

        #Deselect previous frame
        if not self.selectedFrame == None:
            self.changeFrameColor(self.selectedFrame, FLBG)
            self.checkbox.pack_forget()

        #If clicked on already selected frame, set selected frame to None
        if self.selectedFrame is fl:
            self.selectedFrame = None

        else:
            #Update selected frame
            self.selectedFrame = fl

            self.changeFrameColor(self.selectedFrame, SELECTEDBG)

            self.checkbox = tk.Checkbutton(self.selectedFrame, text="Perm?", selectcolor="white", fg="black", bg=SELECTEDBG, activebackground=SELECTEDBG, variable=self.permanent)
            self.checkbox.pack()


    def bindAllToScrollWheel(self, parent):
        #Recursively bind all widgets in parent to scroll wheel
        for widget in parent.winfo_children():
            self.bindAllToScrollWheel(widget)
        self.bind_scroll_wheel(parent)

    def getFruit(self):
        fruitName = self.selectedFrame.winfo_children()[1].cget("text")
        permanent = self.permanent.get()

        return bloxfruit(fruitName, permanent=permanent)
    















class InventoryManager(tk.Toplevel):
    def __init__(self, master, inventoryColumns=10,**kw):
        super().__init__(master=master, **kw)

        #Configure window
        self.config(bg=BG)

        self.iconbitmap("assets/kitsune.ico")
        self.title("Manage inventory")

        self.fruitLabels = list()
        self.removeButtons = list()
        self.inventoryColumns = inventoryColumns
        self.fruitSelectorOpen = False
        self.removeModeEnabled = False

        #Get inventory from config
        self.inventory = getConfig("INVENTORY")
        #Deserialize fruit data
        for i, fruitData in enumerate(self.inventory):
            self.inventory[i] = fruitFromSerialized(fruitData)

        self.inventory.sort(reverse=True)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        #Create frame for inventory
        self.inventoryFrame = tk.Frame(self, bg=BG)
        self.inventoryFrame.grid(row=1, column=0)

        #Create label for when inventory is empty
        self.emptyLabel = tk.Label(self.inventoryFrame, text="Your inventory is empty", font=("Cascadia Code", 24), bg=BG, fg="white", border=0)

        #Create top bar
        self.topbar = tk.Frame(self, relief="sunken", borderwidth=2, bg=SBG)
        self.topbar.grid(row=0, column=0, sticky=tk.W+tk.E)

        #Create label for inventory value
        self.valueLabel = tk.Label(self.topbar, bg=BG, text="Value: ", anchor=tk.E, fg="white", padx=5, width=25)
        self.valueLabel.pack(side=tk.RIGHT)

        self.addFruitButton = tk.Button(self.topbar, bg=BG, activebackground=ACTIVEBG, text="Add Fruit", padx=25, fg="white", command=self.toggleFruitSelector)
        self.addFruitButton.pack(side=tk.LEFT, padx=5)

        self.removeFruitButton = tk.Button(self.topbar, bg=BG, activebackground=ACTIVEBG, text="Remove Fruit", padx=25, fg="white", command=self.toggleRemoveMode)
        self.removeFruitButton.pack(side=tk.LEFT, padx=5)

        #Create the fruit selector frame but dont display it
        self.fruitSelectorFrame = tk.Frame(self, bg=BG, relief="solid", borderwidth=2)
        
        self.fruitSelector = FruitSelector(self.fruitSelectorFrame, picWidth=75, picHeight=75, scrollbars="vertical", columns=4, width=400)
        self.fruitSelector.pack(side=tk.TOP)

        #Configure dummy button
        self.fruitSelector.button.config(command=self.addFruit)

        self.updateInventoryLabels()
        self.updateInventoryValue()


    def toggleFruitSelector(self):
        #Disable remove mod
        if self.removeModeEnabled:
            self.toggleRemoveMode()


        if not self.fruitSelectorOpen:
            self.fruitSelectorOpen = True
            
            #Deselect any previously selected frame
            try:
                self.fruitSelector.changeFrameColor(self.fruitSelector.selectedFrame, FLBG)
                self.fruitSelector.checkbox.pack_forget()
                self.fruitSelector.selectedFrame = None
            except:
                #This runs if no frame was previously selected
                pass
                
            self.fruitSelectorFrame.grid(row=1,column=0, sticky=tk.N+tk.W)

        else:
            self.fruitSelectorOpen = False
            self.fruitSelectorFrame.grid_forget()
    

    def toggleRemoveMode(self):
        #Disable fruit selector
        if self.fruitSelectorOpen:
            self.toggleFruitSelector()

        
        if not self.removeModeEnabled:
            self.removeModeEnabled = True

            for i, fl in enumerate(self.fruitLabels):
                #Create button with the corresponding fruit label index as command argument
                rb = tk.Button(fl, text="X", fg="red", command=lambda i=i:self.removeFruit(i))
                rb.pack()
                self.removeButtons.append(rb)

        else:
            self.removeModeEnabled = False
            #Delete all remove buttons
            for rb in self.removeButtons:
                rb.destroy()
            self.removeButtons.clear()

            self.updateInventoryLabels()


    def addFruit(self):
        selectedFruit = self.fruitSelector.getFruit()
        self.inventory.append(selectedFruit)

        self.updateInventoryLabels()

        self.updateInventoryValue()
    

    def removeFruit(self, i):
        fl = self.fruitLabels[i]
        fl.destroy()
        self.fruitLabels.pop(i)
        self.inventory.pop(i)
        self.removeButtons.pop(i)

        #Update remove button indexes
        for i, fl in enumerate(self.fruitLabels):
            self.removeButtons[i].config(command=lambda i=i:self.removeFruit(i))

        self.updateInventoryValue()


    def clearFruitLabels(self):
        for fl in self.fruitLabels:
            fl.destroy()
        self.fruitLabels.clear()


    def updateInventoryLabels(self):
        self.inventory.sort(reverse=True)

        if len(self.inventory) == 0:
            self.clearFruitLabels()
            self.emptyLabel.grid(row=0, column=0,sticky=tk.W+tk.E)

        else:
            self.clearFruitLabels()
            self.emptyLabel.grid_forget()

            for fruit in self.inventory:
                self.fruitLabels.append(fruitLabel(self.inventoryFrame, fruit.name, permanent=fruit.permanent, usePrice=False))

            for i, fl in enumerate(self.fruitLabels):
                row, column = divmod(i, self.inventoryColumns)
                fl.grid(row=row, column=column, padx=7, pady=7)

            self.normalizeLabelSize()

            if self.winfo_reqheight() > self.winfo_height():
                self.geometry(str(self.winfo_width())+"x"+str(self.winfo_reqheight()))
    

    def normalizeLabelSize(self):
        #Figure out fruit label with most width
        maxWidth = int()
        for fl in self.fruitLabels:
            fl.update_idletasks()
            if fl.winfo_width() > maxWidth:
                maxWidth = fl.winfo_width()

        #Change all fruit labels to have width of maxWidth
        for fl in self.fruitLabels:
            fl.config(padx=(maxWidth-fl.winfo_width())/2)

        #Change height of fruit label based on tallest fruit label in row
        for i in range(0, len(self.fruitLabels), self.inventoryColumns):
            rowLabels = self.fruitLabels[i:i+self.inventoryColumns]
            maxHeight = int()

            #Find tallest label in row
            for fl in rowLabels:
                if fl.winfo_height() > maxHeight:
                    maxHeight = fl.winfo_height()
            
            #Configure label height
            for fl in rowLabels:
                fl.config(pady=(maxHeight-fl.winfo_height())/2)


    def saveInventory(self):
        serializedFruits = list()

        for fruit in self.inventory:
            serializedFruits.append(fruit.serialize())

        changeConfig("INVENTORY", serializedFruits)

    
    def updateInventoryValue(self):
        value = int()
        for fruit in self.inventory:
            value += fruit.getValue()
        
        self.valueLabel.config(text="Value: $"+f'{value:,}')


    #Override the destroy method of Toplevel
    def destroy(self):
        savedInventory = getConfig("INVENTORY")
        #Deserialize fruit data
        for i, fruitData in enumerate(savedInventory):
            savedInventory[i] = fruitFromSerialized(fruitData)

        if not savedInventory == self.inventory:
            answer = tkmessagebox.askyesno("Save inventory?", "Do you want to save the changes you made to your inventory?")
            if answer:
                self.saveInventory()

        super().destroy()