#pylint: disable=C0301
"""
This module contains all functions that contain database actions, like
creating new records, reading from the DB etc.

There should be no business logic here.
"""

import json
import os
#from typing import List
from nanoid import generate
from pymongo import MongoClient
from beanie import init_beanie
import motor.motor_asyncio
import classes




mongo_client=None

async def initialise_beanie():
    MONGO_DB_DATABASE_NAME = "bpf"
    mongo_host = os.getenv('MONGODB_HOST', '')
    mongo_port = int(os.getenv('MONGODB_PORT', ''))
    endpoint = 'mongodb://{0}'.format(mongo_host)
    MOTOR_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(endpoint)
    DATABASE = MOTOR_CLIENT[MONGO_DB_DATABASE_NAME]
    document_models = [classes.Metadata,classes.PersonDb,classes.OrganisationDb,classes.BookDb]
    await init_beanie(database=DATABASE, document_models=[classes.Metadata,\
                                                        classes.PersonDb,\
                                                        classes.OrganisationDb,\
                                                        classes.BookDb,\
                                                        classes.PlaceDb,\
                                                        classes.PagesDb])


def get_database():
    """
    Method to get the database connection
    """
    global mongo_client
    if bool(mongo_client):
        return mongo_client['bpf']
    mongo_host = os.getenv('MONGODB_HOST', '')
    print("host",mongo_host)
    print(os.getenv('MONGODB_PORT', ''))
    mongo_port = int(os.getenv('MONGODB_PORT', ''))
    print("port",mongo_port)
    endpoint = 'mongodb://{0}'.format(mongo_host)
    print("endpoint",endpoint)
    mongo_client = MongoClient(host=endpoint,port=mongo_port,connectTimeoutMS=1000,timeoutMS=1200)
    print(mongo_client)
    print("databases",mongo_client.list_database_names())
#    await init_beanie(database=mongo_client.bpf, document_models=[classes.Metadata,classes.PersonDb,classes.OrganisationDb,classes.BookDb])
    return mongo_client['bpf']
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    # client = MongoClient('localhost', 27017)
    # Create the database for our example (we will use the same database throughout the tutorial
#   return client['bpf']


def insert_metadata(metadata: classes.Metadata):
    """
    Method to create a metadata record
    """
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(metadata.dict())
    return "Hello World"

def get_all_resources_from_db():
    """
    Method to get all ressources from the database
    """
    print("Getting all ressources from the database")
    dbname = get_database()
    print("Database name:",dbname)
#    print(".")
    collection = dbname['bpf']
# the next line is not working for me :-(
#    r=list(collection.find({"type" : { "$in" : ["Manuscript", "Book", "Manifest"]}}, {"id": 1, "type" : 1, "preview" : 1}))
    r=list(collection.find())
    print(r)
    return r

def get_resource_from_db(identifier):
    """
    Method to get a single record from the database given its id
    """
    print(identifier)
    dbname = get_database()
    collection = dbname['bpf']
    r=collection.find({"id" : identifier })
    print("search done")
    print(r[0])
#    for rr in r:
#        print(rr)
    return r[0]

def update_image_with_frames(identifier,i,frames):
    """
    does something
    """
    dbname = get_database()
    collection = dbname['bpf']
    print(json.dumps([ob.__dict__ for ob in frames]))
    result = collection.update_one({"id" : identifier}, {'$set' : {"images."+str(i)+".frames" : [ob.__dict__ for ob in frames] }})
#json.dumps([ob.__dict__ for ob in frames])
    return result

def insert_record_person(person: classes.PersonDb):
    """
This function inserts a newly created record for a person into the database
It was made for persons connected to books but probably can be used for any person
    """
    print("Inserting person metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(person.dict())
    return "Hello World"

#def add_external_id(record_id, external_id):
    # I think that this is not needed and should be removed
    # This function is used to add another external ID (typically a VIAF ID) to a record that
    #  has an array for external IDs (currently Person, Organisation, Place)
#    dbname = get_database()
#    collection=dbname['bpf']
#    result = collection.update_one({"id" : record_id}, {'$addToSet' : {"external_id" : external_id}})

#def add_connection_id(record_id, connected_entity_type, name, new_internal_id):
# I replaced this everywhere (I hopeI with add_connection_id_and_name)
#    print("in dabactions - inserting new connection id")
    # This function is used to go to a specific record, find there a connected_person with a specific name, and add an internal ID to this connection
#    dbname = get_database()
#    collection=dbname['bpf']
#    mongo_term1 = connected_entity_type + ".name"
#    mongo_term2 = connected_entity_type + ".$.id"

    #result = collection.update_one({"id" : record_id, "connected_persons.name" : name},
    # {'$set' : {"connected_persons.$.id" : new_internal_id}})
    #result = collection.update_one({"id" : record_id, "connected_entity_type.name" : name},
    # {'$set' : {"connected_entity_type.$.id" : new_internal_id}})
#    result = collection.update_one({"id" : record_id, mongo_term1 : name},
# {'$set' : {mongo_term2 : new_internal_id}})

def add_connection_id_and_name(record_id, connected_entity_type, far_connection_type, name, name_replacement, new_internal_id, connection_type, connection_time, connection_comments):
    """
This function is used to go to a specific record, find there a connected_person with a specific name, and add an internal ID to this connection and replaces the name with the name connected to the internal ID
Later, the name connected to the internal ID should be a preview with dates
    """
    print("in dabactions - inserting new connection and name")
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
    #result = collection.update_one({"id" : record_id, "connected_entity_type.name" : name},
    # {'$set' : {"connected_entity_type.$.id" : new_internal_id, "connected_entity_type.$.name" : name_replacement}})
    #result = collection.update_one({"id" : record_id, mongo_term1 : name, mongo_term2 : far_connection_type},
    # {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id, mongo_term1 : name, mongo_term2 : far_connection_type},
    # {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id, mongo_term1 : name, mongo_term2 : far_connection_type},
    # {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id, "$and": [{mongo_term1 : name}, {mongo_term2 : far_connection_type}]},
    #  {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}})
    #result = collection.update_one({"id" : record_id},
    # {'$set' : {mongo_term3 : new_internal_id, mongo_term4 : name_replacement}},
    #  {'arrayFilters' : [{mongo_term2 : far_connection_type}, {mongo_term3 : new_internal_id}]}, upsert=False)
    #result = collection.update_one({"id" : "VzqhhOhKIDVYeNuZy56JR"},
    #  {"$set" : {"name_variant.$[filter]" : "Weimarb"}}, {"arrayFilters" : [{"filter" : "Grossgebauer, Philipp"}]})
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
    """
This function is used to go to a specific record that has not yet a reciprocal connection, and inserts it
    """
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
    """
This function is used to add another person type (e.g., Author, Artist etc.) to a person record
    """
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : person_id}, {'$addToSet' : {"person_type1" : person_type1}})

def insert_record_organisation(organisation: classes.OrganisationDb):
    """
This function inserts a newly created record for an organisation into the database
It was made for organisations connected to books but probably can be used for any organisation
    """
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(organisation.dict())
    return "Hello World"

def add_organisation_type(organisation_id, organisation_type1):
    """
This function is used to add another person type (e.g., Author, Artist etc.) to a person record
    """
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : organisation_id}, {'$addToSet' : {"org_type1" : organisation_type1}})

def insert_record_place(place: classes.PlaceDb):
    """
This function inserts a newly created record for a place into the database
It was made for places connected to books but probably can be used for any place
    """
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(place.dict())
    return "Hello World"

def copy_place_record(place_id, place_type):
    """
Different from person and organisation records, places only have one 'type', e.g. a person can be "author" and "depicted person"
but a place cannot be 'building' and 'town'. Town and region records exist in two versions, as 'historical' and as 'modern'
(e.g., a building is in the modern town of Istanbul in Province Istanbul, Turkey, 
a Scriptorium worked in the historical town of Constantinople in Thrace in the Byzantine Empire)
Hence, if a town is only catalogued as 'Town - modern' but has to be connected to a book record, the record has to be copied into a 'Town - historical'
One will manually have to change the affiliation of this record from modern provinces to historical regions, but this is something that can only be done
once I have an 'edit' view for authority records.
    """
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    place = collection.find_one({"id" : place_id})
    del place["_id"] # I have to remove the automatic id so that it can create a new one
    place["id"] = generate()
    place["place_type1"] = ["Place - historical"]
    collection.insert_one(place)
    return place_id


def insert_record_manuscript(manuscript : classes.ManuscriptDb):
    """
    \todo
    """
    print("Inserting metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(manuscript.dict())
    return "Hello World"

def insert_record_book(book : classes.BookDb):
    """
    \todo
    """
    print("Inserting book metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(book.dict())
    return "Hello World"

def insert_record_pages(pages : classes.PagesDb):
    """
    \todo
    """
    print("Inserting pages metadata in database")
    dbname = get_database()
    collection=dbname['bpf']
    collection.insert_one(pages.dict())
    return "Hello World"

def create_image_record():
    """
    \todo
    """
    print("Creating an image record in the database")
    dbname = get_database()
    collection=dbname['bpf']


def find_person(person: classes.Person, parameter: str):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    person = classes.Person()
    if parameter=="external_id":
        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.id_name, "id": person.id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
#                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_locations" : 1})
    elif parameter=="name_preferred":
        person_found = collection.find({"name_preferred" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1})
    elif parameter=="name_variant":
        person_found = collection.find({"name_variant" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1})
    elif parameter=="GND":
        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": person.new_authority_id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
    elif parameter=="external_id_ingest":
        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
    elif parameter=="external_id_connected_organisation":
        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_organisations" : 1})
    elif parameter=="external_id_connected_location":
        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_locations" : 1})

    return person_found


def find_organisation(organisation: classes.Organisation, parameter: str):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    organisation_found = classes.Organisation
    if parameter=="external_id":
        organisation_found = collection.find_one({"external_id": {"$elemMatch": {"name": organisation.id_name, "id": organisation.id}}}, {"id": 1, "name_preferred": 1, "org_type1": 1})
    if parameter=="external_id_ingest":
        organisation_found = collection.find_one({"external_id": {"$elemMatch": {"name": organisation.name, "id": organisation.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
    if parameter=="external_id_organisation":
        organisation_found = collection.find_one({"external_id": {"$elemMatch": {"name": organisation.name, "id": organisation.id}}}, {"id": 1, "name_preferred" : 1, "connected_organisations" : 1})
    if parameter=="name":
        organisation_found = collection.find({"name_preferred" : organisation.name}, {"id": 1, "name_preferred" : 1, "org_type1" : 1})
    if parameter=="name_variant":
        organisation_found = collection.find({"name_variant" : organisation.name}, {"id": 1, "name_preferred" : 1, "org_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
    if parameter=="GND":
        organisation_found = collection.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": organisation.new_authority_id}}}, {"id": 1, "name_preferred": 1, "org_type1" : 1})
    if parameter=="external_id_location":
        organisation_found = collection.find_one({"external_id": {"$elemMatch": {"name": organisation.name, "id": organisation.id}}}, {"id": 1, "name_preferred" : 1, "connected_locations" : 1})

    return organisation_found


def find_place(place: classes.Place, parameter: str):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    place_found = classes.Place
    if parameter=="external_id":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.id_name, "id": place.id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
    if parameter=="name_preferred":
        place_found = collection.find({"name_preferred" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1})
    if parameter=="name_variant":
        place_found = collection.find({"name_variant" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
    if parameter=="GND":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": place.new_authority_id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
    if parameter=="external_id_ingest":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.name, "id": place.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
    if parameter=="external_id_connected_organisations":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.name, "id": place.id}}}, {"id": 1, "name_preferred" : 1, "connected_organisations" : 1})
    if parameter=="external_id_connected_locations":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.name, "id": place.id}}}, {"id": 1, "name_preferred" : 1, "connected_locations" : 1})

    return place_found


def find_organisation_viaf(new_record_viaf_id,new_record_gnd_id):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    list_found = list(collection.find({ \
        "$or": [{"connected_organisations.external_id.name" : "viaf",\
        "connected_organisations.external_id.id" : new_record_viaf_id},\
        {"connected_organisations.external_id.name" : "GND",\
        "connected_organisations.external_id.id" : new_record_gnd_id}]},\
        {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_organisations" : 1}))
    return list_found

def find_person_viaf(new_record_viaf_id,new_record_gnd_id):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    list_found = list(collection.find({ \
        "$or": [{"connected_persons.external_id.name" : "viaf",\
        "connected_persons.external_id.id" : new_record_viaf_id},\
        {"connected_persons.external_id.name" : "GND",\
        "connected_persons.external_id.id" : new_record_gnd_id}]},\
        {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
    return list_found


def find_place_viaf(new_record_viaf_id,new_record_gnd_id):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    list_found = list(collection.find({ \
        "$or": [{"connected_locations.external_id.name" : "viaf",\
        "connected_locations.external_id.id" : new_record_viaf_id},\
        {"connected_locations.external_id.name" : "GND",\
        "connected_locations.external_id.id" : new_record_gnd_id}]},\
        {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_locations" : 1}))
    return list_found
