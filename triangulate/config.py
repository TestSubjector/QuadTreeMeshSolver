import json

def getConfig():
    with open("..\config.json","r") as f:
        config = json.load(f)
    return config