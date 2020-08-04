import pymongo
from pymongo import MongoClient
import json

with open('config.json') as config_file:
    data = json.load(config_file)

cluster = MongoClient("mongodb+srv://{user}:{password}@eugenemongo.ibdxz.mongodb.net/translationbot?retryWrites=true&w=majority".format(user = data['DBUSER'], password = data['DBPASSWORD']))
db = cluster["TranslationBot"]
collection = db["translationbot"]

def insertNewUser(user, inputLanguage, translate):
    if findUser(user).count()==0:
        lastInsertedId = 0
        if(collection.find().sort('_id', pymongo.DESCENDING).limit(1).count()>0):
            lastInsertedId = collection.find().sort('_id', pymongo.DESCENDING).limit(1)[0]['_id'];
            lastInsertedId+=1
        post = {"_id": lastInsertedId, "user_id": user, "inputLanguage": inputLanguage, "TranslatedOutput": translate}
        collection.insert(post)
        return True
    else:
        return False

def findUser(user):
    return collection.find({"user_id": user})

def updateUser(user, translate, isTranslate):
    if isTranslate == True:
        collection.update_one({"user_id":user}, {"$set":{"TranslatedOutput":translate}})
    else:
        collection.update_one({"user_id":user}, {"$set":{"inputLanguage":translate}})

def getUserDefaultLanguage(user):
    if(collection.find({"user_id": user}).count()>0):
        return collection.find({"user_id": user})[0]['TranslatedOutput']
    else:
        insertNewUser(user, "en", "es")
        return "spanish"

def getUserDefaultInputLanguage(user):
    if(collection.find({"user_id": user}).count()>0):
        return collection.find({"user_id": user})[0]['inputLanguage']
    else:
        insertNewUser(user, "en", "es")
        return "english"
