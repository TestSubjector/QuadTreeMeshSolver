import json
import redis
import uuid
import jsonpickle
import marshal
import pickle

def getConfig():
    with open("config.json","r") as f:
        config = json.load(f)
    return config

conn = redis.Redis(getConfig()["global"]["redis"]["host"],getConfig()["global"]["redis"]["port"],getConfig()["global"]["redis"]["db"],getConfig()["global"]["redis"]["password"])

def setKeyVal(keyitm,keyval):
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    if PREFIX == "NONE":
        setPrefix()
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    conn.set(PREFIX + "_" + str(keyitm),json.dumps({keyitm: keyval}))
    return True

def getKeyVal(keyitm):
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    if PREFIX == "NONE":
        setPrefix()
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    try:
        result = dict(json.loads(conn.get(PREFIX + "_" + str(keyitm))))
        return result.get(keyitm)
    except TypeError:
        return None

def setPrefix():
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    if PREFIX == "NONE":
        conn = redis.Redis(getConfig()["global"]["redis"]["host"],getConfig()["global"]["redis"]["port"],getConfig()["global"]["redis"]["db"],getConfig()["global"]["redis"]["password"])
        PREFIX = str(uuid.uuid4()).replace("-","")
        data = dict(load_obj("config"))
        data["global"]["redis"]["prefix"] = PREFIX
        save_obj(data,"config")

def save_obj(obj, name):
    with open(name + '.json', 'w') as f:
        json.dump(obj, f)

def load_obj(name):
    with open(name + '.json', 'r') as f:
        return json.load(f)

def save_obj_marshal(obj, name):
    with open(name + '.marshal', 'wb') as f:
        marshal.dump(obj, f)

def load_obj_marshal(name):
    with open(name + '.marshal', 'rb') as f:
        return marshal.load(f)

def save_obj_cpickle(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f,protocol=cPickle.HIGHEST_PROTOCOL)

def load_obj_cpickle(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)