#pylint: disable=C0301
"""
This module contains functions for displaying (and later perhaps also editing) records from the database
"""
import db_actions
import classes

@classes.async_func_logger
async def get_book_record(identifier):
    """
This function displays all elements links to a printed book record
    """
    print("searching with id: "+identifier)
    result =  await classes.BookDb.get(identifier,fetch_links=True)
    # if result["persons"]:
    #     for person in result["persons"]:
    #         identifier = person["id"]
    #         person_record = collection.find_one({"id" : identifier}, {"name_preferred" : 1})
    #         person["preview"] = person_record["name_preferred"]
    # if result["organisations"]:
    #     for organisation in result["organisations"]:
    #         identifier = organisation["id"]
    #         organisation_record = collection.find_one({"id" : identifier}, {"name_preferred" : 1})
    #         organisation["preview"] = organisation_record["name_preferred"]
    # if result["places"]:
    #     print("found associated places")
    #     for place in result["places"]:
    #         identifier = place["id"]
    #         place_record = collection.find_one({"id" : identifier}, {"name_preferred" : 1})
    #         place["preview"] = place_record["name_preferred"]
    print("result form search in database: ")
    print(result)
#    result = await result.to_list
    return result

@classes.func_logger
def get_manuscript_record(identifier):
    """
This function displays all elements links to a printed book record
    """
    dbname = db_actions.get_database()
    collection=dbname['bpf']
    result = collection.find_one({"id": identifier})
    if result["repository"]:
        for repository in result["repository"]:
            identifier = repository["place_id"]
            repository_record = collection.find_one({"id" : identifier}, {"name_preferred" : 1})
            repository["preview"] = repository_record["name_preferred"]
    print("result form search in database: ")
    print(result)
    return result

@classes.func_logger
def get_record(identifier):
    """
This function downloads a record with a given ID from the database
    """
    dbname = db_actions.get_database()
    collection=dbname['bpf']
    result = collection.find_one({"id": identifier})
    #pipeline = [{"$match" :{"id" : id}}]  #, {"$lookup" :{"from": collection, "local_field": "connected_persons.id", "foreign_field": "id", "as":"connected_persons_details"}}]
    #results = collection.aggregate(pipeline)
#    for record in results:
#        print("Here is record from PyMongo: ")
#        print(record)
    return result
