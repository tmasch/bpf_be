#pylint: disable=C0302,C0303,C0301,C0116
"""
\todo
"""
#import xml.etree.ElementTree
#import re
import os
import urllib.request

import numpy as np
import pymarc
from lxml import etree
from pymongo import MongoClient

#from dates_parsing import date_overall_parsing
from rich import print

from bpf import classes
from bpf import db_actions
from bpf import get_external_data
from bpf.parsing import parse_date
from bpf.parsing import parsing_helpers


#  a connection to the database has already been made.
#os.environ["MONGODB_HOST"] = "localhost"
#os.environ["MONGODB_PORT"] = "27017"

#client = MongoClient("localhost", 27017)
#db = client.bpf
#coll = db.bpf

#dbname =  db_actions.get_database()
#coll=dbname['bpf']

@classes.async_func_logger
async def identify_person(role_in):
    """
This function is used for every person named in the bibliographic record (author, editor, printer 
etc.). It will first search if a record for this person is already in the MongoDB database, and 
then search in the GND. If there is an ID-number (internal or GND), the search is done for the 
ID-number, otherwise for the name as string, and if this fails, for the name as key-words).
    """
# I think that there are problems with the search strategy - I hope it was not wrong in my original version. 
# 1: is there a GND ID known (never from ISTC; but from VD17/18, and perhaps from VD16)
#   if yes:
#       2: is the GND ID already in the database?
#           if yes:
#               3: is the Person_type1 (should be turned into something different) compatible with the 
#                   role demanded here?
#                       if yes:
#                           give this record as only search result
#                       if no: 
#                           give this record as only search result, but with a warning about the 
#                           discrepancy of type/role
#                           Unless the user makes a manual search with a different result, the person_type1 corresponding 
#                           to the role will be added. 
#           if no:
#               Search for the record with this ID in the GND; parse it, and present it as only search result
#               Unless the user manually searches with a different result, the record will be added with a 
#               person_type_one according to the role it has here.
#   if no:
#       4: Are records with this name already in the database? (search both for name_preferred and name_variant)
#           if yes: 
#               5: If one of them has not the person_type1 fitting with the role, act as in 3
#           if no:
#               6. Is the role 'Artist' (will probably not happen yet)
#                   if yes:
#                       make a search in ULAN (currently only OR search for individual words, this is not ideal)
#                       present list of results, save selected result with person_type_1 'Artist'
#                   if no:
#                       7. Is the name as a string found in the GND?
#                           if yes:
#                               present list of results, save selected result with person_type1 corresponding to role
#                           if no:
#                               8. Is the name as a search for single words found in the GND?
#                                   if yes:
#                                       present list of results, save selected result with person_type1 corresponding to role
#                                   if no:
#                                       I haven't written anything on that. 
#                                       > prompt user to give an ID from the GND or another database or create a stub record with the information available
# Or should all the stuff with Role/Person_type done after the search (naturally, there can only be a discrepancy if a record is already in the database.)


    print("Person and role to be identified")
    print(role_in.model_dump())
#    person=role_in.entity_and_connections.person
#    person
#    person_in=classes.Role()

#    candidates = []
    internal_id_person_type1_needed =  parsing_helpers.map_role_to_person_type(role_in.get_attribute("role"))

    found_person=False
    print("     Searching for person in database by GND ID")
#    gnd_id_in=role_in.entity_and_connections.entity.gnd_id
    gnd_id_in=role_in.get_attribute("gnd_id")
    print("input gnd id:"+gnd_id_in)
    if gnd_id_in:
        xx = classes.Role.find(classes.Role.entity_and_connections.entity.gnd_id == gnd_id_in,fetch_links=True)
        role_in_db = await xx.to_list()
        print("Search result")
        print(role_in_db)
    # This makes little sense up to now since no record from ISTC comes with a GND ID. 
    # This will be needed later, when also records of the VD17 and VD18 are being parsed. 


#    person.chosen_candidate = 999
    # For some reason, I cannot return the form when
    #'chosen candidate' is empty. Hence, I put this in as a default setting.
#    if person.id:
#        person_found = coll.find_one({"external_id": {"$elemMatch":
# {"name": person.id_name, "id": person.id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
#        person_found = await db_actions.find_person(person,"external_id")
#        if person_found:
            #print(person_found)
#            person.internal_id = person_found["id"]
#            person.internal_id_person_type1 = person_found["person_type1"]

#            person.internal_id_preview = person_found["name_preferred"] + " (in Database)"
            # The date should be added, but I first have to write how it is to be parsed
        if role_in_db:
#        role_in_db[0].comment="(in Database)"
            found_person=True
            print("found person")

            #The following is a warning that a matching person has the wrong type. 
    # if role_in.role not i

    #         if person.internal_id_person_type1_needed not in person.internal_id_person_type1:
    #             person_type1_present = ""
    #             for t in person.internal_id_person_type1:
    #                 person_type1_present = person_type1_present + "' and '" + t + "'"
    #             person_type1_present = person_type1_present[5:]
    #             person.internal_id_person_type1_comment = "This person is currently catalogued as " + person_type1_present + ", but not as '" + person.internal_id_person_type1_needed + "'. The latter will be added if this record has been saved. " 


#async def search_for_person_candidates():
    if not found_person and role_in.get_attribute("gnd_id"):
        print("Searching in GND by ID")
        print(role_in.get_attribute("gnd_id"))
#        else:
#            if person.id_name == "GND": # I will have to create similar things for other authority files
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D'\
              + role_in.entity_and_connections.entity.gnd_id\
                  + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
        print("url for person search: ")
        print(authority_url)
#        role_in.entity_and_connections.connected_persons = await find_and_parse_person_gnd(authority_url)
        person_found=True # This variable doesn't exist. Furthermore, there has not yet been any search
        print(role_in.model_dump())

#     else:

#         person.name = person.name.strip()
#         for old, new in parsing_helpers.encoding_list.items():
#             person.name = person.name.replace(old, new)

#         candidates_result = coll.find({"name_preferred" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1})
# #        candidates_result = await db_actions.find_person(person,"name_preferred")
#         for candidate_result in candidates_result:
#             candidate = classes.Person()   
#             candidate.internal_id = candidate_result["id"]
#             candidate.name_preferred = candidate_result["name_preferred"]
#             candidate.internal_id_person_type1 = candidate_result["person_type1"]
#             candidate.preview = candidate.name_preferred + " (in Database)" # The years should be added once I have them
#             print("Found as preferred name")
#             print(candidate.internal_id)
#             print(candidate.name_preferred)
#             print(candidate.internal_id_person_type1)
#             person_in.person_selection.append(candidate)
#         candidates_result = coll.find({"name_variant" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1}) 
# #        candidates_result = db_actions.find_person(person,"name_variant")
#         #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
#         for candidate_result in candidates_result:
#             candidate = classes.Person()
#             candidate.internal_id = candidate_result["id"]
#             candidate.name_preferred = candidate_result["name_preferred"]
#             candidate.internal_id_person_type1 = candidate_result["person_type1"]
#             candidate.preview = candidate.name_preferred + " (in Database)" # Also here, the years should be added
#             print("Found as variant: ")
#             print(candidate.internal_id)
#             print(candidate.name_preferred)
#             print(candidate.internal_id_person_type1)
#             candidate_duplicate = False
#             for extant_candidate in person_in.person_candidates:
#                 if extant_candidate.name_preferred == candidate.name_preferred:
#                     candidate_duplicate = True
#             if not candidate_duplicate:
# #                cc=classes.SelectionCandidate()
# #                cc.person=candidate          
# #                person_in.person_selection.append(cc)
#                 print(person.potential_candidates)


#             for candidate in person_in.person_candidates:
#                 if person.internal_id_person_type1_needed not in candidate.internal_id_person_type1:
#                     person_type1_present = ""
#                     for t in candidate.internal_id_person_type1:
#                         person_type1_present = person_type1_present + "' and '" + t + "'"
#                     person_type1_present = person_type1_present[5:]
#                     candidate.internal_id_person_type1_comment = "This person is currently catalogued as " + person_type1_present + ", but not as '" + person.internal_id_person_type1_needed + "'. The latter will be added if this record has been saved. " 

    if not found_person and role_in.get_attribute("gnd_id"):
        # I have the feeling that this search is never executed - why?
        print("No person found yet")
        person_name_search = role_in.name
        for old, new in parsing_helpers.url_replacement.items():
            person_name_search = person_name_search.replace(old, new)
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Per%3D' + person_name_search + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
        print(authority_url)
#        person_in.person_candidates = parse_person_gnd(authority_url)

    if not found_person:
        # This search shoudl only happen if the search before did not work. It should likewise exclude artists. 
            # if not person_in.person_candidates: #if still nothing has been found, a keyword search is performed instead of a string search. 
        print("Searching in GND by name")
        person_name_search = role_in.name
        name_divided = person_name_search.split("%20")
        name_query = ""           
        for word in name_divided:
            if word != "": #necessary, otherwise there will be error messages
                search_phrase = r"Per=" + word + r"%20and%20" # I don't get it, but the thing only works if the "=" is written as such and not as Percent code. Above, it is different. 
                name_query = name_query + search_phrase
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=' + name_query + r'BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'    
#        print(authority_url)
        new_potential_candidates = await find_and_parse_person_gnd(authority_url)
        role_in.entity_and_connections.connected_entities = new_potential_candidates

#        role_in.entity_and_connections.connected_persons.ap
#                = new_potential_candidates
#        person_in.person_candidates = person.person_candidates + new_potential_candidates
#         else:
#             if not person_in.person_candidates:
#                 person = await get_external_data.search_ulan(person)
#     if len(person_in.person_candidates) == 1: # If there is only one entry for this person, it is by default selected (although the user can also run a new search, once this is established)
#         person.chosen_candidate = 0
#     print("new person record")
# #    print(person)
#     person_in.person=person
#    print(person)
    print(role_in.model_dump())
    return role_in




@classes.async_func_logger
async def identify_additional_person(new_authority_id, role):
    """
This function is used for any additional authority records that are suggested as identifications for persons connected to a book.
Normally, they are parsed with gnd_parsing_person - but beforehand it is checked if they are already in Iconobase and have not been found for whatever reason. 
Currently all records must come from the GND - if other authority files are included, this function has to be changed. 
    """
    new_authority_id = new_authority_id.strip()
    potential_persons_list = []
    potential_person = classes.Node()
#    person_found = coll.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": new_authority_id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
    person = classes.Node()
    person.new_authority_id = new_authority_id
    person_found = db_actions.find_person(person,"GND")
    if person_found:
        #print(person_found)
        potential_person.internal_id = person_found["id"]
        potential_person.internal_id_person_type1 = person_found["person_type1"]
        potential_person.preview = person_found["name_preferred"] # The date should be added, but I first have to write how it is to be parsed
        internal_id_person_type1_needed =  parsing_helpers.map_role_to_person_type(role)
        if internal_id_person_type1_needed not in potential_person.internal_id_person_type1: 
            person_type1_present = ""
            for t in potential_person.internal_id_person_type1:
                person_type1_present = person_type1_present + "' and '" + t + "'"
            person_type1_present = person_type1_present[5:]
            potential_person.internal_id_person_type1_comment = "This person is currently catalogued as " + person_type1_present + ", but not as '" \
                + internal_id_person_type1_needed + "'. The latter will be added if this record has been saved. " 
        potential_persons_list.append(potential_person)

    else: 
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
        potential_persons_list = await find_and_parse_person_gnd(authority_url)
    #print("added person")
    #print(potential_persons_list)
    return potential_persons_list

@classes.func_logger
def identify_organisation(organisation):
    """
This function is used for every organisation named in the bibliographic record (printer etc.),
 and in addition for the repository of a book or manuscript. It will first search if a record
   for this organisation is already in the MongoDB database, and then search in the GND. If 
   there is an ID-number (internal or GND, the search is done for the ID-number, otherwise for
     the name as string, and if this fails, for the name as key-words)
    """
#    candidates = []
    print("Starting organisatin_identification for repository")
    organisation.internal_id_org_type1_needed = parsing_helpers.map_role_to_organisation_type(organisation.role)
    organisation.chosen_candidate = 999 # For some reason, this must not be empty
    if organisation.id:
#        organisation_found = coll.find_one({"external_id": {"$elemMatch": {"name": organisation.id_name, "id": organisation.id}}}, {"id": 1, "name_preferred": 1, "org_type1": 1})
        organisation_found = db_actions.find_organisation(organisation,"external_id")
        if organisation_found:
            organisation.internal_id = organisation_found["id"]
            organisation.internal_id_preview = organisation_found["name_preferred"] + " (in Database)"
            organisation.internal_id_org_type1 = organisation_found["org_type1"]
            org_type1_needed =  parsing_helpers.map_role_to_organisation_type(organisation.role)
            
            #The following is a warning that a matching person has the wrong type. 
            if org_type1_needed not in organisation.internal_id_org_type1:
                org_type1_present = ""
                for t in organisation.internal_id_org_type1:
                    org_type1_present = org_type1_present + "' and '" + t
                    org_type1_present = org_type1_present[5:] + "'"
                organisation.internal_id_org_type1_comment = "This organisation is currently catalogued as " + org_type1_present + ", but not as '" + org_type1_needed + "'. The latter will be added if this record has been saved. " 

        else:
            if organisation.id_name == "GND": # I will have to create similar things for other authority files
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + organisation.id + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
                print(authority_url)
                organisation.potential_candidates = find_and_parse_organisation_gnd(authority_url)
    else:
        print("No repository ID")
        organisation.name = organisation.name.strip()
#        candidates_result = (coll.find({"name_preferred" : organisation.name}, {"id": 1, "name_preferred" : 1, "org_type1" : 1}))
        candidates_result = db_actions.find_organisation(organisation,"name")
        print("Search for repository candidate completed")
        for candidate_result in candidates_result:
            candidate = classes.Node()   
            candidate.internal_id = candidate_result["id"]
            candidate.name_preferred = candidate_result["name_preferred"]
            candidate.preview = candidate_result["name_preferred"] + " (in Database)"
            candidate.internal_id_org_type1 = candidate_result["org_type1"]
            print("orgtype1 in search for name_preferred: ")
            print(candidate.preview)
            print(candidate.internal_id_org_type1)
            organisation.potential_candidates.append(candidate)
#        candidates_result = coll.find({"name_variant" : organisation.name}, {"id": 1, "name_preferred" : 1, "org_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
        candidates_result = db_actions.find_organisation(organisation,"name_variant")
        for candidate_result in candidates_result:
            candidate = classes.Node()   
            candidate.internal_id = candidate_result["id"]
            candidate.name_preferred = candidate_result["name_preferred"]
            candidate.internal_id_org_type1 = candidate_result["org_type1"]
            candidate.preview = candidate.name_preferred + " (in Database)" # Maybe I add other information to it later. 
            print("orgtype1 in search for name_variant: ")
            print(candidate.internal_id_org_type1)
            candidate_duplicate = False # This is needed to avoid having a candidate listed twice, it is rather longwided since I cannot use a simple if ... in thing in class instances. 
            for extant_candidate in organisation.potential_candidates:
                if extant_candidate.name_preferred == candidate.name_preferred:
                    candidate_duplicate = True
            if not candidate_duplicate:
                    
#            if candidate not in organisation.potential_candidates:
#                print("Candidate not yet in list")
                organisation.potential_candidates.append(candidate)
            # The following is about a warning if the found organisations have the wrong type. I could not try it out, since the VD17 always gives IDs of organisations, 
            # and the ISTC does not have them. 
            for candidate in organisation.potential_candidates:
                print("Repository types present:")
                print(candidate.internal_id_org_type1)
                print("Repository types needed: ")
                print(organisation.internal_id_org_type1_needed)
                if organisation.internal_id_org_type1_needed not in candidate.internal_id_org_type1:
                    org_type1_present = ""
                    for t in candidate.internal_id_org_type1:
                        org_type1_present = org_type1_present + "' and '" + t + "'"
                    org_type1_present = org_type1_present[5:]
                    candidate.internal_id_org_type1_comment = "This organisation is currently catalogued as "\
                          + org_type1_present + ", but not as '" + organisation.internal_id_org_type1_needed + "'. The latter will be added if this record has been saved. " 

        if not organisation.potential_candidates: #if nothing has been found in the database
            organisation_name_search = organisation.name
            for old, new in parsing_helpers.url_replacement.items():
                organisation_name_search = organisation_name_search.replace(old, new)
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Koe%3D' + organisation_name_search + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'          
            organisation.potential_candidates = find_and_parse_organisation_gnd(authority_url)        
            name_divided = organisation_name_search.split("%20")
            name_query = ""           
            for word in name_divided:
                if word != "":    
                    search_phrase = r"Koe=" + word + r"%20and%20" # I don't get it, but the thing only works if the "=" is written as such and not as Percent code. Above, it is different. 
                    name_query = name_query + search_phrase
#                    print ("name query:" + name_query)
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=' + name_query + r'BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'    
      
            new_potential_candidates = find_and_parse_organisation_gnd(authority_url)
            for candidate in new_potential_candidates:
                if candidate not in organisation.potential_candidates: #I need this distinction because I perform both a string and a keyword search, and both may yield the same results
                    organisation.potential_candidates.append(candidate)
    if len(organisation.potential_candidates) == 1: # If there is only one entry for this organisation, it is by default selected (although the user can also run a new search, once this is established)
        organisation.chosen_candidate = 0
        
    return organisation

@classes.func_logger
def identify_additional_organisation(new_authority_id, role):
    """
This function is used for any additional authority records that are suggested as identifications for organisations connected to a book.
Normally, they are parsed with gnd_parsing_organisation - but beforehand it is checked if they are already in Iconobase and have not been found for whatever reason. 
Currently all records must come from the GND - if other authority files are included, this function has to be changed. 
    """
    new_authority_id = new_authority_id.strip()
    potential_orgs_list = []
    potential_org = classes.Node()
    org = classes.Node()
    org.new_authority_id=new_authority_id
#    org_found = coll.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": new_authority_id}}}, {"id": 1, "name_preferred": 1, "org_type1" : 1})
    org_found = db_actions.find_organisation(org,"GND")
    if org_found:            
        print(org_found)
        potential_org.internal_id = org_found["id"]
        potential_org.internal_id_org_type1 = org_found["org_type1"]
        potential_org.preview = org_found["name_preferred"] # The date should be added, but I first have to write how it is to be parsed
        internal_id_org_type1_needed = parsing_helpers.map_role_to_organisation_type(role)
        if internal_id_org_type1_needed not in potential_org.internal_id_org_type1: 
            org_type1_present = ""
            for t in potential_org.internal_id_org_type1:
                org_type1_present = org_type1_present + "' and '" + t + "'"
            org_type1_present = org_type1_present[5:]
            potential_org.internal_id_org_type1_comment = "This organisation is currently catalogued as " + org_type1_present + ", but not as '" \
                + internal_id_org_type1_needed + "'. The latter will be added if this record has been saved. " 
        else:
            internal_id_org_type1_needed = ""
        potential_orgs_list.append(potential_org)
    else: 
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
        potential_orgs_list = find_and_parse_organisation_gnd(authority_url)

    return potential_orgs_list



                

@classes.func_logger
async def identify_place(place):
    """
This function is used for every place named in the bibliographic record (place of publishing / manufacture)
It will first search if a record for this place is already in the MongoDB database, and then search in the GND
If there is an ID-number (internal or GND, the search is done for the ID-number, otherwise for the name as string, and if this fails, for the name as key-words)
Note that the GND parser combined with it suppresses all records to regions - if this mechanism is later also used for identifying regions, this might need to be changed
Since there are often many locations connected toa town (e.g., all villages in its district), I increase the number of hits from the GND to 400 and sort them alphabetically. 
    """
    if place.role:
        print(place.role)
    else:
        print("No place.role")
        place.role = "pup" # I just define this for the time being. 
    place.internal_id_place_type1_needed = parsing_helpers.map_role_to_place_type(place.role)
    place.chosen_candidate = 999
    print("Arrived in place_identification")
    if place.id:
#        place_found = coll.find_one({"external_id": {"$elemMatch": {"name": place.id_name, "id": place.id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
        place_found = db_actions.find_place(place,"external_id")
        if place_found:
            place.internal_id = place_found["id"]
            place.internal_id_preview = place_found["name_preferred"] + " (in Database)"
            place.internal_id_place_type1 = place_found["place_type1"] 
#            print('Place data:')
#            print(place.internal_id_place_type1)           
            place_type1_needed = parsing_helpers.map_role_to_place_type(place.role)
            #The following is a warning that a matching place has the wrong type. It should also be 
            # included for all searches for names in Iconobase, but I don't build this yet since there aren't any records in it that allow my to try it out. 
            # This option has not been tried out properly since places rarely come with GND numbers
            if place_type1_needed not in place.internal_id_place_type1:
                place_type1_present = ""
                for t in place.internal_id_place_type1:
                    place_type1_present = place_type1_present + "' and '" + t
                place_type1_present = place_type1_present[5:] + "'"

                place.internal_id_place_type1_comment = "This place is currently catalogued as " + place_type1_present + ", but not as '" + place_type1_needed + "'. \
                    An additional record for " + place_type1_needed + " will be produced if this record is saved. " 
        else:
            if place.id_name == "GND": # I will have to create similar things for other authority files
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + place.id + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
                print("authority_url with Gnd number: " + authority_url)
                place.potential_candidates = await parse_place_gnd(authority_url)              
    else:
        print("place name has no ID")
        place.name = place.name.strip()
#        candidates_result = coll.find({"name_preferred" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1})
        candidates_result = db_actions.find_place(place,"name_preferred")
        for candidate_result in candidates_result:           
            candidate = classes.Node()   
            candidate.internal_id = candidate_result["id"]
            candidate.name_preferred = candidate_result["name_preferred"] # I need this to create previews for places of making
            print("candidate found through name search in database (preferred name)" + candidate.internal_id)
            candidate.preview = candidate_result["name_preferred"] + " (in Database)"
            candidate.internal_id_place_type1 = candidate_result["place_type1"]
            place.potential_candidates.append(candidate)
#        candidates_result = coll.find({"name_variant" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
        candidates_result = db_actions.find_place(place,"name_variant")
        for candidate_result in candidates_result:
            candidate = classes.Node()   
            candidate.internal_id = candidate_result["id"]
            print("candidate found through name search in database (variant name name)" + candidate.internal_id)
            candidate.preview = candidate_result["name_preferred"] + " (in Database)"
            candidate.internal_id_place_type1 = candidate_result["place_type1"]

            if candidate not in place.potential_candidates:
                place.potential_candidates.append(candidate)
                # Warning if the place has not the right type:
            for candidate in place.potential_candidates:
                print(candidate.preview)
                print(candidate.internal_id_place_type1)
                print(place.internal_id_place_type1_needed)
                if place.internal_id_place_type1_needed not in candidate.internal_id_place_type1:
                    place_type1_present = ""
                    for t in candidate.internal_id_place_type1:
                        place_type1_present = place_type1_present + "' and '" + t + "'"
                    place_type1_present = place_type1_present[5:]


                    candidate.internal_id_place_type1_comment = "This place is currently catalogued as " + place_type1_present + ", but not as '" + place.internal_id_place_type1_needed + "'. \
                    An additional record for " + place.internal_id_place_type1_needed + " will be produced if this place is selected and the record is saved. " 

        if not place.potential_candidates: #if nothing has been found
            print("Candidate not found in database")
            place_name_search = place.name.strip()
            for old, new in parsing_helpers.url_replacement.items():
                place_name_search = place_name_search.replace(old, new)
                #print("Search term for place :x" + place_name_search + "x")
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Geo%3D' + place_name_search + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
            print('URL for place name search : '+ authority_url)
            place.potential_candidates = await parse_place_gnd(authority_url)
            print("Number of 'portential candidates': ")
            print(len(place.potential_candidates))
#       I actually do not believe that one needs a words search for places              
            name_divided = place_name_search.split("%20")
            name_query = ""           
            for word in name_divided:
                if word != "":    
                    search_phrase = r"Geo%3D" + word + r"%20and%20" # I don't get it, but the thing only works if the "=" is written as such and not as Percent code. Above, it is different. 
                    name_query = name_query + search_phrase
                    print ("name query:" + name_query)
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=' + name_query + r'BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'    
            additional_potential_candidates = await parse_place_gnd(authority_url)
            print("Number or additional potential candidates: ")
            print(len(additional_potential_candidates))
            for additional_candidate in additional_potential_candidates:
                if additional_candidate not in place.potential_candidates:
                    place.potential_candidates.append(additional_candidate)
    place.potential_candidates = sorted(place.potential_candidates, key = lambda candidate : candidate.preview)
    if len(place.potential_candidates) == 1: # If there is only one entry for this person, it is by default selected (although the user can also run a new search, once this is established)
        place.chosen_candidate = 0
    return place


@classes.func_logger
async def identify_additional_place(new_authority_id, role):
    """
This function is used for any additional authority records that are suggested as identifications for organisations connected to a book.
Normally, they are parsed with gnd_parsing_place - but beforehand it is checked if they are already in Iconobase and have not been found for whatever reason. 
Currently all records must come from the GND - if other authority files are included, this function has to be changed. 
    """
    new_authority_id = new_authority_id.strip()
    potential_places_list = []
    potential_place = classes.Node()
#    place_found = coll.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": new_authority_id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
    place=classes.Node
    place.new_authority_id=new_authority_id
    place_found = db_actions.find_place(place,"GND")
    if place_found:            
#        print(place_found)
        potential_place.internal_id = place_found["id"]
        potential_place.internal_id_place_type1 = place_found["place_type1"]
        potential_place.preview = place_found["name_preferred"] + " (in Database)" 
        internal_id_place_type1_needed = parsing_helpers.map_role_to_place_type(role)
        if internal_id_place_type1_needed not in potential_place.internal_id_place_type1: 
            place_type1_present = ""
            for t in potential_place.internal_id_place_type1:
                place_type1_present = place_type1_present + "' and '" + t + "'"
            place_type1_present = place_type1_present[5:]
            potential_place.internal_id_place_type1_comment = "This place is currently catalogued as " + place_type1_present + ", but not as '" \
                + internal_id_place_type1_needed + "'. An additional record for " + internal_id_place_type1_needed + " will be produced if this place is selected and the record is saved. "
        potential_places_list.append(potential_place)
    else: 
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
#        print("authority URL in additional_place_identification")
#        print(authority_url)
        potential_places_list = await parse_place_gnd(authority_url)
#        print("Potential places list in additional_place_identification: ")
#        print(potential_places_list)
    return potential_places_list


@classes.async_func_logger
async def find_and_parse_person_gndid(gnd_id):
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D'\
                    + gnd_id\
                    + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
    content=await get_external_data.get_web_data(authority_url)
    root = etree.XML(content)
    records=root.find("records", namespaces=root.nsmap)
    for record in records:
#Set GND IDs
        d = find_datafields(record,"035")
#        print(x)
        s = find_subfields(d,"a")
        for y in s:
            if y.get("a") is not None:
                external_reference = classes.ExternalReference()
                external_reference.name="GND"
                external_reference.external_id=y["a"]
#                person_found.external_id.append(external_reference)

@classes.async_func_logger
async def get_records(gnd_id):
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D'\
                    + gnd_id\
                    + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
    content=await get_external_data.get_web_data(authority_url)
    root = etree.XML(content)
    records=root.find("records", namespaces=root.nsmap)
    return records

@classes.async_func_logger
async def find_related_persons(gnd_id):
    records = await get_records(gnd_id)
    for record in records:
        r = gnd_record_get_connected_persons(record)
    return r



@classes.async_func_logger
async def find_and_parse_person_gnd(authority_url):
    """
\todo
    """

#    url = urllib.request.urlopen(authority_url)
#    tree = xml.etree.ElementTree.parse(url)
#    root = tree.getroot()

    result = []
    content=await get_external_data.get_web_data(authority_url)
    root = etree.XML(content)
    records=root.find("records", namespaces=root.nsmap)
#    print(records)
#    print(records.tag)
#    tag_id='400'
#    subfield_code="a"
    for record in records:
        print("found record")



    #print(root)
    
    # for record in root[2]:
    #     print("Parsing person information")
    #     pe = classes.Person()
    #     comment = ""
    #     date_preview = ""
    #     ortg_preview = ""
    #     orts_preview = ""
    #     ortw_preview = ""
    #     name_variant_preview = ""
    #     comments_preview = ""

        person_found=classes.Node()
        person_found.external_id.extend(gnd_record_get_gnd_internal_id(record))
        person_found.external_id.extend(gnd_record_get_external_references(record))
        name_preferred, comments = gnd_record_get_name_preferred(record)
        person_found.add_attribute("name_preferred",name_preferred)
        name_variant, comments = gnd_record_get_name_variant(record, person_found.comments)
#        person_found.add_attribute("name_variant",name_variant)
        person_found.add_attribute("gnd_id",gnd_record_get_gnd_id(record))
        person_found.type="Person"
#        person_found.connected_persons =  gnd_record_get_connected_persons(record)
#        person_found.connected_organisations = gnd_record_get_connected_orgs(record)
#        person_found.connected_places = gnd_record_get_connected_places(record)
        person_found.add_attribute("sex",gnd_record_get_sex(record))
#        person_found.dates_from_source = get_gnd_dates(record)
#        person_found.comments = parse_gnd_profession(record, person_found.comments)
#        person_found.comments = get_gnd_comments(record, person_found.comments)
#        print(person_found)
 #       connected_person = classes.EntityConnection()
 #       connected_person.connection_type = "Candidate"
 #       connected_person.entityA = person_found
        result.append(person_found)



    return result



@classes.func_logger
def gnd_record_get_gnd_internal_id(record):
    """
    #         for step1 in record[2][0]:
    #             match step1.get('tag'):
    # #                case "001":
    # #                    pe_id = External_id()
    # #                    pe_id.name = "GND_intern"
    # #                    pe_id.id = step1.text
    # #                    pe_id.uri = "GND_intern" + step1.text                    
    # #                    pe.external_id.append(pe_id)
    """
    external_references=[]
    controlfields=record.findall("{*}recordData/{*}record/{*}controlfield[@tag='001']")
    
    #datafields = find_datafields(record,"001")
    

    
    external_reference = classes.ExternalReference()
    external_reference.name="GND intern"
    external_reference.external_id=controlfields[0].text
    external_references.append(external_reference)
            
#   Annoyingly, the search also finds IDs from the old database PND. If it is possible that a PND ID is the same as the GND ID of a 
#   different record, I have to include a function to delete this record from the results (I am enquiring if this is the case)

    print("internal GND id: ")
    print(external_references)
    print(controlfields)
    return external_references

    # x = find_datafields(record,"001")
    # print(x)
    # for y in x:
    #     if y.get("a") is not None:
    #         external_reference = classes.ExternalReference()
    #         external_reference.name = "GND_intern"
    # datafields=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
    # for datafield in datafields:
    #     subfields=datafield.findall("{*}subfield")
    #     subfield_hash={}
    #     for subfield in subfields:
    #         key= subfield.get("code")
    #         value=subfield.text
    

@classes.func_logger
def gnd_record_get_gnd_id(record):
    gnd_id=""
    datafields = find_datafields(record,"035")
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        print(subfields)
        if subfields:
            if subfields[0][0:8] == "(DE-588)":
                gnd_id=subfields[0][8:] #The latter cuts out the prefix '(DE-588)'.
    print(gnd_id)
    return gnd_id

@classes.func_logger
def gnd_record_get_external_references(record):
    """
#                 case "035":
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "a":
#                                 pe_id = classes.ExternalReference()
#                                 pe_id.name = "GND"
#                                 if step2.text[0:8] == "(DE-588)":
#                                     pe_id.external_id = step2.text[8:] #The latter cuts out the prefix '(DE-588)'.
#                                     pe_id.uri = r'https://d-nb.info/gnd/' + pe_id.external_id
#                                     duplicate_id = False  # Sometimes, the record containing the GND ID appears twice, hence it should not be added a second time. 
#                                     for id_duplicate in pe.external_id:
#                                         if id_duplicate.uri == pe_id.uri:
#                                             duplicate_id = True
#                                     if not duplicate_id:
#                                         pe.external_id.append(pe_id)
# #                                    if not pe.external_id: #
# #                                        pe.external_id.append(pe_id)
#                                 # Quite often, there are several GND records for one person, and if discovered, they are merged, and all GND IDs but become obsolete.
#                                 # However, they are still stored in the record (035z) and are found by the search. 
#                                 # Hence, this ID may be different from the person.id I used for the search in the first place.
"""
    external_references=[]
    datafields = find_datafields(record,"035")
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        if subfields: 
            external_reference = classes.ExternalReference()
            external_reference.name="GND"
            if subfields[0][0:8] == "(DE-588)" or subfields[0][0:8] == "(DE-101)": 
                # sometimes, there is this prefix, which is unnecessary and should be cut out. 
                external_reference.external_id=subfields[0][8:]
            else:
                external_reference.external_id=subfields[0][0:]
            external_reference.uri = r'https://d-nb.info/gnd/' + external_reference.external_id
            for extant_external_reference in external_references:
                if extant_external_reference.name == external_reference.name and \
                    extant_external_reference.external_id == external_reference.external_id:
                    break
            else: 
                external_references.append(external_reference)
            
#   Annoyingly, the search also finds IDs from the old database PND. If it is possible that a PND ID is the same as the GND ID of a 
#   different record, I have to include a function to delete this record from the results (I am enquiring if this is the case)

    return external_references



@classes.func_logger
def gnd_record_get_name_preferred(record):
    """
    Takes the preferred name from field 100
    Possible additions: some more standard identifyers in 100c
    e.g. "Gott", "Biblische Person" could be moved to 'Comment'
    Or: standardised terms in the 'Comment' section may even
    be used for putting Person records into the right group
    of person
    """
# Set preferred name
    name_preferred = ""
    comments = ""
    datafields = find_datafields(record,"100")
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        if subfields: 
            name_preferred = subfields[0]
        subfields = find_subfields(datafield,"b")
        if subfields: 
            name_preferred = name_preferred+ " " + subfields[0]
        subfields = find_subfields(datafield,"c")
        if subfields:
            if ("Kaiser" in subfields[0] or "König" in subfields[0] or "Herzog" in subfields[0] \
                    or "Kurfürst" in subfields[0] or "Markgraf" in subfields[0] \
                        or "Bischof" in subfields[0] or "Fürstbischof" in subfields[0] \
                            or "Erzbischof" in subfields[0] or "Fürsterzbischof" in subfields[0] \
                                or "Abt" in subfields[0]):
                comments = subfields[0]
            elif ", Heiliger" in subfields[0]:
                name_preferred = name_preferred +" ("+ subfields[0][:-10] + ")"
                comments = "Saint"
            elif ", Heilige" in subfields[0]:
                name_preferred = name_preferred +" ("+ subfields[0][:-9] + ")"
                comments = "Saint"
            elif subfields[0] == "Heiliger":
                comments = "Saint"
            elif subfields[0] == "Heilige":
                comments = "Saint"            

            
            else:
                name_preferred = name_preferred + " (" + subfields[0] + ")"
    return (name_preferred, comments)

@classes.func_logger
def gnd_record_get_sex(record):
    """
    #                 case "375":
    #                     for step2 in step1:
    #                         match step2.get('code'):
    #                             case "a":
    #                                 if step2.text == "1":
    #                                     pe.sex = "male"
    #                                 if step2.text == "2":
    #                                     pe.sex = "female"
    # Set sex
    """
    print("in function gnd_record_get_sex")
    sex = ""
    datafields = find_datafields(record,"375")
    for datafield in datafields:
    
        subfields = find_subfields(datafield,"a")
        if subfields:
            print("sex_subfields")
            print(subfields)
            if subfields[0] == "1":
                sex = "male"
            elif subfields[0] == "2":
                sex = "female"
    return sex


@classes.func_logger
def gnd_record_get_name_variant(record, comments):
    """
#                 case "400":
#                     name_number = ""
#                     name_comment = ""
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "a":
#                                 name_variant = step2.text
#                             case "b": # The numbering for rulers
#                                 name_number =  " " + step2.text
#                             case "c": # For rulers, comments on Territory, title and time of ruling. 
#                                 # I put that now into a comment field. Once I have all the structure for persons' offices I might try to make an automatic import,
#                                 # but I fear it is too messy to make it worthwhile.                                
#                                 comment = step2.text
#                                 if " von " in comment or " of " in comment or " de " in comment or "," in comment: # This field can contain either an additional epithet or the territory and title of a ruler. The former will be stored
#                                     # as part of the name, the latter will be relegated to the comment field. 
#                                     # As a rough way of discerning both, anything with "von", "of" or "de" or a comma is regarded as belonging to a ruler
#                                     if comment not in pe.comments:
#                                         pe.comments = pe.comments + " / " + comment
#                                 else: 
#                                     name_comment = " (" + comment + ")"
# #                                    name_variant = name_variant + name_number + " (" + comment + ")"
#                     name_variant = name_variant + name_number + name_comment
#                     for variant in pe.name_variant:
#                         if name_variant in variant:
#                             name_variant = ""
#                     if name_variant:
#                         pe.name_variant.append(name_variant)
"""
    datafields = find_datafields(record,"400")
    variants = []
    for datafield in datafields:
        name_variant = ""
        

        subfields = find_subfields(datafield,"a")
        if subfields: 
            name_variant = subfields[0]
        subfields = find_subfields(datafield,"b")
        if subfields: 
            name_variant = name_variant + " " + subfields[0]
        subfields = find_subfields(datafield,"c")
        if subfields:
            if " von " in subfields[0] or " of " in subfields[0] or " de " in subfields[0] or "," in subfields[0]:
                if subfields[0] not in comments:
                    comments = comments + " / " + subfields[0]
            else:
                name_variant = name_variant + " (" + subfields[0] + ")"
        if name_variant not in variants:
            variants.append(name_variant)
    return (variants, comments)
            




@classes.func_logger
def gnd_record_get_connected_persons(record):
    """
#                 case "500":
#                     conn_pe = classes.Person()
# #                    conn_pe.external_id = []
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "0":
#                                 if step2.text[0:8] == "(DE-588)":
#                                     conn_id = classes.ExternalReference()
#                                     conn_id.name = "GND"
#                                     conn_id.external_id = step2.text[8:]
#                                     conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.external_id
#                                     conn_pe.external_id.append(conn_id)

#                             case "a":
#                                 conn_pe.name = step2.text
#                             case "b": 
#                                 conn_pe.name = conn_pe.name + " " + step2.text
#                             case "c": 
#                                 conn_pe.name = conn_pe.name + "(" + step2.text + ")" #in this case I add this to the name
#                             # since it may make clear who the person is. 
#                             case "4":
#                                 if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
#                                     conn_pe.connection_type = step2.text
#                             case "9": 
#                                 if step2.text[0:2] == "v:":
#                                     conn_pe.connection_comment = step2.text[2:]
#                                 if step2.text[0:2] == "Z:":
#                                     conn_pe.connection_time = step2.text[2:]
#                     if "VD-16 Mitverf." not in conn_pe.connection_comment: 
#                             # someone connected all persons who appear together as authors in the VD16,
#                             # I want them removed. 
#                         pe.connected_persons.append(conn_pe)
"""
    # Question: do we need here both 'name' and 'name_preferred'?
    # My idea was the following: I save very simple references to related persons
    # (connection type + name + id). If there was a record with this id in the database,
    # I replace the name with the preferred name in the record (they should be identical, but 
    # maybe they are not). 
    # If now there are full new entity records created (although probably as 'stubs'), 
    # one should probably use here the field 'name_preferred' (and if the stub is upgraded,
    # it should probably be replaced with the name_preferred of the actual record for this person).
    # Does the field 'name' have a role at all? Probably not - but I still left it. 
    # Perhaps, the name_preferred should also go as Preview into the ConnectedEntities, if one 
    # does previews there. 

    # How should this be connected to the person record? As long as there is no connection, it is not called,
    # and I cannot test it. 
    connections = []
    datafields = find_datafields(record,"500")
    for datafield in datafields:
        p=classes.Node()
        p.type="Person"
        ec=classes.Edge()
        subfields = find_subfields(datafield,"0")
        if subfields: 
            for subfield in subfields:
                external_reference = classes.ExternalReference()
                external_reference.name = "GND"
                if subfield[0:8] == "(DE-588)" or subfield[0:8] == "(DE-101)":
                    external_reference.external_id = subfield[8:]
                else:
                    external_reference.external_id = subfield
                external_reference.uri = r'https://d-nb.info/gnd/' + external_reference.external_id
                p.external_id.append(external_reference)
        subfields = find_subfields(datafield,"a")
        if subfields: 
            p.name = subfields[0]
        subfields = find_subfields(datafield,"b")
        if subfields: 
            p.name = p.name + " " + subfields[0]
        subfields = find_subfields(datafield,"c")
        if subfields:
            p.name = p.name + " (" + subfields[0] + ")"
        p.name_preferred = p.name
        subfields = find_subfields(datafield,"4")
        if subfields: 
            if "http" not in subfields[0]:
                ec.connection_type = subfields[0] # Once one can give connection_types for both directions,
                # here the correct connection types in both directions have to be created
                ec.relationB = subfields[0]
        subfields = find_subfields(datafield,"9")
        if subfields: 
            for subfield in subfields:
                if subfield[0:2] == "v:":
                    ec.connection_comment = subfield[2:]
                elif subfield[0:2] == "Z:":
                    ec.connection_time = subfield[2:]
            
        ec.entityB = p
        if "VD-16 Mitverf." not in ec.connection_comment:
            connections.append(ec)
    print(connections)
    return connections


@classes.func_logger
def gnd_record_get_connected_orgs(record):
    """
#                 case "510":
#                     conn_org = classes.EntityConnection()
#                     conn_org.external_id = []
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "0":
#                                 if step2.text[0:8] == "(DE-588)":
#                                     conn_id = classes.ExternalReference()
#                                     conn_id.name = "GND"
#                                     conn_id.external_id = step2.text[8:]
#                                     conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.external_id
#                                     conn_org.external_id.append(conn_id)
#                             case "a": 
#                                 conn_org.name = step2.text
#                             case "b": #for sub-units of organisations - no clue if this will ever happen in my circumstances
#                                 conn_org.name = conn_org.name + " (" + step2.text + ")"
#                             case "4":
#                                 if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
#                                     conn_org.connection_type = step2.text
#                             case "9": 
#                                 if step2.text[0:2] == "v:":
#                                     conn_org.connection_comment = step2.text[2:]
#                                 if step2.text[0:2] == "Z:":
#                                     conn_org.connection_time = step2.text[2:]
#                     pe.connected_organisations.append(conn_org)
    
    """
    connections = []
    datafields = find_datafields(record,"510")
    for datafield in datafields:
        org=classes.Node()
        org.type="Organisation"
        ec=classes.Edge()
        subfields = find_subfields(datafield,"0")
        if subfields: 
            for subfield in subfields:
                external_reference = classes.ExternalReference()
                external_reference.name = "GND"
                if subfield[0:8] == "(DE-588)" or subfield[0:8] == "(DE-101)":
                    external_reference.external_id = subfield[8:]
                else:
                    external_reference.external_id = subfield
                external_reference.uri = r'https://d-nb.info/gnd/' + external_reference.external_id
                org.external_id.append(external_reference)
        subfields = find_subfields(datafield,"a")
        if subfields: 
            org.name = subfields[0]
        subfields = find_subfields(datafield,"b")
        if subfields: 
            org.name = org.name + " (" + subfields[0] + ")"
        org.name_preferred = org.name
        subfields = find_subfields(datafield,"4")
        if subfields: 
            if "http" not in subfields[0]:
                ec.connection_type = subfields[0] # Once one can give connection_types for both directions,
                # here the correct connection types in both directions have to be created
                ec.relationB = subfields[0]
        subfields = find_subfields(datafield,"9")
        if subfields: 
            for subfield in subfields:
                if subfield[0:2] == "v:":
                    ec.connection_comment = subfield[2:]
                elif subfield[0:2] == "Z:":
                    ec.connection_time = subfield[2:]
            
        ec.entityB = org
        connections.append(ec)
    print(connections)
    return connections


@classes.func_logger
def gnd_record_get_connected_places(record):
    """
    #                 case "551":
#                     conn_pl = classes.EntityConnection()
#                     conn_id = classes.ExternalReference()
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "0":
#                                 if step2.text[0:8] == "(DE-588)":
#                                     conn_id.name = "GND"
#                                     conn_id.external_id = step2.text[8:]
#                                     conn_pl.external_id.append(conn_id)
#                                     conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.external_id
#                             case "a": 
#                                 conn_pl.name = step2.text
#                             case "g": 
#                                 conn_pl.name = conn_pl.name + " (" + step2.text + ")"
#                             case "4":
#                                 if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
#                                     conn_pl.connection_type = step2.text
#                             case "9": 
#                                 if step2.text[0:2] == "v:":
#                                     conn_pl.connection_comment = step2.text[2:]
#                                 if step2.text[0:2] == "Z:":
#                                     conn_pl.connection_time = step2.text[2:]
#                     if conn_pl.connection_type == "ortg":
#                         ortg_preview = ", born in " + conn_pl.name
#                     if conn_pl.connection_type == "orts":
#                         orts_preview = ", died in " + conn_pl.name
#                     if conn_pl.connection_type == "ortw":
#                         ortw_preview = ", active in " + conn_pl.name
#                     pe.connected_locations.append(conn_pl)
"""
    connections = []
    datafields = find_datafields(record,"551")
    for datafield in datafields:
        pl=classes.Node()
        pl.type="Place"
        ec=classes.Edge()
        subfields = find_subfields(datafield,"0")
        if subfields: 
            for subfield in subfields:
                external_reference = classes.ExternalReference()
                external_reference.name = "GND"
                if subfield[0:8] == "(DE-588)" or subfield[0:8] == "(DE-101)":
                    external_reference.external_id = subfield[8:]
                else:
                    external_reference.external_id = subfield
                external_reference.uri = r'https://d-nb.info/gnd/' + external_reference.external_id
                pl.external_id.append(external_reference)
        subfields = find_subfields(datafield,"a")
        if subfields: 
            pl.name = subfields[0]
        subfields = find_subfields(datafield,"g")
        if subfields: 
            pl.name = pl.name + " (" + subfields[0] + ")"
        pl.name_preferred = pl.name
        subfields = find_subfields(datafield,"4")
        if subfields: 
            if "http" not in subfields[0]:
                ec.connection_type = subfields[0] # Once one can give connection_types for both directions,
                # here the correct connection types in both directions have to be created with the help of all the
                # long lists of different terms. 
                ec.relationB = subfields[0]
        subfields = find_subfields(datafield,"9")
        if subfields: 
            for subfield in subfields:
                if subfield[0:2] == "v:":
                    ec.connection_comment = subfield[2:]
                elif subfield[0:2] == "Z:":
                    ec.connection_time = subfield[2:]
            
        ec.entityB = pl
        connections.append(ec)
    print(connections)
    return connections




@classes.func_logger
def gnd_record_get_stuff(record):
    """
    I assume that this is all no longer needed. 
#         #if pe.dates_from_source:
#             #pe.dates = dates_parsing(pe.dates_from_source)
#         if pe.comments:                
#             comments_preview = " (" + pe.comments + ")"
#         if pe.name_variant:
#             name_variant_preview = ", also called: "
#             for variant in pe.name_variant:
#                 name_variant_preview = name_variant_preview + variant + "; "
#             name_variant_preview = name_variant_preview[:-2]
        

#         pe.preview = pe.name_preferred + date_preview + ortg_preview + ortw_preview + orts_preview + name_variant_preview + comments_preview
#         potential_persons_list.append(pe)
        #print(potential_persons_list)
#        print(pe.preview)
                    

#        print(pe.external_id)
#        print(pe.name_preferred)
#        print(pe.name_variant)
#        print(pe.sex)
#        print(pe.comments)    
#        print(pe.connected_persons)
#        print(pe.dates_from_source)
#        print(pe.connected_organisations)
#        print(pe.connected_locations)
#        pprint(pe)
#    print(persons_list)
#        print(person_found.model_dump())
        connected_person = classes.EntityConnection()
        connected_person.connection_type = "Candidate"
        connected_person.person = person_found
#        print(connected_person.model_dump())
#        print(result.model_dump())
        result.append(connected_person)
#        print(result.model_dump())



                


        
    #record = root[2][0][2][0][0]
    #print(record.text)
    #print("potential persons list made")
"""
# This section contains four elements: connected organisations, connected places, dates, and professions. 
# The first two should function analogous to connected persons above, but it does not make sense
# to refactor them as long as I cannot test gnd_record_get_connected_persons.   The other two have been copied
# into separate functions
    
    result = ""
    return result


@classes.func_logger
def get_gnd_comments(record, comments):
    """
    #                 case "678":
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "b":
#                                 if pe.comments:
#                                     pe.comments = step2.text + "; " + pe.comments
#                                 else:
#                                     pe.comments = step2.text
    """
    datafields = find_datafields(record,"678")
    for datafield in datafields:
        subfields = find_subfields(datafield,"b")
        if subfields:
            comments = comments + "; " + subfields[0]
    if comments[0:2] == "; ":
        comments = comments[2:]
    return comments

@classes.func_logger
def get_gnd_dates(record):
    """
                case "548":
#                     date = classes.DateImport()
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "a":
#                                 date.datestring_raw = step2.text
#                             case "v":
#                                 date.date_comments = step2.text
#                             case "4":
#                                 if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
#                                     date.datetype = step2.text
#                     if date.datetype == "datl":
#                         date_preview = " (" + date.datestring_raw + ")"
#                     if date.datetype == "datw" and date_preview == "": # only shown in the preview if there is no datl
#                         date_preview = " (active: " + date.datestring_raw + ")" 
#                     pe.dates_from_source.append(date)
#                     print("Date as imported from GND: ")
#                     print(pe.dates_from_source)
#  #                   pe.dates_from_source.append(date)
#                     # If the GND contains the exact date ("datx"), it also gives the years only ("datl"). 
#                     # The latter should be removed later

"""
    datafields = find_datafields(record,"548")
    dates_from_source = []
    date = classes.DateImport()
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        if subfields:
            date.datestring_raw = subfields[0]
        subfields = find_subfields(datafield,"v")
        if subfields: 
            date.date_comments = subfields[0]
        subfields = find_subfields(datafield,"4")
        for subfield in subfields:
            if subfield[0:4] != "http":
                date.datetype = subfield
                break
        dates_from_source.append(date)
        # in the original version, I had also a date_preview field that had to be filled. 
        # One should either introduce such a field, or parse the dates straight away - 
        # the latter would make most sense. 
        # Since this function is not only used for persons but also for organisations, a potential
        # preview must not only cater for "datl" (no comments needed) and "datw" ("active "), 
        # but also for "datb" ("extant ")
        return (dates_from_source)
        

@classes.func_logger
def parse_gnd_profession(record, comments):

    #                 case "550": #This is used for professions or for general headings. This information is simply displayed in the "comment" field
#                     # so that it can be used to manually create the links I will need. 
#                     for step2 in step1:
#                         match step2.get('code'):
#                             case "a":
#                                 if pe.comments:
#                                     pe.comments = step2.text + "; " + pe.comments
#                                 else:
#                                     pe.comments = step2.text
# 
    datafields = find_datafields(record,"550")
    profession = ""
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        if subfields:
            for subfield in subfields: 
                profession = profession + "; " + subfield
    if profession[0:2] == "; ":
        profession = profession[2:]
    if comments == "":
        comments = profession
    else: 
        comments = comments + "; " + profession
    return comments


@classes.async_func_logger
async def find_and_parse_organisation_gnd(authority_url):
    """
This is largely a copy after the find_and_parse_person_gnd function. 
It is still untested. ONly few functions had to be written anew, most 
were reused from parsing person records. 
    """
    result = []
    content=await get_external_data.get_web_data(authority_url)
    root = etree.XML(content)
    records=root.find("records", namespaces=root.nsmap)
    for record in records:
        exclude = gnd_org_record_exclusion(record)
        if not exclude:
            print("found record")

            org_found=classes.Node()
            org_found.external_id.extend(gnd_record_get_gnd_internal_id(record))
            org_found.external_id.extend(gnd_record_get_external_references(record))
            org_found.name_preferred = gnd_org_record_get_name_preferred(record)
            org_found.name_variant = gnd_org_record_get_name_variant(record)
    #        org_found.gnd_id=gnd_record_get_gnd_id(record)
            org_found.type="Organisation"
    #        org_found.connected_persons =  gnd_record_get_connected_persons(record)
    #        org_found.connected_organisations = gnd_record_get_connected_orgs(record)
#           org_found.connected_places = gnd_record_get_connected_places(record)

            org_found.dates_from_source = get_gnd_dates(record)
            org_found.comments = parse_gnd_profession(record, org_found.comments)
            org_found.comments = get_gnd_comments(record, org_found.comments)
    #        print(org_found)

            connected_org = classes.Edge()
            connected_org.connection_type = "Candidate"
            connected_org.entityA = org_found
            result.append(connected_org)
    return result

@classes.func_logger
def gnd_org_record_exclusion(record):
    """
    This module checks two fields in the GND record - if one of them has a relevant entry, the entire 
    record is excluded from the list of candidates. 
                    case "075": # This entity type  is only important for removing records with entity type 'wis' from the search results - these are records for individual
                            # manuscripts, but have the same record type as organisations. 
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                entity = step2.text

                case "260":
                    cross_reference = True # Records with entries in this field should not be used

    """
    exclude = False
    datafields = find_datafields(record,"075")
    for datafield in datafields:
        subfields = find_subfields(datafield,"b")
        for subfield in subfields:
            if subfield == "wis":
                exclude = True
    
    datafields = find_datafields(record, "260")
    if datafields:
        exclude = True
    return exclude
    

@classes.async_func_logger
def gnd_org_record_get_name_preferred(record):
    """
    Takes the preferred name of an organisation
                case "110":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                org.name_preferred = step2.text                               
                            case "b": # probably used for subdivisions - I don't think this will happen often
                                org.name_preferred = org.name_preferred + " (" + step2.text + ")"
                            case "g": # used for the location of subdivisions - just in case it is necessary in some cases to avoid confusion
                                org.name_preferred = org.name_preferred + " (" + step2.text + ")"
                            case "x": # also sued for some subdivisions
                                org.name_preferred = org.name_preferred + " (" + step2.text + ")"

    """
    name_preferred = ""
    datafields = find_datafields(record,"110")
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        if subfields: 
            name_preferred = subfields[0]
        subfields = find_subfields(datafield,"b")
        if subfields: 
            name_preferred = name_preferred+ " (" + subfields[0] + ")"
        subfields = find_subfields(datafield,"g")
        if subfields: 
            name_preferred = name_preferred+ " (" + subfields[0] + ")"
        subfields = find_subfields(datafield,"x")
        if subfields: 
            name_preferred = name_preferred+ " (" + subfields[0] + ")"
    return (name_preferred)


@classes.func_logger
def gnd_org_record_get_name_variant(record):
    """
                    case "410":
                    name_subdivision = ""
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                name_variant = step2.text
                            case "b": # The numbering for rulers
                                name_subdivision =  " (" + step2.text + ")"
                    name_variant = name_variant + name_subdivision
                    for variant in org.name_variant:
                        if name_variant in variant:
                            name_variant = ""
                    if name_variant:
                        org.name_variant.append(name_variant)

                        """
    datafields = find_datafields(record,"410")
    variants = []
    for datafield in datafields:
        name_variant = ""
        subfields = find_subfields(datafield,"a")
        if subfields: 
            name_variant = subfields[0]
        subfields = find_subfields(datafield,"b")
        if subfields: 
            name_variant = name_variant + " (" + subfields[0] + ")"
        if name_variant not in variants:
            variants.append(name_variant)
    return (variants)



@classes.func_logger
def gnd_parsing_place_part_of_list(root): 
    """
Unfortunately, the search for places often yields several hundred results. Since the normal search function only downloads 100 results
per bathc, I may need to run it several times, and hence I have to call the search several times. 
In order to do so, I had to divide the function gnd_parsing_place. The function with this name now only launches one or more search options to bring back all results
and later filters out many irrelevant results that I annoyingly cannot exclude from the search. 
The longest part of the function the actual parsing of the XMl results, is moved to this function gnd_parsing_place_part_of_list. 
    """

    records=root.find("records", namespaces=root.nsmap)

    result = []
    for record in records:
#        print("arrived in parsing record")

        pl_found = classes.Node()
        entity_types = gnd_place_record_get_entity_type(record)
        if(("gik" in entity_types or "giz" in entity_types or "gxz" in entity_types) and "gil" not in entity_types):
            # This is for searching for towns. If I want to use this function later also for searching e.g., countries,
            # I have to create here different filters
            pl_found.external_id.extend(gnd_record_get_gnd_internal_id(record))
            pl_found.external_id.extend(gnd_record_get_external_references(record))
            pl_found.external_id.extend(gnd_place_record_get_geonames(record))
            #pl_found.coordinates = gnd_place_record_get_coordinates(record)
            # up to now, entity does not allow for coordinates, this has to change
            pl_found.name_preferred = gnd_place_record_get_name_preferred(record)
            pl_found.name_variant = gnd_place_record_get_name_variant(record)
    #        org_found.gnd_id=gnd_record_get_gnd_id(record)
            pl_found.type="Place"
    #        pl_found.connected_persons =  gnd_record_get_connected_persons(record)
    #        pl_found.connected_organisations = gnd_record_get_connected_orgs(record)
#           pl_found.connected_places = gnd_record_get_connected_places(record)

            pl_found.dates_from_source = get_gnd_dates(record) # just in case
            pl_found.comments = parse_gnd_profession(record, pl_found.comments)
            pl_found.comments = get_gnd_comments(record, pl_found.comments)
    #        print(org_found)

            connected_place = classes.Edge()
            connected_place.connection_type = "Candidate"
            connected_place.entityA = pl_found
            result.append(connected_place)

#            print(potential_places_list)
    return result

def gnd_place_record_get_entity_type(record):
    """
    The entity indicates if the place is a town or a building or a country etc.
    It thus determines, if a place should be parsed and entered into the list
    for selection.                 
                    case "075":
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                entity_list.append(step2.text)
    """
    entities = []
    datafields = find_datafields(record,"075")
    for datafield in datafields:
        subfields = find_subfields(datafield,"b")
        if subfields: 
            entities.append.subfields[0]
    return entities
    
def gnd_place_record_get_geonames(record):
    """ 
    The geonames id is stored in a separate field.                    
               case "024":
                    pl_id = classes.ExternalReference()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pl_id.external_id = step2.text
                            case "2":
                                pl_id.name = step2.text
                        if pl_id.name == "geonames":
                            pl_id.uri = "https://sws.geonames.org/" + pl_id.external_id
                            pl.external_id.append(pl_id)                            
"""
    external_references=[]
    datafields = find_datafields(record,"024")
    for datafield in datafields:
        external_reference = classes.ExternalReference()
        subfields = find_subfields(datafield,"a")
        if subfields: 
            external_reference.external_id = subfields[0]
        subfields = find_subfields(datafield,"2")
        if subfields:
            external_reference.name = subfields[0]
            if external_reference.name == "geonames":
                external_reference.uri = "https://sws.geonames.org/" + external_references.external_id
                external_references.append(external_reference)      
    return(external_references)

def gnd_place_record_get_coordinates(record):
    """
                case "034":
                    coordinates = classes.Coordinates()
                    pl_id = classes.ExternalReference()
                    for step2 in step1:
                        match step2.get('code'):
                            case "d": 
                                coordinates.west = step2.text
                            case "e": 
                                coordinates.east = step2.text
                            case "f":
                                coordinates.north = step2.text
                            case "g": 
                                coordinates.south = step2.text
                    pl.coordinates.append(coordinates)

    """
    coordinates_list=[]
    datafields = find_datafields(record,"034")
    for datafield in datafields:
        coordinates = classes.Coordinates()
        subfields = find_subfields(datafield,"d")
        if subfields:
            coordinates.west = subfields[0]
        subfields = find_subfields(datafield,"e")
        if subfields:
            coordinates.east = subfields[0]
        subfields = find_subfields(datafield,"f")
        if subfields:
            coordinates.north = subfields[0]
        subfields = find_subfields(datafield,"g")
        if subfields:
            coordinates.south = subfields[0]
        coordinates_list.append(coordinates)
    return coordinates_list
    
def gnd_place_record_get_name_preferred(record):
    """
                    case "151":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pl.name_preferred = step2.text                               
                            case "x" | "z": # some kind of subdivision, I don't know how often it will appear
                                pl.name_preferred = pl.name_preferred + " (" + step2.text + ") "

    """    
    name_preferred = []
    datafields = find_datafields(record,"151")
    for datafield in datafields:
        subfields = find_subfields(datafield,"a")
        if subfields:
            name_preferred = subfields[0]
        # "x" and "z" in subfields are for subdivisions of some kind
        # I have no clue if they ever occur in images relevant to me. 
        subfields = find_subfields(datafield,"x")
        if subfields:
            name_preferred = name_preferred + " (" + subfields[0] + ")"
        subfields = find_subfields(datafield,"z")
        if subfields:
            name_preferred = name_preferred + " (" + subfields[0] + ")"
    return name_preferred

def gnd_place_record_get_name_variant(record):
    """

                        case "451":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                name_variant = step2.text
                            case "i" | "x" | "z": # different comment fields
                                name_number =  " (" + step2.text + ") "
                    for variant in pl.name_variant:
                        if name_variant in variant:
                            name_variant = ""
                    if name_variant:
                        name_variant = name_variant + name_number
                        #just in case this name_number is ever used with places
                        pl.name_variant.append(name_variant)

    """
    variants = []
    datafields = find_datafields(record,"451")
    for datafield in datafields:
        name_variant = ""
        subfields = find_subfields(datafield,"a")
        if subfields: 
            name_variant = subfields[0]
        # I don't know if the subfields i, x and z ever contain any relevant information,
        # so I add them just in case. 
        subfields = find_subfields(datafield,"i")
        if subfields: 
            name_variant = name_variant + " )" + subfields[0] + ")"
        subfields = find_subfields(datafield,"x")
        if subfields: 
            name_variant = name_variant + " (" + subfields[0] + ")"
        subfields = find_subfields(datafield,"z")
        if subfields: 
            name_variant = name_variant + " (" + subfields[0] + ")"
        if name_variant not in variants:
            variants.append(name_variant)
    return (variants)



async def parse_place_gnd(authority_url):
    """
\todo

    """
    
    potential_places_list = []
    potential_places_list_complete = []
    search_term = authority_url[89:-61]
    if "%" in search_term: # If there was a word search, I only search for the first word
        search_term = search_term.split("%")[0]
    content=await get_external_data.get_web_data(authority_url)
    root = etree.XML(content)
    if root[1].text:      
        record_count = int(root[1].text)
    else:
        record_count = 0
    print('Number of records found')
    print(record_count)

    if record_count > 0:
        potential_places_list = gnd_parsing_place_part_of_list(root)

    if record_count > 100:
        record_count = record_count-100
        start_record = 101
        authority_url_basis = authority_url + "&startRecord="

#         authority_url_basis = authority_url[:-18] + "startRecord="
        while record_count > 0:
            authority_url = authority_url_basis + str(start_record)
            content=await get_external_data.get_web_data(authority_url)
            root = etree.XML(content)
            additional_potential_places_list = gnd_parsing_place_part_of_list(root)
            potential_places_list = potential_places_list + additional_potential_places_list
            record_count = record_count - 100
            start_record = start_record + 100
    if potential_places_list:
#        print("List of potential places: ")
#        print(potential_places_list)
        for place in potential_places_list:
            if search_term in place.name_preferred or len(potential_places_list) == 1:
#                print(place.name_preferred)
                potential_places_list_complete.append(place)   
    return potential_places_list_complete


#person = Person()
#person.id_name = "GND"
#person.id = "11900108X" #Lautensack
#person.role = "prt"
#person.id = "118650130" # Aristotle
#person.id = "118780743" #Louis XVIII
#person.name = "Lautensack, Paul"
#person.name = "Rubens, Peter Paul"
#person.name = "Andreas Asula"
#record = person_identification(person)
#organisation = Organisation()
#organisation.id_name = "GND"
#organisation.id = "2133444-4"
#record = organisation_identification(organisation)
#authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + organisation.id + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
#print(authority_url)
#record = gnd_parsing_organisation(authority_url)
#print(record)
#organisation.name = "Bamberg, Staatsbibliothek"
#authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Koe%3DBamberg,%20Staatsbibliothek%20%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
#record = gnd_parsing_organisation(authority_url)
#record = organisation_identification(organisation)
#print(record)
#authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D4086808-4%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
#place = Place()
#place.id_name = "GND"
#place.id = "4086808-4"
#place.name = "Frankfurt, Main"
#x = place_identification(place)

#print(x)


@classes.func_logger
async def identify_making_process(making_processes):
    """
    This module has bene primarily made for parsing information about the making process of a manuscript or printed book
    that had been entered manually during the ingest process. 
    If such information is added when working on individual records, it might be possible to adopt this module, but one would probably rather go directly
    to parsing the individual parts of it. 
    Manuscripts have by default one Making Process, Printed Books two (in theory three, but the third, printing, is already defined by bibliographic data
    and hence would not be added here). 
    Each making process has a number (currently as integer, although I wonder if one should not rather use a string to allow for e.g. 1a, 1b etc), 
    a process_type (the activity, e.g. design, blockcutting, etc.), and a process qualifier (e.g., none, attributed, follower of, etc.) - these two 
    will eventually probably belong drop-down fields. 
    It also has three fields that need parsing - one for a person (normally the artist), one for a place, and one for a date. 
    The person will be parsed similar to persons conntected to a book - but instead of the GND, the Getty ULAN would be the preferred source of information. 
    The place will be parsed as places conntected to a book (also here historical names), and the GND will also here be the principal source. 
    The date will be entered according to relatively simple rules that the editors would have to learn and would be parsed in a separate routine. 

    Eventually, two more fields will be added - the Medium, and the Illustrated Text.     
    """
    for making_process in making_processes:
        place = making_process.place
        if place.name != "":
            place.role = "Place of Making"
            place_new = await identify_place(place)
            print(place_new)
            making_process.place = place_new
        artist = making_process.person
        if artist.name != "":
            print("Artist found")
            print(artist.name)
            artist.role = "art"
            artist_new = await identify_person(artist)
            print(artist_new)
            making_process.person = artist_new
        date = making_process.date
        if date.datestring_raw != "":
            print("Date_found")
            print(date.datestring_raw)
            try:
                date_new = parse_date.parse_manually_entered_date(date.datestring_raw)
                making_process.date = date_new
            except classes.InvalidDateStringException as d:
                print(f"String could not be divided into individual dates: {d}")
            except classes.InvalidDateException as e:
                print(f"Failed to parse date string {e}")
            except classes.InvalidMonthException as f:
                print(f"Failed to parse date string {f}")
            except classes.InvalidDayException as g:
                print(f"Failed to parse date string {g}")
            except classes.InvalidDateRangeException as h:
                print(f"{h}")

    
    return making_processes

#class MarcxmlSubfield():
#    string : key
#    string : value


# @classes.func_logger
# def find_datafields(record,tag_id):
#     """
#     This function returns for a datafield in an MARCXML record a
#     hash with the subfields, where the key is the code attribute
#     and the value is the text in the subfield.
#     Note that there is only one subfield with the same key allowed
#     """
# #    results=np.array([])
#     print(tag_id)
#     datafields=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
# #    print(datafields)
#     for datafield in datafields:
#         subfields=datafield.findall("{*}subfield")
# #        subfield_hash={}
#         result=[]
#         for subfield in subfields:
#             key= subfield.get("code")
#             value=subfield.text

# #            subfield_hash[key].append(value)
#             s = [key,value]
#             print(s)
# #            print("Hash"+key+value)
#             result.append(s)
#         results = np.append(results,[result],0)
#     print("resulting datafields")
#     print(results)
#     return results

# @classes.func_logger
# def find_tuple(l,key):
#     r=[]
#     for e in l:
#         if e[0] == key:
#             print(e[0],e[1],key)
#             r.append(e[1])
#             print(r)
#     return r

def find_datafields(record,tag_id):
    datafields=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
    return datafields

def find_subfields(datafield,subfield_id):
    r=[]
    subfields=datafield.findall("{*}subfield")
    for subfield in subfields:
        key= subfield.get("code")
        value_raw=subfield.text
        value = parsing_helpers.turn_umlaut_to_unicode(value_raw)
        if key == subfield_id:
            r.append(value)
    return r
