import json

FILEDIR = "data/config.json"

def changeConfig(config, newValue):
    with open(FILEDIR) as f:
        CONFIGS = json.loads(f.read())
    
    CONFIGS[config] = newValue

    with open(FILEDIR, "w") as f:
        f.write(json.dumps(CONFIGS, indent=2))

def getConfig(config):
    with open(FILEDIR) as f:
        return json.loads(f.read())[config]
    
def RESTOREDEFAULTCONFIG():
    CONFIGS = dict()

    #SPECIAL ITEM NAMES (will replace first name with second in bloxfruit.py and main.py)
    CONFIGS["specialnames"] = [
        ["+1 fruit storage", "fruit storage"],
        ["2x boss drop chance", "2x boss drops"],
        ["1 fruit storage", "fruit storage"],
        ["5x legendary scrolls", "legendary scrolls"]
    ]

    #URLS
    CONFIGS["fruitdataurl"] = "https://blox-fruits.fandom.com/wiki/Blox_Fruits"
    CONFIGS["gamepassdataurl"] = "https://blox-fruits.fandom.com/wiki/Shop"

    CONFIGS["stockurl"] = "https://blox-fruits.fandom.com/wiki/Blox_Fruits_%22Stock%22"
    
    CONFIGS["tradesurl"] = "https://fruityblox.com/trading"
    CONFIGS["staticpfpsrc"] = "https://fruityblox.com/static/img/profile-pic.png"

    CONFIGS["valuesurl"] = "https://www.bloxfruitsvalues.com/"
    CONFIGS["valuesurlappends"] = ["common", "uncommon", "rare", "legendary", "mythical", "gamepass"]
    CONFIGS["gamepassvaluesurl"] = "https://www.bloxfruitsvalues.com/gamepass"

    CONFIGS["INVENTORY"] = []    
    CONFIGS["SAVEDTRADES"] = []

    with open(FILEDIR, "w") as f:
        f.write(json.dumps(CONFIGS, indent=2))