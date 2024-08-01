import urllib.request
import requests
import xml.etree.ElementTree
from classes import *
import re
import dbactions
from dates_parsing import date_overall_parsing
from dates_parsing import artist_date_parsing
from dates_parsing import entered_date
import asyncio
import aiohttp
import ast
class InvalidDateException(Exception):
    pass

class InvalidMonthException(Exception):
    pass

class InvalidDayException(Exception):
    pass

class InvalidDateStringException(Exception):
    pass

class InvalidDateRangeException(Exception):
    pass




#from dbactions import *
url_replacement = {" " : "%20", "ä" : "%C3%A4", "ö" : "%C3%B6", "ü" : "%C3%BC", "Ä" : "%C3%84", "Ö" : "%C3%96", "Ü": "%C3%9C", \
                   "ß" : r"%C3%9F", "(" : "", ")" : "", "," : "",  "." : "" , "-" : "", \
                    "â": "%C3%A2", "ê" : "%C3%AA", "î" : "%C3%AE", "ô": "%C3%B4", "û" : "%C3%BB", "&" : "", \
                        "á" : "%C3%A1", "é" : "%C3%A9", "í" : "%C3%AD", "ó" : "%C3%B3", "ú": "%C3%BA", \
                        "à" : "%C3%A0", "è" : "%C3%A8", "ì": "%C3%AC", "ò" : "%C3%B2", "ù" : "%C3%B9", \
                        "Č" : "%C4%8C", "č" : "%C4%8D", "Ř": "%C5%98", "ř" : "%C5%99", "Š" : "%C5%A0", "š" : "%C5%A1"}  
#perhaps more signs will have to be added here later
# I also exclude "." - this is permitted in an URL, but the search dislikes it
role_person_type_correspondence = {"aut" : "Author", "edt" : "Author", "rsp" : "Author", "prt" : "Printer", "pbl" : "Printer", "art" : "Artist"}
role_org_type_correspondence = {"aut" : "Author", "edt" : "Author", "prt" : "Printer", "pbl" : "Printer", "col" : "Collection", "art" : "Artist"}
role_place_type_correspondence = {"pup" : "Town - historical", "mfp" : "Town - historical", "uvp" : "Town - historical", "Place of Making" : "Town - historical"}
#There is a problem - "Place of Making" could also go with "Region - historical" - I ignore that for the moment. 
from pymongo import MongoClient
encoding_list = {"Ö": "Ö", "ä": "ä", "ö": "ö", "ü": "ü", "é": "é"}


#This is only for stand-alone execution of functions in this module, in other cases, a connection to the database has already been made. 
#client = MongoClient("localhost", 27017)
#db = client.bpf
#coll = db.bpf

dbname = dbactions.get_database()
coll=dbname['bpf']


async def person_identification(person):
# This function is used for every person named in the bibliographic record (author, editor, printer etc.)
# It will first search if a record for this person is already in the MongoDB database, and then search in the GND
# If there is an ID-number (internal or GND, the search is done for the ID-number, otherwise for the name as string, and if this fails, for the name as key-words)
    candidates = []
    person.internal_id_person_type1_needed =  role_person_type_correspondence[person.role] 
    person.chosen_candidate = 999 # For some reason, I cannot return the form when 'chosen candidate' is empty. Hence, I put this in as a default setting. 
    if person.id:
        person_found = coll.find_one({"external_id": {"$elemMatch": {"name": person.id_name, "id": person.id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
        if person_found:            
            #print(person_found)
            person.internal_id = person_found["id"]
            person.internal_id_person_type1 = person_found["person_type1"]
            person.internal_id_preview = person_found["name_preferred"] + " (in Database)"
            # The date should be added, but I first have to write how it is to be parsed
            
            #The following is a warning that a matching person has the wrong type. 
            if person.internal_id_person_type1_needed not in person.internal_id_person_type1:
                person_type1_present = ""
                for type in person.internal_id_person_type1:
                    person_type1_present = person_type1_present + "' and '" + type + "'"
                person_type1_present = person_type1_present[5:]
                person.internal_id_person_type1_comment = "This person is currently catalogued as " + person_type1_present + ", but not as '" + person.internal_id_person_type1_needed + "'. The latter will be added if this record has been saved. " 
        else:
            if person.id_name == "GND": # I will have to create similar things for other authority files
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + person.id + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
                print("url for person search: ")
                print(authority_url)
                person.potential_candidates = gnd_parsing_person(authority_url)
    else:

        person.name = person.name.strip()
        for old, new in encoding_list.items():
            person.name = person.name.replace(old, new)
        candidates_result = coll.find({"name_preferred" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1})
        for candidate_result in candidates_result:
            candidate = Person_import()   
            candidate.internal_id = candidate_result["id"]
            candidate.name_preferred = candidate_result["name_preferred"]
            candidate.internal_id_person_type1 = candidate_result["person_type1"]
            candidate.preview = candidate.name_preferred + " (in Database)" # The years should be added once I have them
            print("Found as preferred name")
            print(candidate.internal_id)
            print(candidate.name_preferred)
            print(candidate.internal_id_person_type1)
            person.potential_candidates.append(candidate)
        candidates_result = coll.find({"name_variant" : person.name}, {"id": 1, "name_preferred" : 1, "person_type1" : 1}) 
        #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
        for candidate_result in candidates_result:
            candidate = Person_import()
            candidate.internal_id = candidate_result["id"]
            candidate.name_preferred = candidate_result["name_preferred"]
            candidate.internal_id_person_type1 = candidate_result["person_type1"]
            candidate.preview = candidate.name_preferred + " (in Database)" # Also here, the years should be added
            print("Found as variant: ")
            print(candidate.internal_id)
            print(candidate.name_preferred)
            print(candidate.internal_id_person_type1)
            candidate_duplicate = False
            for extant_candidate in person.potential_candidates:
                if extant_candidate.name_preferred == candidate.name_preferred:
                    candidate_duplicate = True
            if candidate_duplicate == False:             
                person.potential_candidates.append(candidate)
                #print(person.potential_candidates)
            for candidate in person.potential_candidates:
                if person.internal_id_person_type1_needed not in candidate.internal_id_person_type1:
                    person_type1_present = ""
                    for type in candidate.internal_id_person_type1:
                        person_type1_present = person_type1_present + "' and '" + type + "'"
                    person_type1_present = person_type1_present[5:]
                    candidate.internal_id_person_type1_comment = "This person is currently catalogued as " + person_type1_present + ", but not as '" + person.internal_id_person_type1_needed + "'. The latter will be added if this record has been saved. " 
        if person.internal_id_person_type1_needed != "Artist":
            if not person.potential_candidates: #if nothing has been found in the database
                print("No person found")
                person_name_search = person.name
                for old, new in url_replacement.items():
                    person_name_search = person_name_search.replace(old, new)
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Per%3D' + person_name_search + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
                print(authority_url)
                person.potential_candidates = gnd_parsing_person(authority_url)
            if not person.potential_candidates: #if still nothing has been found, a keyword search is performed instead of a string search. 
                name_divided = person_name_search.split("%20")
                name_query = ""           
                for word in name_divided:
                    if word != "": #necessary, otherwise there will be error messages
                        search_phrase = r"Per=" + word + r"%20and%20" # I don't get it, but the thing only works if the "=" is written as such and not as Percent code. Above, it is different. 
                        name_query = name_query + search_phrase
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=' + name_query + r'BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'    
                print(authority_url)
                new_potential_candidates = gnd_parsing_person(authority_url)
                person.potential_candidates = person.potential_candidates + new_potential_candidates
        else:
            if not person.potential_candidates:
                person = await ulan_search(person)
    if len(person.potential_candidates) == 1: # If there is only one entry for this person, it is by default selected (although the user can also run a new search, once this is established)
        person.chosen_candidate = 0
    print("new person record")
    print(person)
    return person         
                

def additional_person_identification(new_authority_id, role):
    # This function is used for any additional authority records that are suggested as identifications for persons connected to a book.
    # Normally, they are parsed with gnd_parsing_person - but beforehand it is checked if they are already in Iconobase and have not been found for whatever reason. 
    # Currently all records must come from the GND - if other authority files are included, this function has to be changed. 
    new_authority_id = new_authority_id.strip()
    potential_persons_list = []
    potential_person = Person_import()
    person_found = coll.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": new_authority_id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
    if person_found:            
        #print(person_found)
        potential_person.internal_id = person_found["id"]
        potential_person.internal_id_person_type1 = person_found["person_type1"]
        potential_person.preview = person_found["name_preferred"] # The date should be added, but I first have to write how it is to be parsed
        internal_id_person_type1_needed =  role_person_type_correspondence[role]
        if internal_id_person_type1_needed not in potential_person.internal_id_person_type1: 
            person_type1_present = ""
            for type in potential_person.internal_id_person_type1:
                person_type1_present = person_type1_present + "' and '" + type + "'"
            person_type1_present = person_type1_present[5:]
            potential_person.internal_id_person_type1_comment = "This person is currently catalogued as " + person_type1_present + ", but not as '" \
                + internal_id_person_type1_needed + "'. The latter will be added if this record has been saved. " 
        potential_persons_list.append(potential_person)

    else: 
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
        potential_persons_list = gnd_parsing_person(authority_url)
    #print("added person")
    #print(potential_persons_list)
    return(potential_persons_list)





def organisation_identification(organisation):
# This function is used for every organisation named in the bibliographic record (printer etc.), and in addition for the repository of a book or manuscript
# It will first search if a record for this organisation is already in the MongoDB database, and then search in the GND
# If there is an ID-number (internal or GND, the search is done for the ID-number, otherwise for the name as string, and if this fails, for the name as key-words)
    candidates = []
    print("Starting organisatin_identification for repository")
    organisation.internal_id_org_type1_needed = role_org_type_correspondence[organisation.role]
    organisation.chosen_candidate = 999 # For some reason, this must not be empty
    if organisation.id:
        organisation_found = coll.find_one({"external_id": {"$elemMatch": {"name": organisation.id_name, "id": organisation.id}}}, {"id": 1, "name_preferred": 1, "org_type1": 1})
        if organisation_found:
            organisation.internal_id = organisation_found["id"]
            organisation.internal_id_preview = organisation_found["name_preferred"] + " (in Database)"
            organisation.internal_id_org_type1 = organisation_found["org_type1"]
            org_type1_needed =  role_org_type_correspondence[organisation.role] 
            
            #The following is a warning that a matching person has the wrong type. 
            if org_type1_needed not in organisation.internal_id_org_type1:
                org_type1_present = ""
                for type in organisation.internal_id_org_type1:
                    org_type1_present = org_type1_present + "' and '" + type
                    org_type1_present = org_type1_present[5:] + "'"
                organisation.internal_id_org_type1_comment = "This organisation is currently catalogued as " + org_type1_present + ", but not as '" + org_type1_needed + "'. The latter will be added if this record has been saved. " 

        else:
            if organisation.id_name == "GND": # I will have to create similar things for other authority files
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + organisation.id + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
                print(authority_url)
                organisation.potential_candidates = gnd_parsing_organisation(authority_url)
    else:
        print("No repository ID")
        organisation.name = organisation.name.strip()
        candidates_result = (coll.find({"name_preferred" : organisation.name}, {"id": 1, "name_preferred" : 1, "org_type1" : 1}))
        print("Search for repository candidate completed")
        for candidate_result in candidates_result:
            candidate = Organisation_import()   
            candidate.internal_id = candidate_result["id"]
            candidate.name_preferred = candidate_result["name_preferred"]
            candidate.preview = candidate_result["name_preferred"] + " (in Database)"
            candidate.internal_id_org_type1 = candidate_result["org_type1"]
            print("orgtype1 in search for name_preferred: ")
            print(candidate.preview)
            print(candidate.internal_id_org_type1)
            organisation.potential_candidates.append(candidate)
        candidates_result = coll.find({"name_variant" : organisation.name}, {"id": 1, "name_preferred" : 1, "org_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
        for candidate_result in candidates_result:
            candidate = Organisation_import()   
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
            if candidate_duplicate == False:
                    
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
                    for type in candidate.internal_id_org_type1:
                        org_type1_present = org_type1_present + "' and '" + type + "'"
                    org_type1_present = org_type1_present[5:]
                    candidate.internal_id_org_type1_comment = "This organisation is currently catalogued as "\
                          + org_type1_present + ", but not as '" + organisation.internal_id_org_type1_needed + "'. The latter will be added if this record has been saved. " 

        if not organisation.potential_candidates: #if nothing has been found in the database
            organisation_name_search = organisation.name
            for old, new in url_replacement.items():
                organisation_name_search = organisation_name_search.replace(old, new)
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Koe%3D' + organisation_name_search + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'          
            organisation.potential_candidates = gnd_parsing_organisation(authority_url)        
            name_divided = organisation_name_search.split("%20")
            name_query = ""           
            for word in name_divided:
                if word != "":    
                    search_phrase = r"Koe=" + word + r"%20and%20" # I don't get it, but the thing only works if the "=" is written as such and not as Percent code. Above, it is different. 
                    name_query = name_query + search_phrase
#                    print ("name query:" + name_query)
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=' + name_query + r'BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'    
      
            new_potential_candidates = gnd_parsing_organisation(authority_url)
            for candidate in new_potential_candidates:
                if candidate not in organisation.potential_candidates: #I need this distinction because I perform both a string and a keyword search, and both may yield the same results
                    organisation.potential_candidates.append(candidate)
    if len(organisation.potential_candidates) == 1: # If there is only one entry for this organisation, it is by default selected (although the user can also run a new search, once this is established)
        organisation.chosen_candidate = 0
        
    return organisation

def additional_organisation_identification(new_authority_id, role):
    # This function is used for any additional authority records that are suggested as identifications for organisations connected to a book.
    # Normally, they are parsed with gnd_parsing_organisation - but beforehand it is checked if they are already in Iconobase and have not been found for whatever reason. 
    # Currently all records must come from the GND - if other authority files are included, this function has to be changed. 
    new_authority_id = new_authority_id.strip()
    potential_orgs_list = []
    potential_org = Person_import()
    org_found = coll.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": new_authority_id}}}, {"id": 1, "name_preferred": 1, "org_type1" : 1})
    if org_found:            
        print(org_found)
        potential_org.internal_id = org_found["id"]
        potential_org.internal_id_org_type1 = org_found["org_type1"]
        potential_org.preview = org_found["name_preferred"] # The date should be added, but I first have to write how it is to be parsed
        internal_id_org_type1_needed =  role_org_type_correspondence[role]
        if internal_id_org_type1_needed not in potential_org.internal_id_org_type1: 
            org_type1_present = ""
            for type in potential_org.internal_id_org_type1:
                org_type1_present = org_type1_present + "' and '" + type + "'"
            org_type1_present = org_type1_present[5:]
            potential_org.internal_id_org_type1_comment = "This organisation is currently catalogued as " + org_type1_present + ", but not as '" \
                + internal_id_org_type1_needed + "'. The latter will be added if this record has been saved. " 
        else:
            internal_id_org_type1_needed = ""
        potential_orgs_list.append(potential_org)
    else: 
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
        potential_orgs_list = gnd_parsing_organisation(authority_url)

    return(potential_orgs_list)



                

def place_identification(place):
# This function is used for every place named in the bibliographic record (place of publishing / manufacture)
# It will first search if a record for this place is already in the MongoDB database, and then search in the GND
# If there is an ID-number (internal or GND, the search is done for the ID-number, otherwise for the name as string, and if this fails, for the name as key-words)
# Note that the GND parser combined with it suppresses all records to regions - if this mechanism is later also used for identifying regions, this might need to be changed
# Since there are often many locations connected toa town (e.g., all villages in its district), I increase the number of hits from the GND to 400 and sort them alphabetically. 
    if place.role:
        print(place.role)
    else:
        print("No place.role")
        place.role = "pup" # I just define this for the time being. 
    place.internal_id_place_type1_needed =  role_place_type_correspondence[place.role] 
    place.chosen_candidate = 999
    print("Arrived in place_identification")
    if place.id:
        place_found = coll.find_one({"external_id": {"$elemMatch": {"name": place.id_name, "id": place.id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
        if place_found:
            place.internal_id = place_found["id"]
            place.internal_id_preview = place_found["name_preferred"] + " (in Database)"
            place.internal_id_place_type1 = place_found["place_type1"] 
#            print('Place data:')
#            print(place.internal_id_place_type1)           
            place_type1_needed =  role_place_type_correspondence[place.role] #The following is a warning that a matching place has the wrong type. It should also be 
            # included for all searches for names in Iconobase, but I don't build this yet since there aren't any records in it that allow my to try it out. 
            # This option has not been tried out properly since places rarely come with GND numbers
            if place_type1_needed not in place.internal_id_place_type1:
                place_type1_present = ""
                for type in place.internal_id_place_type1:
                    place_type1_present = place_type1_present + "' and '" + type
                place_type1_present = place_type1_present[5:] + "'"

                place.internal_id_place_type1_comment = "This place is currently catalogued as " + place_type1_present + ", but not as '" + place_type1_needed + "'. \
                    An additional record for " + place_type1_needed + " will be produced if this record is saved. " 
        else:
            if place.id_name == "GND": # I will have to create similar things for other authority files
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + place.id + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
                print("authority_url with Gnd number: " + authority_url)
                place.potential_candidates = gnd_parsing_place(authority_url)              
    else:
        print("place name has no ID")
        place.name = place.name.strip()
        candidates_result = coll.find({"name_preferred" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1})
        for candidate_result in candidates_result:           
            candidate = Place_import()   
            candidate.internal_id = candidate_result["id"]
            print("candidate found through name search in database (preferred name)" + candidate.internal_id)
            candidate.preview = candidate_result["name_preferred"] + " (in Database)"
            candidate.internal_id_place_type1 = candidate_result["place_type1"]
            place.potential_candidates.append(candidate)
        candidates_result = coll.find({"name_variant" : place.name}, {"id": 1, "name_preferred" : 1, "place_type1" : 1}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
        for candidate_result in candidates_result:
            candidate = Place_import()   
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
                    for type in candidate.internal_id_place_type1:
                        place_type1_present = place_type1_present + "' and '" + type + "'"
                    place_type1_present = place_type1_present[5:]


                    candidate.internal_id_place_type1_comment = "This place is currently catalogued as " + place_type1_present + ", but not as '" + place.internal_id_place_type1_needed + "'. \
                    An additional record for " + place.internal_id_place_type1_needed + " will be produced if this place is selected and the record is saved. " 

        if not place.potential_candidates: #if nothing has been found
            print("Candidate not found in database")
            place_name_search = place.name.strip()
            for old, new in url_replacement.items():
                place_name_search = place_name_search.replace(old, new)
                #print("Search term for place :x" + place_name_search + "x")
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Geo%3D' + place_name_search + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
            print('URL for place name search : '+ authority_url)
            place.potential_candidates = gnd_parsing_place(authority_url)
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
            additional_potential_candidates = gnd_parsing_place(authority_url)
            print("Number or additional potential candidates: ")
            print(len(additional_potential_candidates))
            for additional_candidate in additional_potential_candidates:
                if additional_candidate not in place.potential_candidates:
                    place.potential_candidates.append(additional_candidate)
    place.potential_candidates = sorted(place.potential_candidates, key = lambda candidate : candidate.preview)
    if len(place.potential_candidates) == 1: # If there is only one entry for this person, it is by default selected (although the user can also run a new search, once this is established)
        place.chosen_candidate = 0
    return place


def additional_place_identification(new_authority_id, role):
    # This function is used for any additional authority records that are suggested as identifications for organisations connected to a book.
    # Normally, they are parsed with gnd_parsing_place - but beforehand it is checked if they are already in Iconobase and have not been found for whatever reason. 
    # Currently all records must come from the GND - if other authority files are included, this function has to be changed. 
    new_authority_id = new_authority_id.strip()
    potential_places_list = []
    potential_place = Place_import()
    place_found = coll.find_one({"external_id": {"$elemMatch": {"name": "GND", "id": new_authority_id}}}, {"id": 1, "name_preferred": 1, "place_type1" : 1})
    if place_found:            
#        print(place_found)
        potential_place.internal_id = place_found["id"]
        potential_place.internal_id_place_type1 = place_found["place_type1"]
        potential_place.preview = place_found["name_preferred"] + " (in Database)" 
        internal_id_place_type1_needed =  role_place_type_correspondence[role]
        if internal_id_place_type1_needed not in potential_place.internal_id_place_type1: 
            place_type1_present = ""
            for type in potential_place.internal_id_place_type1:
                place_type1_present = place_type1_present + "' and '" + type + "'"
            place_type1_present = place_type1_present[5:]
            potential_place.internal_id_place_type1_comment = "This place is currently catalogued as " + place_type1_present + ", but not as '" \
                + internal_id_place_type1_needed + "'. An additional record for " + internal_id_place_type1_needed + " will be produced if this place is selected and the record is saved. "
        potential_places_list.append(potential_place)
    else: 
        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
#        print("authority URL in additional_place_identification")
#        print(authority_url)
        potential_places_list = gnd_parsing_place(authority_url)
#        print("Potential places list in additional_place_identification: ")
#        print(potential_places_list)
    return(potential_places_list)




def gnd_parsing_person(authority_url):
    print("arrived in gnd_parsing_person")
    potential_persons_list = []
    url = urllib.request.urlopen(authority_url)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    #print(root)
    
    for record in root[2]:
        print("Parsing person information")
        pe = Person_import()
        comment = ""
        date_preview = ""
        ortg_preview = ""
        orts_preview = ""
        ortw_preview = ""
        name_variant_preview = ""
        comments_preview = ""
        for step1 in record[2][0]:
            match step1.get('tag'):
#                case "001":
#                    pe_id = External_id()
#                    pe_id.name = "GND_intern"
#                    pe_id.id = step1.text
#                    pe_id.uri = "GND_intern" + step1.text                    
#                    pe.external_id.append(pe_id)

                case "035":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pe_id = External_id()
                                pe_id.name = "GND"
                                if step2.text[0:8] == "(DE-588)":
                                    pe_id.id = step2.text[8:] #The latter cuts out the prefix '(DE-588)'.
                                    pe_id.uri = r'https://d-nb.info/gnd/' + pe_id.id
                                    duplicate_id = False  # Sometimes, the record containing the GND ID appears twice, hence it should not be added a second time. 
                                    for id_duplicate in pe.external_id:
                                        if id_duplicate.uri == pe_id.uri:
                                            duplicate_id = True
                                    if not duplicate_id:
                                        pe.external_id.append(pe_id)
#                                    if not pe.external_id: #
#                                        pe.external_id.append(pe_id)
                                # Quite often, there are several GND records for one person, and if discovered, they are merged, and all GND IDs but become obsolete.
                                # However, they are still stored in the record (035z) and are found by the search. 
                                # Hence, this ID may be different from the person.id I used for the search in the first place.
                                # Annoyingly, the search also finds IDs from the old database PND. If it is possible that a PND ID is the same as the GND ID of a 
                                # different record, I have to include a function to delete this record from the results (I am enquiring if this is the case)
                case "100":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pe.name_preferred = step2.text                               
                            case "b": # The numbering for rulers
                                pe.name_preferred = pe.name_preferred + " " + step2.text
                            case "c": # For rulers, comments on Territory, title and time of ruling. However, 
                                # I put that now into a comment field. Once I have all the structure for persons' offices I might try to make an automatic import,
                                # but I fear it is too messy to make it worthwhile. 
                                if not ("Kaiser" in step2.text or "König" in step2.text or "Herzog" in step2.text or "Kurfürst" in step2.text or "Markgraf" in step2.text or \
                                        "Bischof" in step2.text or "Fürstbischof" in step2.text or "Erzbischof" in step2.text or "Fürsterzbischof" in step2.text or "Abt" in step2.text):
                                    pe.name_preferred = pe.name_preferred + " (" +  step2.text + ")"
                                else:
                                    pe.comments = step2.text

                case "375":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                if step2.text == "1":
                                    pe.sex = "male"
                                if step2.text == "2":
                                    pe.sex = "female"
                case "400":
                    name_number = ""
                    name_comment = ""
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                name_variant = step2.text
                            case "b": # The numbering for rulers
                                name_number =  " " + step2.text
                            case "c": # For rulers, comments on Territory, title and time of ruling. 
                                # I put that now into a comment field. Once I have all the structure for persons' offices I might try to make an automatic import,
                                # but I fear it is too messy to make it worthwhile.                                
                                comment = step2.text
                                if " von " in comment or " of " in comment or " de " in comment or "," in comment: # This field can contain either an additional epithet or the territory and title of a ruler. The former will be stored
                                    # as part of the name, the latter will be relegated to the comment field. 
                                    # As a rough way of discerning both, anything with "von", "of" or "de" or a comma is regarded as belonging to a ruler
                                    if comment not in pe.comments:
                                        pe.comments = pe.comments + " / " + comment
                                else: 
                                    name_comment = " (" + comment + ")"
#                                    name_variant = name_variant + name_number + " (" + comment + ")"
                    name_variant = name_variant + name_number + name_comment
                    for variant in pe.name_variant:
                        if name_variant in variant:
                            name_variant = ""
                    if name_variant:
                        pe.name_variant.append(name_variant)
                case "500":
                    conn_pe = Connected_entity()
                    conn_pe.external_id = []
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id = External_id()
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_pe.external_id.append(conn_id)

                            case "a":
                                conn_pe.name = step2.text
                            case "b": 
                                conn_pe.name = conn_pe.name + " " + step2.text
                            case "c": 
                                conn_pe.name = conn_pe.name + "(" + step2.text + ")" #in this case I add this to the name
                            # since it may make clear who the person is. 
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_pe.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_pe.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_pe.connection_time = step2.text[2:]
                    if "VD-16 Mitverf." not in conn_pe.connection_comment: 
                            # someone connected all persons who appear together as authors in the VD16,
                            # I want them removed. 
                        pe.connected_persons.append(conn_pe)
                case "510":
                    conn_org = Connected_entity()
                    conn_org.external_id = []
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id = External_id()
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_org.external_id.append(conn_id)
                            case "a": 
                                conn_org.name = step2.text
                            case "b": #for sub-units of organisations - no clue if this will ever happen in my circumstances
                                conn_org.name = conn_org.name + " (" + step2.text + ")"
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_org.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_org.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_org.connection_time = step2.text[2:]
                    pe.connected_organisations.append(conn_org)
                case "548":
                    date = Date_import()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                date.datestring_raw = step2.text
                            case "v":
                                date.date_comments = step2.text
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    date.datetype = step2.text
                    if date.datetype == "datl":
                        date_preview = " (" + date.datestring_raw + ")"
                    if date.datetype == "datw" and date_preview == "": # only shown in the preview if there is no datl
                        date_preview = " (active: " + date.datestring_raw + ")" 
                    pe.dates_from_source.append(date)
                    print("Date as imported from GND: ")
                    print(pe.dates_from_source)
 #                   pe.dates_from_source.append(date)
                    # If the GND contains the exact date ("datx"), it also gives the years only ("datl"). 
                    # The latter should be removed later
                case "550": #This is used for professions or for general headings. This information is simply displayed in the "comment" field
                    # so that it can be used to manually create the links I will need. 
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                if pe.comments:
                                    pe.comments = step2.text + "; " + pe.comments
                                else:
                                    pe.comments = step2.text
                case "551":
                    conn_pl = Connected_entity()
                    conn_id = External_id()
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_pl.external_id.append(conn_id)
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                            case "a": 
                                conn_pl.name = step2.text
                            case "g": 
                                conn_pl.name = conn_pl.name + " (" + step2.text + ")"
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_pl.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_pl.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_pl.connection_time = step2.text[2:]
                    if conn_pl.connection_type == "ortg":
                        ortg_preview = ", born in " + conn_pl.name
                    if conn_pl.connection_type == "orts":
                        orts_preview = ", died in " + conn_pl.name
                    if conn_pl.connection_type == "ortw":
                        ortw_preview = ", active in " + conn_pl.name
                    pe.connected_locations.append(conn_pl)
                case "678":
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                if pe.comments:
                                    pe.comments = step2.text + "; " + pe.comments
                                else:
                                    pe.comments = step2.text
        #if pe.dates_from_source:
            #pe.dates = dates_parsing(pe.dates_from_source)
        if pe.comments:                
            comments_preview = " (" + pe.comments + ")"
        if pe.name_variant:
            name_variant_preview = ", also called: "
            for variant in pe.name_variant:
                name_variant_preview = name_variant_preview + variant + "; "
            name_variant_preview = name_variant_preview[:-2]
        

        pe.preview = pe.name_preferred + date_preview + ortg_preview + ortw_preview + orts_preview + name_variant_preview + comments_preview
        potential_persons_list.append(pe)
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

                


        
    #record = root[2][0][2][0][0]
    #print(record.text)
    #print("potential persons list made")
    return potential_persons_list




def gnd_parsing_organisation(authority_url):
    potential_organisations_list = []
    print("organisation-authority: " + authority_url)
    url = urllib.request.urlopen(authority_url)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    record_number = 0
    for record in root[2]:
        org = Organisation_import()
        comment = ""
        date_preview = ""
        orta_preview = ""
        geow_preview = ""
        vorg_preview = ""
        nach_preview = ""
        name_variant_preview = ""
        comments_preview = ""
        cross_reference = False
#        print("Number of record:")
#        print(record_number)
        record_number = record_number + 1
        for step1 in record[2][0]:
            match step1.get('tag'):
#                case "001":
#                    org_id = External_id()
#                    org_id.name = "GND_intern"
#                    org_id.id = step1.text
#                    org_id.uri = "GND_intern" + step1.text
#                    org.external_id.append(org_id)
                case "035":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                org_id = External_id()
                                org_id.name = "GND"
                                if step2.text[0:8] == "(DE-588)":
                                    org_id.id = step2.text[8:] #The latter cuts out the prefix '(DE-588)'.
                                    org_id.uri = r'https://d-nb.info/gnd/' + org_id.id
                                    duplicate_id = False  # Sometimes, the record containing the GND ID appears twice, hence it should not be added a second time. 
                                    for id_duplicate in org.external_id:
                                        if id_duplicate.uri == org_id.uri:
                                            duplicate_id = True
                                    if not duplicate_id:
                                        org.external_id.append(org_id)

#                                    if not org.external_id: 
#                                        org.external_id.append(org_id)
                                # Quite often, there are several GND records for one organisation, and if discovered, they are merged, and all GND IDs but become obsolete.
                                # However, they are still stored in the record (035z) and are found by the search. 
                                # Hence, this ID may be different from the organisation.id I used for the search in the first place.
                                # Annoyingly, the search also finds IDs from the old database GKD. If it is possible that a GKD ID is the same as the GND ID of a 
                                # different record, I have to include a function to delete this record from the results (I am enquiring if this is the case)
                case "075": # This entity type  is only important for removing records with entity type 'wis' from the search results - these are records for individual
                            # manuscripts, but have the same record type as organisations. 
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                entity = step2.text
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

                case "260":
                    cross_reference = True # Records with entries in this field should not be used
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
                case "500":
                    conn_pe = Connected_entity()
                    conn_pe.external_id = []
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id = External_id()
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_pe.external_id.append(conn_id)

                            case "a":
                                conn_pe.name = step2.text
                            case "b": 
                                conn_pe.name = conn_pe.name + " " + step2.text
                            case "c": 
                                conn_pe.name = conn_pe.name + "(" + step2.text + ")" #in this case I add this to the name
                            # since it may make clear who the person is. 
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_pe.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_pe.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_pe.connection_time = step2.text[2:]
                    org.connected_persons.append(conn_pe)
                case "510":
                    conn_org = Connected_entity()
                    conn_org.external_id = []
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id = External_id()
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_org.external_id.append(conn_id)
                            case "a": 
                                conn_org.name = step2.text
                            case "b": #for sub-units of organisations - no clue if this will ever happen in my circumstances
                                conn_org.name = conn_org.name + " (" + step2.text + ")"
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_org.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_org.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_org.connection_time = step2.text[2:]
                    if conn_org.connection_type == "vorg":
                        vorg_preview = ", (precursor: " + conn_org.name + ")"
                    if conn_org.connection_type == "nach":
                        nach_preview = ", (successor: " + conn_org.name + ")"
                    org.connected_organisations.append(conn_org)
                case "548":
                    date = Date_import()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                date.datestring = step2.text
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    date.datetype = step2.text
                    if date.datetype == "datb" : 
                        date_preview = " (extant: " + date.datestring + ")" 
                    org.dates_from_source.append(date)
                case "550": #This is used for professions or for general headings. This information is simply displayed in the "comment" field
                    # so that it can be used to manually create the links I will need. 
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                if org.comments:
                                    org.comments = step2.text + "; " + org.comments
                                else:
                                    org.comments = step2.text
                case "551":
                    conn_pl = Connected_entity()
                    conn_id = External_id()
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_pl.external_id.append(conn_id)
                            case "a": 
                                conn_pl.name = step2.text
                            case "g": 
                                conn_pl.name = conn_pl.name + " (" + step2.text + ")"
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_pl.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_pl.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_pl.connection_time = step2.text[2:]
                    if conn_pl.connection_type == "orta":
                        orta_preview = ", located in " + conn_pl.name
                    if conn_pl.connection_type == "geow":
                        geow_preview = ", responsible for " + conn_pl.name
                    org.connected_locations.append(conn_pl)
                case "678":
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                if org.comments:
                                    org.comments = step2.text + "; " + org.comments
                                else:
                                    org.comments = step2.text
        if org.comments:                
            comments_preview = " (" + org.comments + ")"
        if org.name_variant:
            name_variant_preview = ", also called: "
            for variant in org.name_variant:
                name_variant_preview = name_variant_preview + variant + "; "
            name_variant_preview = name_variant_preview[:-2]

        org.preview = org.name_preferred + date_preview + vorg_preview + nach_preview + orta_preview + geow_preview + name_variant_preview + comments_preview
        if entity != "wis" and not cross_reference: # 'wis' means catalogue entries of manuscripts. For strange reasons, they are found through the same search pattern as the libraries
            # and thus have to be weeded out here. 
            potential_organisations_list.append(org)
    print("This list comes from gnd parsing, thus very early on")    
    print(potential_organisations_list)
    return(potential_organisations_list)


def gnd_parsing_place_part_of_list(root): # Unfortunately, the search for places often yields several hundred results. Since the normal search function only downloads 100 results
    # per bathc, I may need to run it several times, and hence I have to call the search several times. 
    # In order to do so, I had to divide the function gnd_parsing_place. The function with this name now only launches one or more search options to bring back all results
    # and later filters out many irrelevant results that I annoyingly cannot exclude from the search. 
    # The longest part of the function the actual parsing of the XMl results, is moved to this function gnd_parsing_place_part_of_list. 
    potential_places_list = []
    for record in root[2]:
#        print("arrived in parsing record")
        pl = Place_import()
        comment = ""
        obpa_preview = ""
        adue_preview = ""
        vorg_preview = ""
        nach_preview = ""
        name_variant_preview = ""
        comments_preview = ""
        entity_list = []
        for step1 in record[2][0]:
            match step1.get('tag'):
#                case "001":
#                    pl_id = External_id()
#                    pl_id.name = "GND_intern"
#                    pl_id.id = step1.text
#                    pl_id.uri = "GND_intern" + step1.text
#                    pl.external_id.append(pl_id)                
                case "024":
                    pl_id = External_id()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pl_id.id = step2.text
                            case "2":
                                pl_id.name = step2.text
                        if pl_id.name == "geonames":
                            pl_id.uri = "https://sws.geonames.org/" + pl_id.id
                            pl.external_id.append(pl_id)                            
                case "034":
                    coordinates = Coordinates()
                    pl_id = External_id()
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
                case "035":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pl_id = External_id()
                                pl_id.name = "GND"
                                if step2.text[0:8] == "(DE-588)":
                                    pl_id.id = step2.text[8:] #The latter cuts out the prefix '(DE-588)'.   
                                    pl_id.uri = r'https://d-nb.info/gnd/' + pl_id.id                          
                                    pl.external_id.append(pl_id)
                        
                                # Quite often, there are several GND records for one place, and if discovered, they are merged, and all GND IDs but become obsolete.
                                # However, they are still stored in the record (035z) and are found by the search. 
                                # Hence, this ID may be different from the person.id I used for the search in the first place.
                                # Annoyingly, the search also finds IDs from the old database . If it is possible that a PND ID is the same as the GND ID of a 
                                # different record, I have to include a function to delete this record from the results (I am enquiring if this is the case)
                case "075":
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                entity_list.append(step2.text)
                case "151":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pl.name_preferred = step2.text                               
                            case "x" | "z": # some kind of subdivision, I don't know how often it will appear
                                pl.name_preferred = pl.name_preferred + " (" + step2.text + ") "
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
                        pl.name_variant.append(name_variant)
                case "500":
                    conn_pe = Connected_entity()
                    conn_pe.external_id = []
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id = External_id()
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id               
                                    conn_pe.external_id.append(conn_id)

                            case "a":
                                conn_pe.name = step2.text
                            case "b": 
                                conn_pe.name = conn_pe.name + " " + step2.text
                            case "c": 
                                conn_pe.name = conn_pe.name + "(" + step2.text + ")" #in this case I add this to the name
                            # since it may make clear who the person is. 
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_pe.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_pe.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_pe.connection_time = step2.text[2:]
                    if "VD-16 Mitverf." not in conn_pe.connection_comment: 
                            # someone connected all persons who appear together as authors in the VD16,
                            # I want them removed. 
                        pl.connected_persons.append(conn_pe)
                case "510":
                    conn_org = Connected_entity()
                    conn_org.external_id = []
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id = External_id()
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_org.external_id.append(conn_id)
                            case "a": 
                                conn_org.name = step2.text
                            case "b": #for sub-units of organisations - no clue if this will ever happen in my circumstances
                                conn_org.name = conn_org.name + " (" + step2.text + ")"
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_org.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_org.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_org.connection_time = step2.text[2:]
                    pl.connected_organisations.append(conn_org)
                case "548": #I wonder if this is ever used for places
                    date = Date_import()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                date.datestring = step2.text
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    date.datetype = step2.text
                    if date.datetype == "datb":
                        date_preview = " (extant" + date.datestring + ")"
                case "550": #This is used for general headings. This information is simply displayed in the "comment" field
                    # so that it can be used to manually create the links I will need. 
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                if pl.comments:
                                    pl.comments = step2.text + "; " + pl.comments
                                else:
                                    pl.comments = step2.text
                case "551":
                    conn_pl = Connected_entity()
                    conn_id = External_id()
                    for step2 in step1:
                        match step2.get('code'):
                            case "0":
                                if step2.text[0:8] == "(DE-588)":
                                    conn_id.name = "GND"
                                    conn_id.id = step2.text[8:]
                                    conn_id.uri =  r'https://d-nb.info/gnd/' + conn_id.id
                                    conn_pl.external_id.append(conn_id)
                            case "a": 
                                conn_pl.name = step2.text
                            case "g": 
                                conn_pl.name = conn_pl.name + " (" + step2.text + ")"
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    conn_pl.connection_type = step2.text
                            case "9": 
                                if step2.text[0:2] == "v:":
                                    conn_pl.connection_comment = step2.text[2:]
                                if step2.text[0:2] == "Z:":
                                    conn_pl.connection_time = step2.text[2:]
                    if conn_pl.connection_type == "obpa":
                        obpa_preview = ", part of " + conn_pl.name
                    if conn_pl.connection_type == "adue":
                        adue_preview = ", part of " + conn_pl.name
                    
                    if conn_pl.connection_type == "vorg":
                        vorg_preview = ", earlier called " + conn_pl.name
                    if conn_pl.connection_type == "nach":
                        nach_preview = ", later called " + conn_pl.name
                    pl.connected_locations.append(conn_pl)
                case "678":
                    for step2 in step1:
                        match step2.get('code'):
                            case "b":
                                if pl.comments:
                                    pl.comments = step2.text + "; " + pl.comments
                                else:
                                    pl.comments = step2.text
        if pl.comments:                
            comments_preview = " (" + pl.comments + ")"
        if pl.name_variant:
            name_variant_preview = ", also called: "
            for variant in pl.name_variant:
                name_variant_preview = name_variant_preview + variant + "; "
            name_variant_preview = name_variant_preview[:-2]

        pl.preview = pl.name_preferred + obpa_preview + adue_preview + vorg_preview + nach_preview + name_variant_preview + comments_preview
#        print(pl)
#        print(entity_list)
        if(("gik" in entity_list or "giz" in entity_list or "gxz" in entity_list) and "gil" not in entity_list):
        #Thus, only administrative units or not-further determined locations or fictive locations, provided they are neither states nor larger administrative regions
            potential_places_list.append(pl)
#            print("potential places list at the end of gnd_parsing_place_part_of_list: ")
#            print(potential_places_list)
    return(potential_places_list)

def gnd_parsing_place(authority_url):
    potential_places_list = []
    potential_places_list_complete = []
    search_term = authority_url[89:-61]
    if "%" in search_term: # If there was a word search, I only search for the first word
        search_term = search_term.split("%")[0]
    url = urllib.request.urlopen(authority_url)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
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
            url = urllib.request.urlopen(authority_url)
            tree = xml.etree.ElementTree.parse(url)
            root = tree.getroot()
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
    return(potential_places_list_complete)




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


def dates_parsing(dates_from_source):
    """
    I don't think that this module is in use. 
    """
# This module chooses the most relevant datestring and turns it into a standardised date, consisting of a (standardised) datestring, a logical field determining if it is dates of life or dates of activity,
    # and datetime objects for start and end. 
    # Unfortunately, there is a large number of variants of dates used in the GND - hence, a large number of cases has to be defined (for the start only a few)
# for the moment, I ignore entries with "datu" and "rela" - the former seems to be in most cases an additional date, the 
    if len(dates_from_source) == 1:
        if dates_from_source[0].datetype == "datl" or dates_from_source[0].datetype == "datx": # normally, the latter does not appear alone, but maybe it does sometimes
            datetype = "lived"
            date_raw = dates_from_source[0].datestring
        elif dates_from_source[0].datetype == "datw" or dates_from_source[0].datetype == "datz": # normally, the latter does not appear alone, but maybe it does sometimes
            datetype = "active"
            date_raw = dates_from_source[0].datestring
    if len(dates_from_source) == 2:
        if dates_from_source[0].datetype == "datl" or dates_from_source[1].datetype == "datx":
            datetype = "lived"
            date_raw = dates_from_source[0].datestring
            # this is only provisional - there are - alas - cases in which the datx field contains one exact date, and the datl field both 
            # I should perhaps do it rather differently, saving and parsing all dates and combining them - oh dear!
        
    pass
    return




def artist_record_parsing(artist_record):
    print("arrived in artists_parsing")
    # Currently, this file is also used if an organisation is found at the search for artists. 
    # One needs a separate function for parsing organisations. 
    pe = Person_import()
    name_preferred_inversed = ""
    name_variant_preview = ""
    date_preview = ""
    ortg_preview = ""
    orts_preview = ""
    ortw_preview = ""
    print("artist_record as it arrives in artist_record_parsing")
    print("type of artist_record: ")
    print(type(artist_record))
    print(artist_record)
    
    artist_record = ast.literal_eval(artist_record)
    print("type of artist_record after transformation: ")
    print(type(artist_record))
    #url = requests.get(authority_url)
    #artist_record = artist_record.json()
    external_id = External_id()
    external_id.uri = artist_record["id"]
    external_id.name = "ULAN"
    external_id.id = external_id.uri[29:-5]
    pe.external_id.append(external_id)
    pe.name_preferred = artist_record["_label"]
    name_preferred_split = pe.name_preferred.split(",", maxsplit = 1) # One of the variant names is normally just the preferred name inversed, e.g. "John Smith" instead of "Smith, John"
    if len(name_preferred_split) == 2: # excluding names without a comma, e.g. of non-Western artists
        name_preferred_inversed = name_preferred_split[1].strip() + " " + name_preferred_split[0]
    connections_list = []
    if "identified_by" in artist_record:
        name_variant_list = []       
        for variant in artist_record["identified_by"]:
            if variant["type"] == "Name" and variant["content"] != name_preferred_inversed: # if the inversed versions of the names are ignored
                name_variant = variant["content"]
                name_variant_list.append(name_variant)
        if len(name_variant_list) > 1: 
            # The first name in the list is name_preferred. Hence, there are only variants if there are at least two names, and I have to remove the first
            name_variant_list = name_variant_list[1:]
            pe.name_variant = name_variant_list
        if pe.name_variant:
            name_variant_preview = ", also called: "
            for variant in pe.name_variant:
                name_variant_preview = name_variant_preview + variant + "; "
            name_variant_preview = name_variant_preview[:-2]

    if "classified_as" in artist_record:
        for property in artist_record["classified_as"]:
            if property["id"] == "http://vocab.getty.edu/aat/300189559":
                pe.sex = "male"
            if property["id"] == "http://vocab.getty.edu/aat/300189557":
                pe.sex = "female"
    if "referred_to_by" in artist_record:
        date_raw = ""
        for property in artist_record["referred_to_by"]:
            biography = property["content"]
            if "," in biography:
                biography_divided = biography.split(",")
                for biography_statement in biography_divided:
                    if any(character.isdigit() for character in biography_statement): # if there is a section with no digits (e.g. ", active in Spain"), it is deleted
                        date_raw = date_raw + biography_statement + ", "
                date_raw = date_raw[:-2].strip()
            date_from_source = Date_import()
            date_from_source.datestring_raw = date_raw
            pe.dates_from_source.append(date_from_source)
            date_processed = artist_date_parsing(date_raw)
            pe.datestring = date_processed[0]
            pe.date_start = (date_processed[1], 1, 1)
            pe.date_end = (date_processed[2], 12, 31)
            pe.date_aspect = date_processed[3]
            if pe.datestring:
                date_preview = " (" + pe.datestring + ")"
   
    if "la:related_from_by" in artist_record:
        connections_list = []
        if type((artist_record["la:related_from_by"])) is dict: # only one entry
            connections_list.append(artist_record["la:related_from_by"])           
        else:
            for connection in artist_record["la:related_from_by"]:
                connections_list.append(connection)
        for connection in connections_list:
            conn_ent = Connected_entity()
            conn_ent.external_id = []
            conn_id = External_id()
            id_raw = connection["la:relates_to"]["id"]
            conn_id.uri = id_raw
            if "ulan" in id_raw: #should normally happen, but maybe they have some strange connections
                conn_id.name = "ULAN"
                conn_id.id = id_raw[29:]
                conn_ent.external_id.append(conn_id)
            if type(connection["classified_as"][0]) is str:
                conn_ent.connection_type = connection["classified_as"][0]
            else: 
                conn_ent.connection_type = connection["classified_as"][0]["id"]
            
            match conn_ent.connection_type:
                case "http://vocab.getty.edu/ulan/relationships/1000":                
                    conn_ent.connection_comment = "related to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1003":                
                    conn_ent.connection_comment = "associated with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1005":                
                    conn_ent.connection_comment = "possibly identified with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1006":                
                    conn_ent.connection_comment = "formerly identified with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1007":                
                    conn_ent.connection_comment = "distinguished from"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1008":                
                    conn_ent.connection_comment = "meaning overlaps with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1101":                
                    conn_ent.connection_comment = "teacher of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1102":                
                    conn_ent.connection_comment = "student of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1105":                
                    conn_ent.connection_comment = "apprentice of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1106":                
                    conn_ent.connection_comment = "apprentice was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1107":                
                    conn_ent.connection_comment = "influenced"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1108":                
                    conn_ent.connection_comment = "influenced by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1111":                
                    conn_ent.connection_comment = "master of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1112":                
                    conn_ent.connection_comment = "master was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1113":                
                    conn_ent.connection_comment = "fellow student of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1201":                
                    conn_ent.connection_comment = "patron of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1202":                
                    conn_ent.connection_comment = "patron was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1203":                
                    conn_ent.connection_comment = "donor of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1204":                
                    conn_ent.connection_comment = "donor was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1205":                
                    conn_ent.connection_comment = "client of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1206":                
                    conn_ent.connection_comment = "client was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1211":                
                    conn_ent.connection_comment = "artist to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1212":                
                    conn_ent.connection_comment = "artist was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1213":                
                    conn_ent.connection_comment = "court artist to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1214":                
                    conn_ent.connection_comment = "court artist was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1217":                
                    conn_ent.connection_comment = "employee of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1218":                
                    conn_ent.connection_comment = "employee was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1221":                
                    conn_ent.connection_comment = "appointed by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1222":                
                    conn_ent.connection_comment = "appointee of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1223":                
                    conn_ent.connection_comment = "crowned by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1224":                
                    conn_ent.connection_comment = "crowned"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1301":                
                    conn_ent.connection_comment = "colleague of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1302":                
                    conn_ent.connection_comment = "associate of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1303":                
                    conn_ent.connection_comment = "collaborated with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1305":                
                    conn_ent.connection_comment = "worked with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1306":                
                    conn_ent.connection_comment = "performed with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1307":                
                    conn_ent.connection_comment = "assistant of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1308":                
                    conn_ent.connection_comment = "assisted by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1309":                
                    conn_ent.connection_comment = "advisor of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1311":                
                    conn_ent.connection_comment = "partner of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1315":                
                    conn_ent.connection_comment = "principal of"
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/1317":                
                    conn_ent.connection_comment = "member of"
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/1321":                
                    conn_ent.connection_comment = "school of"
                    conn_ent.connection_type = "organisation"
                

                # 1313/1314 partner (in firm) not included
                # 1318 member (of corporation) was > for orgs
                # 1322 school was für > for orgs
                # 1411/1412 successor of / predecessor of, only for organisations
                # 1413 administration overlaps brauche ich wohl nicht
                # 1414 join venture brauche ich wohl nicht
                # 1421/1422 founded by / founded (für organisationen auf beiden Seiten) wohl nicht
                # 1544 significant partner brauche ich wohl nicht


                case "http://vocab.getty.edu/ulan/relationships/1331":                
                    conn_ent.connection_comment = "worked with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1332":                
                    conn_ent.connection_comment = "worker was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1500":                
                    conn_ent.connection_comment = "related to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1501":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "sister of"
                    else:
                        conn_ent.connection_comment = "brother or sister of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1511":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "daughter of"
                    else:
                        conn_ent.connection_comment = "son or daughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1512":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "mother of"
                    else:
                        conn_ent.connection_comment = "father or mother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1513":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "grandson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "granddaughter of"
                    else:
                        conn_ent.connection_comment = "grandchild of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1514":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "grandfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "grandmother of"
                    else:
                        conn_ent.connection_comment = "grandparent of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1515":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "great-grandfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "great-grandmother of"
                    else:
                        conn_ent.connection_comment = "great-grandfather or great-grandmother off"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1516":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "great-grandson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "great-granddaughter of"
                    else:
                        conn_ent.connection_comment = "great-grandchild of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1521":                
                    conn_ent.connection_comment = "cousin of"
                case "http://vocab.getty.edu/ulan/relationships/1531":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "nephew of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "niece of"
                    else:
                        conn_ent.connection_comment = "nephew or niece of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1532":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "uncle of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "aunt of"
                    else:
                        conn_ent.connection_comment = "uncle or aunt of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1541":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "husband of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "wife of"
                    else:
                        conn_ent.connection_comment = "husband or wife of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1542":                
                    conn_ent.connection_comment = "consort of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1543":                
                    conn_ent.connection_comment = "consort was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1547":                
                    conn_ent.connection_comment = "romantic partner of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1548":                
                    conn_ent.connection_comment = "domestic partner of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1550":                
                    conn_ent.connection_comment = "relative by marriage of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1551":
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "brother-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "sister-in-law of"
                    else:
                        conn_ent.connection_comment = "brother or sister-in-law of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1552":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "father-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "mother-in-law of"
                    else:
                        conn_ent.connection_comment = "father or mother-in-law of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1553":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "son-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "daughter-in-law of"
                    else:
                        conn_ent.connection_comment = "son or daughter-in-law of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1554":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "adoptive father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "adoptive mother of"
                    else:
                        conn_ent.connection_comment = "adoptive father or mother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1555":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "adopted son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "adopted daughter of"
                    else:
                        conn_ent.connection_comment = "adopted son or daughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1556":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "half-brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "half-sister of"
                    else:
                        conn_ent.connection_comment = "half-brother or half-sister of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1557":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "step-brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-sister of"
                    else:
                        conn_ent.connection_comment = "step-brother or step-sister of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1561":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "step-son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-daughter of"
                    else:
                        conn_ent.connection_comment = "step-son or step-daughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1562":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "step-father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-mother of"
                    else:
                        conn_ent.connection_comment = "step-father or step-mother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1571":                
                    conn_ent.connection_comment = "guardian of"   
                case "http://vocab.getty.edu/ulan/relationships/1573":                
                    conn_ent.connection_comment = "ward of"   
                case "http://vocab.getty.edu/ulan/relationships/1574":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "godfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "godmother of"
                    else:
                        conn_ent.connection_comment = "godparent of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1575":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "godson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "goddaughter of"
                    else:
                        conn_ent.connection_comment = "godchild of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1581":                
                    conn_ent.connection_comment = "descendant of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1590":                
                    conn_ent.connection_comment = "possibly related to"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2550":                
                    conn_ent.connection_comment = "friend of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2576":                
                    conn_ent.connection_comment = "patron of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2577":                
                    conn_ent.connection_comment = "patron was"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1573":                
                    conn_ent.connection_comment = "ward of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2572":                
                    conn_ent.connection_comment = "founder of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2574":                
                    conn_ent.connection_comment = "director of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2581":                
                    conn_ent.connection_comment = "administrator of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2674":                
                    conn_ent.connection_comment = "professor at"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2696":                
                    conn_ent.connection_comment = "leader of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2778":                
                    conn_ent.connection_comment = "owner of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2828":                
                    conn_ent.connection_comment = "student at"   
                    conn_ent.connection_type = "organisation"




                # 2573 founded by > for organisations
                # 2575 directed by [i.e., having as director] > for organisation
                # 2578 / 2579 trustee of / trustee was > for organisation, but probably not needed
                # 22582 administrated by > for orgs
                # 2583/2584 chairman / chaired by > probably not needed
                # 2650/2651: publisher was / publisher of (person > org > is this needed?)
                # 2675: professor was > for orgs
                # 2677: teacher was > for orgs
                # 2693: president was > for orgs
                # 2697: leader was > for orgs
                # 2779: owned by > for orgs
                # 2781/2782: dedicatee of , e.g. Rodin > Musée Rodin > das braucht man doch nicht??
                # 2794/2795: representative of / representative was > not needed?
                # 2829: student was > for orgs
                # 2840/2841: Performer with / performer was > not needed



            if conn_ent.connection_type == "person": 
                pe.connected_persons.append(conn_ent)
            if conn_ent.connection_type == "organisation": 
                pe.connected_organisations.append(conn_ent)
                # I could not test the connected organisations since they apparently used very rarely
          
        """Annoyingly, the timespan of the connection does not appear in the json file but only in the rdf and nt files. So, one has to add it later for the selected person only """
    if "born" in artist_record:
        if "took_place_at" in artist_record["born"]:
            if artist_record["born"]["took_place_at"][0]:
                for place_raw in artist_record["born"]["took_place_at"]:
                    conn_place = Connected_entity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "ortg"
                    place_id_list = []
                    place_id = External_id()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
                    ortg_preview = ", born in " + conn_place.name
    if "died" in artist_record:
        if "took_place_at" in artist_record["died"]:
            if artist_record["died"]["took_place_at"][0]:
                for place_raw in artist_record["died"]["took_place_at"]: # in case several alternative places are given
                    conn_place = Connected_entity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "orts"
                    place_id_list = []
                    place_id = External_id()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
                    orts_preview = ", died in " + conn_place.name
    if "carried_out" in artist_record:
        #print("carried_out found")
        for activity in artist_record["carried_out"]:
        #    print(activity)
        #    print(activity["classified_as"][0]["id"])
            if activity["classified_as"][0]["id"] == "http://vocab.getty.edu/aat/300393177" and "took_place_at" in activity:
                place_list = activity["took_place_at"]
                for place_raw in place_list: # I have the feeling, that there is an 'activity' record for every place, but perhaps there may be also sometimes two places linked to one 'activity' record
        #            print("place of activity found")
        #            print(place_raw)
                    conn_place = Connected_entity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "ortw"
                    place_id_list = []
                    place_id = External_id()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
                    ortw_preview = ", active in " + conn_place.name
    # attention: ULAN defines any number of places of activity. I will need one and only one place defined as preferred place. 
    # thus: I need to introduce a function that makes the editor choose one place if there are several, and enter one if there are none.          

    pe.preview = pe.name_preferred + " " + date_preview + " " + ortg_preview + ortw_preview + orts_preview + name_variant_preview
    print(pe)
    return(pe)




async def making_process_identification(making_processes):
    """This module has bene primarily made for parsing information about the making process of a manuscript or printed book
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
            place_new = place_identification(place)
            print(place_new)
            making_process.place = place_new
        artist = making_process.person
        if artist.name != "":
            print("Artist found")
            print(artist.name)
            artist.role = "art"
            artist_new = await person_identification(artist)
            print(artist_new)
            making_process.person = artist_new
        date = making_process.date
        if date.datestring_raw != "":
            print("Date_found")
            print(date.datestring_raw)
            try:
                date_new = entered_date(date.datestring_raw)
                making_process.date = date_new
            except InvalidDateStringException as d:
                print(f"String could not be divided into individual dates: {d}")
            except InvalidDateException as e:
                print(f"Failed to parse date string {e}")
            except InvalidMonthException as f:
                print(f"Failed to parse date string {f}")
            except InvalidDayException as g:
                print(f"Failed to parse date string {g}")
            except InvalidDateRangeException as h:
                print(f"{h}")

    
    return(making_processes)


async def get(session, url): 
    # This is a short programme I received from Gregor Dick. Together with a gather funciton i
    async with session.get(url) as response:
        # Wait for the start of the response.
        await response.read()
        # Wait for the complete response and return its body.
        return await response.text()
        

async def ulan_search(person):
    person_name_search = person.name
    for old, new in url_replacement.items():
        person_name_search = person_name_search.replace(old, new)
    authority_url = r'https://vocab.getty.edu/sparql.json?query=select%20distinct%20%3Fartist_id%20%7B%0A%20%7B%3FSubject%20luc%3Aterm%20%22' + \
        person.name + r'%22%3B%20skos%3AinScheme%20ulan%3A%20%3B%20a%20%3Ftyp%3B%20gvp%3AprefLabelGVP%20%5Bxl%3AliteralForm%20%3FTerm%5D%7D' +\
        r'%20union%20%7B%3FSubject%20luc%3Aterm%20%22' + person.name + r'%22%3B%20skos%3AinScheme%20ulan%3A%20%3B%20a%20%3Ftyp%3B%20xl%3AaltLabel' +\
        r'%20%5Bxl%3AliteralForm%20%3FTerm%5D%7D%0A%20%20%3Ftyp%20rdfs%3AsubClassOf%20gvp%3ASubject%3B%20rdfs%3Alabel%20%3FType.%0A%20filter' + \
        r'%20(%3Ftyp%20!%3D%20gvp%3ASubject)%20%0A%20optional%20%7B%3FSubject%20gvp%3AparentString%20%3FType2%7D%0A%20filter%20(%3FType2%20!%3D%20' +\
        r'%22Unidentified%20Named%20People%20and%20Firms%22)%20%0A%20optional%20%7B%3FSubject%20dc%3Aidentifier%20%3Fartist_id%7D%7D%0AORDER%20BY%20' + \
        r'(fn%3Alower-case(str(%3FTerm)))%0A&toc=Finding_Subjects&implicit=true&equivalent=false&_form=/queriesF'
    ulan_list_raw = requests.get(authority_url)
    ulan_list = ulan_list_raw.json()
    ulan_url_list = []
    if "results" in ulan_list:
        list_results = ulan_list["results"]
        if "bindings" in list_results:
            bindings = list_results["bindings"]
            for artist in bindings:
                artist_id = artist["artist_id"]["value"]
                artist_authority_url = r'https://vocab.getty.edu/ulan/' + artist_id + r'.json'
                ulan_url_list.append(artist_authority_url)
            print(ulan_url_list)
            async with aiohttp.ClientSession() as session:
                results = await asyncio.gather(*(get(session, url) for url in ulan_url_list))
#                print("results")
#                print(results)
#                print(len(results))
            for result in results:
                candidate = artist_record_parsing(result)
#                print("candidate identified: ")
#                print(candidate)
                #authority_url_list.append(artist_authority_url)
                person.potential_candidates.append(candidate)
                #print("candidate appended, now" + str(len(person.potential_candidates)) + "candidates")
                      
    return person

