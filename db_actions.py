#pylint: disable=C0301,E1101,W0603,W0612,W0613,C0116,C0303
"""
This module contains all functions that contain database actions, like
creating new records, reading from the DB etc.

There should be no business logic here.
"""

import json
import os
from nanoid import generate
from pymongo import MongoClient
from beanie import init_beanie
import motor.motor_asyncio

import classes
#import person_relations



MONGO_CLIENT=None

@classes.async_func_logger
async def initialise_beanie():
    mongo_db_database_name = "bpf"
    mongo_host = os.getenv('MONGODB_HOST', '')
    endpoint = f"mongodb://{mongo_host}"
    motor_client = motor.motor_asyncio.AsyncIOMotorClient(endpoint)
    database = motor_client[mongo_db_database_name]
    await init_beanie(database=database, document_models=[\
                                                        classes.Node,\
                                                        classes.Edge, \
                                                        classes.Graph, \
                                                        classes.Union,\
                                                        classes.WebCall,\
                                                        ])

@classes.func_logger
def get_database():
    """
    Method to get the database connection
    """
    global MONGO_CLIENT
    if bool(MONGO_CLIENT):
        return MONGO_CLIENT['bpf']
    mongo_host = os.getenv('MONGODB_HOST', '')
    print("host",mongo_host)
    print(os.getenv('MONGODB_PORT', ''))
    mongo_port = int(os.getenv('MONGODB_PORT', ''))
    print("port",mongo_port)
    endpoint = f"mongodb://{mongo_host}"
    print("endpoint",endpoint)
    MONGO_CLIENT = MongoClient(host=endpoint,port=mongo_port,connectTimeoutMS=1000,timeoutMS=1200)
    print(MONGO_CLIENT)
    print("databases",MONGO_CLIENT.list_database_names())
#    await init_beanie(database=mongo_client.bpf, document_models=[classes.Metadata,classes.Person,classes.OrganisationDb,classes.BookDb])
    return MONGO_CLIENT['bpf']
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    # client = MongoClient('localhost', 27017)
    # Create the database for our example (we will use the same database throughout the tutorial
#   return client['bpf']

# @classes.func_logger
# async def insert_atom(atom):
#     await atom.insert()
#     return 

# @classes.func_logger
# def insert_metadata(metadata: classes.Metadata):
#     """
#     Method to create a metadata record
#     """
#     print("Inserting metadata in database")
#     dbname = get_database()
#     collection=dbname['bpf']
#     collection.insert_one(metadata.dict())
#     return "Hello World"

@classes.async_func_logger
async def get_all_resources_from_db():
    """
    Method to get all ressources from the database
    """
#    print("Getting all ressources from the database")
#    dbname = get_database()
#    print("Database name:",dbname)
#    print(".")
#    collection = dbname['bpf']
# the next line is not working for me :-(
#    r=list(collection.find({"type" : { "$in" : ["Manuscript", "Book", "Manifest"]}}, {"id": 1, "type" : 1, "preview" : 1}))
#    r=list(collection.find())
#    books = classes.BookDb.find()
    records = await classes.Union.find().to_list()
    print(records)
#    print(r)
#    r = await books.to_list()
    return records

# @classes.func_logger
# def get_resource_from_db(identifier):
#     """
#     Method to get a single record from the database given its id
#     """
#     print(identifier)
#     dbname = get_database()
#     collection = dbname['bpf']
#     r=collection.find({"id" : identifier })
#     print("search done")
#     print(r[0])
# #    for rr in r:
# #        print(rr)
#     return r[0]

@classes.func_logger
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

#@classes.async_func_logger
#async def insert_record_person(person: classes.Person):
#    """
#This function inserts a newly created record for a person into the database
#It was made for persons connected to books but probably can be used for any person
#    """
#    print("Inserting person metadata in database")
#    dbname = get_database()
#    collection=dbname['bpf']
#    collection.insert_one(person.dict())
#    await person.insert()
#    return "Hello World"

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

@classes.func_logger
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
    return result

@classes.func_logger
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
    return result
@classes.func_logger

def add_person_type(person_id, person_type1):
    """
This function is used to add another person type (e.g., Author, Artist etc.) to a person record
    """
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : person_id}, {'$addToSet' : {"person_type1" : person_type1}})
    return result

@classes.func_logger
def add_organisation_type(organisation_id, organisation_type1):
    """
This function is used to add another person type (e.g., Author, Artist etc.) to a person record
    """
    dbname = get_database()
    collection=dbname['bpf']
    result = collection.update_one({"id" : organisation_id}, {'$addToSet' : {"org_type1" : organisation_type1}})



@classes.func_logger
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

# @classes.func_logger
# async def insert_record_organisation(organisation: classes.OrganisationDb):
#     """
# This function inserts a newly created record for an organisation into the database
# It was made for organisations connected to books but probably can be used for any organisation
#     """
#     print("Inserting metadata in database")
# #    dbname = get_database()
# #    collection=dbname['bpf']
# #    collection.insert_one(organisation.dict())
#     await organisation.insert()
#     return "Hello World"


# @classes.func_logger
# async def insert_record_place(place: classes.PlaceDb):
#     """
# This function inserts a newly created record for a place into the database
# It was made for places connected to books but probably can be used for any place
#     """
#     print("Inserting place metadata in database")
# #    print(place)
# #    print(type(place))
# #    print("dumping")
# #    print (place.model_dump())
#     await place.insert()
# #    dbname = get_database()
# #    collection=dbname['bpf']
# #    collection.insert_one(place.dict())
#     return "Hello World"


# @classes.func_logger
# def insert_record_manuscript(manuscript : classes.ManuscriptDb):
#     """
#     \todo
#     """
#     print("Inserting metadata in database")
#     dbname = get_database()
#     collection=dbname['bpf']
#     collection.insert_one(manuscript.dict())
#     return "Hello World"

# @classes.func_logger
# async def insert_record_book(book : classes.BookDb):
#     """
#     \todo
#     """
#     print("Inserting book metadata in database")
# #    dbname = get_database()
# #    collection=dbname['bpf']
# #    collection.insert_one(book.dict())
#     await book.insert()
#     return "Hello World"

# @classes.async_func_logger
# async def insert_record_pages(pages : classes.PagesDb):
#     """
#     \todo
#     """
#     print("Inserting pages metadata in database")
# #    dbname = get_database()
# #    collection=dbname['bpf']
# #    collection.insert_one(pages.dict())
#     await pages.insert()
#     return "Hello World"

@classes.func_logger
def create_image_record():
    """
    \todo
    """
    print("Creating an image record in the database")
    dbname = get_database()
    collection=dbname['bpf']

@classes.async_func_logger
async def find_person(search_string: str, search_parameter: str):
    """
\todo
    """
    search_result = None
    match search_parameter: 
        case "name":
            search_result=classes.Node.find( classes.Node.name==search_string and
                                             classes.Node.type=="Person" )
        case "external_id":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
#            search_result = await classes.Entity.find_one(classes.Entity.external_id.id == person.id 
#                                            and classes.Entity.external_id.name == person.name)
#                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_locations" : 1})
        case "name_preferred":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = await classes.Person.find(classes.Person.name_preferred == person.name)
#            search_result = collection.find({"name_preferred" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1})
        case "name_variant":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = collection.find({"name_variant" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1})
        case "GND":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": person.new_authority_id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
        case "external_id_ingest":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
        case "external_id_connected_organisation":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_organisations" : 1})
        case "external_id_connected_location":
            classes.logger.info("   ---    NOT IMPLEMENTED   ---   ")
#        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.name, "id": person.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_locations" : 1})
    print(search_result)
 #   if person_found:
#        print("ID "+person_found.id+" NAME "+person_found.name_preferred)
    return await search_result.to_list()

@classes.func_logger
def find_organisation(organisation: classes.Node, parameter: str):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    organisation_found = classes.Node
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

@classes.func_logger
def find_place(place: classes.Node, parameter: str):
    """
\todo
    """
    dbname = get_database()
    collection = dbname['bpf']
    place_found = classes.PlaceDb
    if parameter=="external_id":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.id_name, "id": place.id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
    if parameter=="name_preferred":
        place_found = collection.find({"name_preferred" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1})
    if parameter=="name_variant":
        place_found = collection.find(
            {"name_variant" : place.name}, 
            {"id": 1, "name_preferred" : 1, "place_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
    if parameter=="GND":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": place.new_authority_id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
    if parameter=="external_id_ingest":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.name, "id": place.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
    if parameter=="external_id_connected_organisations":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.name, "id": place.id}}}, {"id": 1, "name_preferred" : 1, "connected_organisations" : 1})
    if parameter=="external_id_connected_locations":
        place_found = collection.find_one({"external_id": {"$elemMatch": {"name": place.name, "id": place.id}}}, {"id": 1, "name_preferred" : 1, "connected_locations" : 1})

    return place_found


@classes.func_logger
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

@classes.func_logger
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

@classes.func_logger
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


# @classes.func_logger
# def add_relationship_in_far_record(record_found: classes.Person , record_new, record_new_type, connected_entity_connection_type, connected_entity_connection_time, connected_entity_connection_comment):
#     """
# \todo Name should be somehing like "link records"

# This module is used for the 'stitching' together of records; it checks, if an already extant record 
# ('far record') already has a connection with the new record.
# If so, it adds the ID of the new record to the connection; if no, it creates a new connection from 
# scratch
# record_found is the record that will receive the reciprocal connection, record_new is the newly created
#  record, record_new_type indicates, if the connection has to be inserted
# under "connected_persons", "connected_organisations", or "connected_locations".
# If the 'far record' has better information on the type of connection, its time, or comments, these 
# fields returned to the main module. 
#     """
#     expected_connection_type = ""
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("step 2: arrived in add_relationship_in_far_record")
#     print("record_found:")
#     #print(record_found)
#     print("record_new:" )
#     #print(record_new)
#     print("connected_person_connection_type: ")
#     print(connected_entity_connection_type)
#     print("connected_entity_connection_time: ")
#     print(connected_entity_connection_time)
#     connection_correction = ""
#     time_correction = ""
#     comment_correction = ""
#     if record_found: # this is for making the reciprocal connection
#         far_record = record_found[record_new_type]
#         print("record_new_type")
#         print(record_new_type)
#         connection_found = False
#         connection_type_for_insert = ""
#         connection_time_for_insert = ""
#         connection_comment_for_insert = ""

#         if "sex" in record_found:
#             connection_sex = record_found["sex"]
#         else:
#             connection_sex = ""
#         if hasattr(record_new, "sex"):
#             connection_backwards_sex = record_new.sex
#         else:
#             connection_backwards_sex = ""
#         expected_connection_type = person_relations.relation_correspondence(connected_entity_connection_type, connection_sex)
#         print("extant connection type: ")
#         print(connected_entity_connection_type)
#         print("expected_connection_type:")
#         print(expected_connection_type)
#         # Sometimes, one and the same person appears twice, in different relations. If one relation had just been inserted, it should have the reciprocal connection type - hopefully
#         vague_connection = ["professional relation to", "related to", "other relationship to", "affiliated to"] # this are very general terms of connections that are to be replaced by more precise ones, if possible

#         for far_entity in far_record:
#             for far_external_id in far_entity["external_id"]:
#                 for external_id_number in range(len(record_new.external_id)):
#                     if far_external_id["uri"] == record_new.external_id[external_id_number].uri:
#                         if far_entity["connection_type"] == expected_connection_type:
#                             connection_type_to_be_searched = expected_connection_type
#                             connection_type_for_insert = far_entity["connection_type"]
#                             connection_found = True
#                             break
#                         else:
#                             if far_entity["connection_type"] in vague_connection:
#                                 connection_type_for_insert = expected_connection_type
#                                 print("far connection type was vague and is to be replaced with: ")
#                                 print(connection_type_for_insert)
#                                 connection_type_to_be_searched = expected_connection_type
#                                 connection_found = True
#                                 break
#                             elif expected_connection_type in vague_connection:
#                                 connection_correction = person_relations.relation_correspondence(far_entity["connection_type"], connection_backwards_sex)
#                                 print("connection in new record too vague, sending back correction: ")
#                                 print(connection_correction)
#                                 connection_type_to_be_searched = far_entity["connection_type"]
#                                 connection_type_for_insert = far_entity["connection_type"]
#                                 connection_found = True
#                                 break

#             if connection_found:
#                 print("step 2a: connection found, new ID and name added to it")
#                 # This is step 2a: there is already a connection, to which the ID of the new record is added
# #                                print("found record for inserting reciprocal ID")
#                 far_entity["id"] = record_new.id
#                 if connected_entity_connection_time != "" and far_entity["connection_time"] == "": # this means that the new record gives a connection time, the old record doesn't.
#                     connection_time_for_insert = connected_entity_connection_time
#                     print("connection_time_for_insert")
#                     print(connection_time_for_insert)
#                 elif far_entity["connection_time"] != "" and connected_entity_connection_time == "": # this means that the old record has a conneciton time, the new one not
#                     print("connection_time sent to new record")
#                     time_correction = far_entity["connection_time"]
#                 else:
#                     print("no connection time for insert in either direction")
#                 if connected_entity_connection_comment != "" and far_entity["connection_comment"] == "": # this means that the new record gives a connection time, the old record doesn't.
#                     connection_comment_for_insert = connected_entity_connection_comment
#                     print("connection_comment_for_insert")
#                     print(connection_comment_for_insert)
#                 elif far_entity["connection_comment"] != "" and connected_entity_connection_comment == "": #this means that the old record has comments, the new one not
#                     print("connection_comment sent to new record")
#                     comment_correction = far_entity["connection_comment"]
#                 else:
#                     print("no connection time for insert either way")
# #                        dbactions.add_connection_id(record_found["id"], record_new_type, far_entity["name"], far_entity["id"])
#                 add_connection_id_and_name(record_found["id"], record_new_type, connection_type_to_be_searched, far_entity["name"], record_new.name_preferred, record_new.id, connection_type_for_insert, connection_time_for_insert, connection_comment_for_insert)
#                 connection_found = True
#                 break
# #                        print("The connected record has a reciprocal connection to which merely the new ID has to be added")
#         if connection_found is False:
#             print("step 2b: no connection found, new connection added")
#             # This is step 2b: there is no reciprocal connection, it needs to be established
# #                        print("For person " + person_found["name_preferred"] + " no connection has been found")
#             new_connection = classes.EntityConnection()
#             new_connection.id = record_new.id
#             new_connection.external_id = record_new.external_id
#             new_connection.name = record_new.name_preferred # better use preview including year
#             new_connection.connection_type = expected_connection_type
#             new_connection.connection_time = connected_entity_connection_time
# #            new_connection.connection_type = person_relations.relation_correspondence(connected_person_connection_type, person_found["sex"])
#             # I need a separate formular, without 'sex', for orgs and places
# #                        new_connection.connection_type = "1counterpart to " + connected_person.connection_type # This has to be replaced by a proper term
#             add_connection(record_found["id"], record_new_type, new_connection)
#         print("Values to be returned from add_relationship_in_other_record")
#         print("connection_correction: ")
#         print(connection_correction)
#         print(type(connection_correction))
#         print("time_correction")
#         print(time_correction)
#         print(type(time_correction))
#         print("comment_correction: ")
#         print(comment_correction)
#         print(type(comment_correction))
#     return connection_correction, time_correction, comment_correction


@classes.async_func_logger
async def save_person(p):
#    p.id= generate()
    if p.type == "Person":
        r = await p.save()
    else:
        r="ERROR"
    return r

@classes.async_func_logger
async def save_person_and_connections():

    pass


def make_new_role(role,person_name):
    r=classes.Node()
    if person_name:
        r.name=person_name
    a=classes.Attribute()
    a.key="role"
    a.value=role
    r.attributes.append(a)
    a=classes.Attribute()
    a.key="chosen_candidate"
    a.value=-1
    r.attributes.append(a)
    return r
