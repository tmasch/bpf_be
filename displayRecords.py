# This module contains functions for displaying (and later perhaps also editing) records from the database

import db_actions
from classes import *

def getBookRecord(id):
    # this function displays all elements links to a printed book record
    dbname = db_actions.get_database()
    collection=dbname['bpf']
    result = collection.find_one({"id": id})
    if result["persons"]:
        for person in result["persons"]:
            id = person["id"]
            person_record = collection.find_one({"id" : id}, {"name_preferred" : 1})
            person["preview"] = person_record["name_preferred"]
    if result["organisations"]:
        for organisation in result["organisations"]:
            id = organisation["id"]
            organisation_record = collection.find_one({"id" : id}, {"name_preferred" : 1})
            organisation["preview"] = organisation_record["name_preferred"]
    if result["places"]:
        for place in result["places"]:
            id = place["id"]
            place_record = collection.find_one({"id" : id}, {"name_preferred" : 1})
            place["preview"] = place_record["name_preferred"]
    print("result form search in database: ")
    print(result)
    return result

def getManuscriptRecord(id):
    # this function displays all elements links to a printed book record
    dbname = db_actions.get_database()
    collection=dbname['bpf']
    result = collection.find_one({"id": id})
    if result["repository"]:
        for repository in result["repository"]:
            id = repository["place_id"]
            repository_record = collection.find_one({"id" : id}, {"name_preferred" : 1})
            repository["preview"] = repository_record["name_preferred"]
    print("result form search in database: ")
    print(result)
    return result


def getRecord(id):
    # this function downloads a record with a given ID from the database
    dbname = db_actions.get_database()
    collection=dbname['bpf']
    result = collection.find_one({"id": id})
    #pipeline = [{"$match" :{"id" : id}}]  #, {"$lookup" :{"from": collection, "local_field": "connected_persons.id", "foreign_field": "id", "as":"connected_persons_details"}}]
    #results = collection.aggregate(pipeline)
#    for record in results: 
#        print("Here is record from PyMongo: ")
#        print(record)
    return(result)