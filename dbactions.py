from pymongo import MongoClient
from classes import *
import json
from typing import List

def get_database():
  
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient('localhost', 27017)
 
   # Create the database for our example (we will use the same database throughout the tutorial
   return client['bpf']
   
   
def insertMetadata(metadata: Metadata):
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(metadata.dict())
    return("Hello World")
    
def getAllRessourcesFromDb():
    dbname = get_database()
    collection = dbname['bpf']
    r=list(collection.find())
    print(r)
    return(r)        
    
def getRessourceFromDb(id):
    print(id)
    dbname = get_database()
    collection = dbname['bpf']
    r=collection.find({"id" : id })
    print("search done")
    print(r[0])
    return(r[0])