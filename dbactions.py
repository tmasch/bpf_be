from pymongo import MongoClient
from classes import *
import json
import os
from typing import List
from nanoid import generate

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
# the next line is not working for me :-(
    r=list(collection.find({"type" : { "$in" : ["Manuscript", "Book", "Manifest"]}}, {"id": 1, "type" : 1, "preview" : 1}))
#    r=list(collection.find())
    print(r)
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

def updateImageWithFrames(id,i,frames):
    dbname = get_database()
    collection = dbname['bpf']
    print(json.dumps([ob.__dict__ for ob in frames]))
    result = collection.update_one({"id" : id}, {'$set' : {"images."+str(i)+".frames" : [ob.__dict__ for ob in frames] }})
#json.dumps([ob.__dict__ for ob in frames])

def insertRecordPerson(person: Person_db):
    # This function insserts a newly created record for a person into the database
    # It was made for persons connected to books but probably can be used for any person
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(person.dict())
    return("Hello World")


def add_person_type(person_id, person_type1):
    # This function is used to add another person type (e.g., Author, Artist etc.) to a person record
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : person_id}, {'$addToSet' : {"person_type1" : person_type1}})

def insertRecordOrganisation(organisation: Organisation_db):
    # This function inserts a newly created record for an organisation into the database
    # It was made for organisations connected to books but probably can be used for any organisation
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(organisation.dict())
    return("Hello World")

def add_organisation_type(organisation_id, organisation_type1):
    # This function is used to add another person type (e.g., Author, Artist etc.) to a person record
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : organisation_id}, {'$addToSet' : {"org_type1" : organisation_type1}})

def insertRecordPlace(place: Place_db):
    # This function inserts a newly created record for a place into the database
    # It was made for places connected to books but probably can be used for any place
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(place.dict())
    return("Hello World")

def copy_place_record(place_id, place_type):
    # Different from person and organisation records, places only have one 'type', e.g. a person can be "author" and "depicted person"
    # but a place cannot be 'building' and 'town'. Town and region records exist in two versions, as 'historical' and as 'modern'
    # (e.g., a building is in the modern town of Istanbul in Province Istanbul, Turkey, 
    # a Scriptorium worked in the historical town of Constantinople in Thrace in the Byzantine Empire)
    # Hence, if a town is only catalogued as 'Town - modern' but has to be connected to a book record, the record has to be copied into a 'Town - historical'
    # One will manually have to change the affiliation of this record from modern provinces to historical regions, but this is something that can only be done
    # once I have an 'edit' view for authority records.
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    place = collection.find_one({"id" : place_id})
    del place["_id"] # I have to remove the automatic id so that it can create a new one
    place["id"] = generate()
    place["place_type1"] = ["Place - historical"]
    collection.insert_one(place)
    return(place_id)


def insertRecordManuscript(manuscript : Manuscript_db):
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(manuscript.dict())
    return("Hello World")

def insertRecordBook(book : Book_db):
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(book.dict())
    return("Hello World")

def insertRecordPages(pages : Pages_db):
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(pages.dict())
    return("Hello World")

