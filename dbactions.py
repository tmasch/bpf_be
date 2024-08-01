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

#def add_external_id(record_id, external_id):
    # I think that this is not needed and should be removed
    # This function is used to add another external ID (typically a VIAF ID) to a record that has an array for external IDs (currently Person, Organisation, Place)
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : record_id}, {'$addToSet' : {"external_id" : external_id}})

#def add_connection_id(record_id, connected_entity_type, name, new_internal_id):
# I replaced this everywhere (I hopeI with add_connection_id_and_name)
    print("in dabactions - inserting new connection id")
    # This function is used to go to a specific record, find there a connected_person with a specific name, and add an internal ID to this connection
    dbname = get_database()
    collection=dbname['bpf']
    mongo_term1 = connected_entity_type + ".name"
    mongo_term2 = connected_entity_type + ".$.id"

    #result = collection.update_one({"id" : record_id, "connected_persons.name" : name}, {'$set' : {"connected_persons.$.id" : new_internal_id}})
    #result = collection.update_one({"id" : record_id, "connected_entity_type.name" : name}, {'$set' : {"connected_entity_type.$.id" : new_internal_id}})
    result = collection.update_one({"id" : record_id, mongo_term1 : name}, {'$set' : {mongo_term2 : new_internal_id}})

def add_connection_id_and_name(record_id, connected_entity_type, far_connection_type, name, name_replacement, new_internal_id, connection_type, connection_time, connection_comments):
    print("in dabactions - inserting new connection and name")
    # This function is used to go to a specific record, find there a connected_person with a specific name, and add an internal ID to this connection and replaces the name with the name connected to the internal ID
    # Later, the name connected to the internal ID should be a preview with dates
    print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
    print("adding connection for: ")
    print(record_id)
    print(name)
    print(far_connection_type)
    print("added is: ")
    print(new_internal_id)
    dbname = get_database()
    collection=dbname['bpf']
    print("overwriting connection_type with: ")
    print(connection_type)
    old_record = collection.find_one({"id": record_id})
    print("far record before addition of new connection")
    print(old_record)

    #mongo_term1 = connected_entity_type + ".na
    #mongo_term2 = connected_entity_type + ".connection_type"
    #mongo_term3 = connected_entity_type + ".$.id"
    #mongo_term4 = connected_entity_type + ".$.name"
    #mongo_term1 = "$" + connected_entity_type
    #mongo_term2 = connected_entity_type + ".name"
    mongo_term1 = connected_entity_type + ".$[elem].id"
    mongo_term2 = connected_entity_type + ".$[elem].name"
    mongo_term3 = connected_entity_type + ".$[elem].connection_type"     
    mongo_term4 = connected_entity_type + ".$[elem].connection_comment" 
    mongo_term5 = connected_entity_type + ".$[elem].connection_time"

#    print(mongo_term1)
#    print(mongo_term2)
#    print(mongo_term3)
#    print(mongo_term4)
    #result = collection.update_one({"id" : record_id, "connected_entity_type.name" : name}, {'$set' : {"connected_entity_type.$.id" : new_internal_id, "connected_entity_type.$.name" : name_replacement}})
    #result = collection.update_one({"id" : record_id, mongo_term1 : name, mongo_term2 : far_connection_type}, {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id, mongo_term1 : name, mongo_term2 : far_connection_type}, {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id, mongo_term1 : name, mongo_term2 : far_connection_type}, {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id, "$and": [{mongo_term1 : name}, {mongo_term2 : far_connection_type}]}, {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id}, {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}}, {'arrayFilters' : [{mongo_term2 : far_connection_type}, {mongo_term3 : new_internal_id}]}, upsert=False)
    #result = collection.update_one({"id" : "VzqhhOhKIDVYeNuZy56JR"}, {"$set" : {"name_variant.$[filter]" : "Weimarb"}}, {"arrayFilters" : [{"filter" : "Grossgebauer, Philipp"}]})
    # This was an attempt to write a lop to do every field, but this is not necessary
    #result = collection.aggregate([{"$match" : {"id" : record_id}}, {"$project" : { "length" :  { "$cond" : { "if" : { "$isArray": mongo_term1 }, "then": { "$size": mongo_term1 }, "else" : 0}} } }])
    #array_length = result[0]["length"]
    #for x in range(array_length):
    #if connection_time == "": # This means, no time for connection is to be inserted - either because there is already one in the extant record, or because there is none in the new record
    #    if connection_comments == "": # ditto for comments
    #        result = collection.update_one({"id" : record_id}, {'$set' : {mongo_term1 : new_internal_id, mongo_term2 : name_replacement}}, upsert=False, array_filters = [{"elem.name" : name, "elem.connection_type" : far_connection_type}])
    #    else:             
    #        result = collection.update_one({"id" : record_id}, {'$set' : {mongo_term1 : new_internal_id, mongo_term2 : name_replacement, mongo_term3 : connection_comments}}, upsert=False, array_filters = [{"elem.name" : name, "elem.connection_type" : far_connection_type}])
    #else: 
    #    if connection_comment == "":
    #        result = collection.update_one({"id" : record_id}, {'$set' : {mongo_term1 : new_internal_id, mongo_term2 : name_replacement, mongo_term4 : connection_time}}, upsert=False, array_filters = [{"elem.name" : name, "elem.connection_type" : far_connection_type}])
    #    else: 
    #        result = collection.update_one({"id" : record_id}, {'$set' : {mongo_term1 : new_internal_id, mongo_term2 : name_replacement, mongo_term4 : connection_comments, mongo_term4 : connection_time}}, upsert=False, array_filters = [{"elem.name" : name, "elem.connection_type" : far_connection_type}])
    result = collection.update_one({"id" : record_id}, {'$set' : {mongo_term1 : new_internal_id, mongo_term2 : name_replacement, mongo_term3 : connection_type, mongo_term4 : connection_comments, mongo_term5 : connection_time}}, upsert=False, array_filters = [{"elem.name" : name, "elem.connection_type" : far_connection_type}])
    changed_record = collection.find_one({"id": record_id})
    print("far record after addition of new connection")
    print(changed_record)
    return

def add_connection(record_id, connected_entity_type, new_connection):
    # This function is used to go to a specific record that has not yet a reciprocal connection, and inserts it
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print("The following connection will be added to record" + record_id)
    print(new_connection)
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : record_id}, {'$addToSet' : {connected_entity_type : new_connection.dict()}})
    record = collection.find_one({"id" : record_id})
    print("far record after addition of new connection")
    print(record)
    return

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

