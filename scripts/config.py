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