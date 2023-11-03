from pymongo import MongoClient
from classes import *
import json
import os
from typing import List

client=None

def get_database():
    global client
    if bool(client):
        return client['bpf']
    host = os.getenv('MONGODB_HOST', '')
    print("host",host)
    print(os.getenv('MONGODB_PORT', ''))
    port = int(os.getenv('MONGODB_PORT', ''))
    print("port",port)
    endpoint = 'mongodb://{0}'.format(host)
    print("endpoint",endpoint)
    client = MongoClient(host=endpoint,port=port,connectTimeoutMS=1000,timeoutMS=1200)
    print(client)
    print("databases",client.list_database_names()) 
    return client['bpf']
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
#   client = MongoClient('localhost', 27017)
 
   # Create the database for our example (we will use the same database throughout the tutorial
#   return client['bpf']
   
   
def insertMetadata(metadata: Metadata):
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(metadata.dict())
    return("Hello World")
    
def getAllRessourcesFromDb():
    print("Getting all ressources from the database")
    dbname = get_database()
    print("Database name:",dbname)
#    print(".")
    collection = dbname['bpf']
    r=list(collection.find())
#    print(r)
    return(r)        
    
def getRessourceFromDb(id):
    print(id)
    dbname = get_database()
    collection = dbname['bpf']
    r=collection.find({"id" : id })
    print("search done")
#    print(r[0])
#    for rr in r:
#        print(rr)
    return(r[0])