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

stockFrame = StockFrame(root, relief="solid", scrollbars="vertical", width=200)
stockFrame.grid(column=0, row=0, sticky=tk.N + tk.W + tk.S)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

root.update_idletasks()
root.mainloop()