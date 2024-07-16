# This module contains functions that transform the information taken from several bibliographic resources (in books_parsing manifest, books_parsing_bibliographies and gndparse), 
# according to the selections made by the user in NewRessource.vue, into a format ready for importing it into Iconobase. 
# There is normally, depending on the material, either one Manuscript or one Book record. 
# If there are any persons, organisations (including repositories) and places connected to the book or manuscript that do not yet have an authority record in the database,
# authority records for them are created first, and then the book or manuscript record is linked to them. 
# In a future setting, these authority records should not be created automatically, but first displayed to the user to see if anything should be added or corrected. 
# Furthermore, now the 'secondary' references (e.g., if we have the Place of Birth of a printer) are merely copied into the record. 
# Later, there should be a search if there are already records for 

from classes import *
from nanoid import generate
import requests
import dbactions
from pymongo import MongoClient
from dates_parsing import date_overall_parsing
import re
import person_relations
import asyncio
import aiohttp


dbname = dbactions.get_database()
coll=dbname['bpf']




role_person_type_correspondence = {"aut" : "Author", "edt" : "Author", "rsp" : "Author", "prt" : "Printer", "pbl" : "Printer"}
person_person_connection_type_correspondence = {"Vater" : "father", "Mutter" : "mother", "Bruder" : "brother", "Schwester" : "sister", "Sohn" : "son", "Tochter" : "daughter", \
                                         "Onkel" : "uncle", "Tante" : "aunt", "Neffe" : "nephew", "Nichte" : "niece", "Enkel" : "grandson", "Enkelin" : "granddaughter", 
                                         "Großvater" : "grandfather", "Großmutter" : "grandmother", "Ehemann" : "husband", "1. Ehemann" : "first husband", "2. Ehemann" : "second husband", \
                                         "3. Ehemann" : "third husband", "4. Ehemann" : "fourth husband", "5. Ehemann" : "fifth husband", "6. Ehemann" : "sixth husband", \
                                         "Ehefrau" : "wife", "1. Ehefrau" : "first wife", "2. Ehefrau" : "second wife", "3. Ehefrau" : "third wife", "4. Ehefrau" : "fourth wife", \
                                         "5. Ehefrau" : "fifth wife", "6. Ehefrau" : "sixth wife", "Adoptivvater" : "adoptive father", "Adoptivmutter" : "adoptive mother", \
                                         "Adoptivsohn" : "adopted son", "Adoptivtochter" : "adopted daughter", "Schwiegervater" : "father-in-law", "Schwiegermutter" : "mother-in-law", \
                                            "Schwiegersohn" : "son-in-law", "Schwiegertochter" : "daughter-in-law", "Schwager" : "brother-in-law", "Schwägerin" : "sister-in-law", \
                                                "Schüler" : "pupil", "Lehrer" : "teacher"}
role_org_type_correspondence = {"aut" : "Author", "edt" : "Author", "prt" : "Printer", "pbl" : "Printer", "col" : "Collection"}
connection_comment_pattern = r'([^,\(]*)([,\()])(.*)'


async def get(session, url): 
    # This is a short programme I received from Gregor Dick. Together with a gather funciton i
#    async with session.head(url, allow_redirects=False) as response:
    async with session.head(url) as response:
        # Wait for the start of the response.
        await response.read()
        return response.headers["Location"]


async def get_viaf_from_authority(url_list):
    # This function the URL of an authority file (currently GND and ULAN) and returns an External_id object
    # It will be used numerous times for 'stitching' records together
#    print("URL as it arrives in get_viaf_from_authorty")
#    print(url)
    url_search_list = []
    url_list = list(dict.fromkeys(url_list)) # this shoudl remove duplicates
    for url in url_list:
        if r"/gnd/" in url:
            identifier = "DNB%7C" + url[22:]
#            print("URI comes from GND")
#            print(identifier)
        elif r"vocab.getty.edu/page/ulan/" in url:
            identifier = "JPG%7C" + url[33:]
        url_search = r'https://viaf.org/viaf/sourceID/' + identifier
        url_search_list.append(url_search)   
#    print(url_list)
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(get(session, url) for url in url_search_list))
    viaf_urls_dict = dict(zip(url_list, results))          
    return viaf_urls_dict

def add_relationship_in_far_record(person_found, person_new, connected_person_connection_type):
# This module is used for the 'stitching' together of person records; it checks, if an already extant record ('far record') already has a connection with the new record. 
# If so, it adds the ID of the new record to the connection; if no, it creates a new connection from scratch
# It appears that it works also for organisations and places connected to persons. 
    if person_found: # this is for making the reciprocal connection
        far_record = person_found["connected_persons"]
        if "sex" not in person_found: # this is to avoid error messages, since person_found can be also an organisation or a place
            person_found["sex"] = ""
        connection_found = False
        for far_person in far_record:
            expected_connection_type = person_relations.relation_correspondence(connected_person_connection_type, person_found["sex"])
            # Sometimes, one and the same person appears twice, in different relations. If one relation had just been inserted, it should have the reciprocal connection type - hopefully
            for far_external_id in far_person["external_id"]:
                for external_id_number in range(len(person_new.external_id)):
                    if far_external_id["uri"] == person_new.external_id[external_id_number].uri and far_person["connection_type"] == expected_connection_type:
                        # This is step 2a: there is already a connection, to which the ID of the new record is added
    #                                print("found record for inserting reciprocal ID")
                        far_person["id"] = person_new.id
                        dbactions.add_connection_id(person_found["id"], far_person["name"], far_person["id"])
                        connection_found = True
                        break
#                        print("The connected record has a reciprocal connection to which merely the new ID has to be added")
        if connection_found == False:
            # This is step 2b: there is no reciprocal connection, it needs to be established
#                        print("For person " + person_found["name_preferred"] + " no connection has been found")
            new_connection = Connected_entity()
            new_connection.id = person_new.id
            new_connection.external_id = person_new.external_id
            new_connection.name = person_new.name_preferred # better use preview including year
            new_connection.connection_type = expected_connection_type
#            new_connection.connection_type = person_relations.relation_correspondence(connected_person_connection_type, person_found["sex"]) 
            # I need a separate formular, without 'sex', for orgs and places
#                        new_connection.connection_type = "1counterpart to " + connected_person.connection_type # This has to be replaced by a proper term
            dbactions.add_connection(person_found["id"], "connected_persons", new_connection)
                    
def person_relationship_parse(connected_entity_type, connection_comment, connection_type, person_new_sex):
# This module is a transmission for the terms that describe a relationship - it does some preliminary parsing and then calls a function in person_relations, that contains lists of the relevant translations
    connection_type_raw = ""
    if connection_comment:
        if ("," in connection_comment or "(" in connection_comment) and connected_entity_type != "place": # this seems to make little sense for connected places
            connection_comment_divided = re.match(connection_comment_pattern, connection_comment).groups()
            connection_type_raw = connection_comment_divided[0]
            if connection_comment_divided[1] == ",":
                connection_comment = connection_comment_divided[2]
            else: # i.e., an opening bracket
                connection_comment = connection_comment_divided[2][:-1]
        else:
            connection_type_raw = connection_comment
    if connected_entity_type == "person":
        connection_type, connection_comment = person_relations.gnd_person_person_relation(connection_type_raw, person_new_sex, connection_type)
    elif connected_entity_type == "organisation":
        connection_type, connection_comment = person_relations.gnd_person_org_relation(connection_type_raw, person_new_sex, connection_type)
    elif connected_entity_type == "location": 
        connection_type, connection_comment = person_relations.gnd_person_place_relation(connection_type_raw, person_new_sex, connection_type)
                  
    return(connection_comment, connection_type)



class Person_against_duplication(BaseModel): # I have these classes here and not in 'classes' because they are only needed in these functions.
    preview : Optional[str] = ""
    id : Optional[str] = ""
    person_type1 : Optional[list[str]]  = []

class Org_against_duplication(BaseModel):
    preview : Optional[str] = ""
    id : Optional[str] = ""
    org_type1 : Optional[list[str]]  = []

class Place_against_duplication(BaseModel):
    preview : Optional[str] = ""
    id : Optional[str] = ""
    place_type1 : Optional[list[str]]  = []


async def metadata_dissection(metadata):

    if metadata.bibliographic_information:
        # Section on Person
        # There are three constellations
        # (a): A person that is already in Iconobase was identified via an ID. In this case, there is no list of potential candidates. 
        # (b): Several persons already in Iconobase were identified through a name search. in this list, there is a list of potential candidates, one of whom has been selected
        #       (In cases a and b, no person has to be added, but possibly some person_type1 has to be added)
        # (c): Persons not in iconobase have been found - whether it be one found via an ID or several found via a name search, they will be in a list of potential candidates
        #          (In this case, a new record for the selected person has to be added, and it will come with the person_type1 required by the role of the person)

    
    
        persons_list = [] # This list exists to make sure that if the same person is mentioned twice in different functions, e.g. as author and publisher, there is only one record created 
        person_against_duplication = Person_against_duplication()
        
        if metadata.bibliographic_information[0].persons:
            for person in metadata.bibliographic_information[0].persons:
                no_new_person_chosen_from_list = False
                if person.chosen_candidate != 999: # I make this awkward construction to avoid 'out of range' exceptions
    #                print("there is a chosen candidate")
                    if person.potential_candidates[person.chosen_candidate].internal_id:                        
                        no_new_person_chosen_from_list = True
    #            else:
    #                    print("There is no chosen candidate")

                if person.internal_id: #Scenario (a) above - in this case, no record has to be added
                    if person.internal_id_person_type1_comment: 
                        #If the person is alredy in Iconobase but has an additional person_type1 in the new entry, it has to be added to the person record. 
                        dbactions.add_person_type(person.internal_id, person.internal_id_person_type1_needed)
                elif no_new_person_chosen_from_list: # Scenario (b) above
                    person.internal_id = person.potential_candidates[person.chosen_candidate].internal_id
                    if person.potential_candidates[person.chosen_candidate].internal_id_person_type1_comment:
    #                    print("Type1 to be added:")
    #                    print(person.potential_candidates[person.chosen_candidate].internal_id) 
    #                    print(person.internal_id_person_type1_needed)
                        dbactions.add_person_type(person.potential_candidates[person.chosen_candidate].internal_id, person.internal_id_person_type1_needed)

                else: 
    #                print("new person")
                    for person_against_duplication in persons_list:
    #                    print("in loop for new person")
                        if person_against_duplication.preview == person.potential_candidates[person.chosen_candidate].preview: 
                            # this means, if a person not yet in the database appears twice in the record, in different roles
                            person.internal_id = person_against_duplication.id
                            person_type = role_person_type_correspondence[person.role]
                            if  person_type not in person_against_duplication.person_type1: 
                                # Since the type is created automatically from the role, there can be only one type in person
                                dbactions.add_person_type(person.internal_id, person_type)


    #                        print("New Person is a duplicate")
                            break
                    else: 
    #                        print("New person is not a duplicate")
                            person.internal_id = await person_ingest(person)
                            person_against_duplication.preview = person.potential_candidates[person.chosen_candidate].preview
                            person_against_duplication.id = person.internal_id
                            person_against_duplication.person_type1 = role_person_type_correspondence[person.role]
                            persons_list.append(person_against_duplication)
    #                       print("record against duplication: ")
    #                       print(person_against_duplication)




    # Section on Organisations
        # There are three constellations
        # (a): An organisation that is already in Iconobase was identified via an ID. In this case, there is no list of potential candidates. 
        # (b): Several organisations already in Iconobase were identified through a name search. in this list, there is a list of potential candidates, one of whom has been selected
        #       (In cases a and b, no organisation has to be added, but possibly some org_type1 has to be added)
        # (c): Organisations not in iconobase have been found - whether it be one found via an ID or several found via a name search, they will be in a list of potential candidates
        #          (In this case, a new record for the selected organisation has to be added, and it will come with the org_type1 required by the role of the person)

        
        
        orgs_list = [] # This list exists to make sure that if the same organisation is mentioned twice in different functions, e.g. as author and publisher, there is only one record created 
        org_against_duplication = Org_against_duplication()
        
        if metadata.bibliographic_information[0].organisations:
            for org in metadata.bibliographic_information[0].organisations:
                no_new_org_chosen_from_list = False
                if org.chosen_candidate and org.chosen_candidate != 999: # I make this awkward construction to avoid 'out of range' exceptions
                    if org.potential_candidates[org.chosen_candidate].internal_id:
                        no_new_org_chosen_from_list = True
                     

                if org.internal_id: #Scenario (a) above - in this case, no record has to be added
                    if org.internal_id_org_type1_comment: 
    #                    print("Type needed:")
    #                    print(org.internal_id_org_type1_needed)
                        #If the organisation is alredy in Iconobase but has an additional org_type1 in the new entry, it has to be added to the organisation record. 
                        dbactions.add_organisation_type(org.internal_id, org.internal_id_org_type1_needed)
                elif no_new_org_chosen_from_list: # Scenario (b) above
                    org.internal_id = org.potential_candidates[org.chosen_candidate].internal_id
                    if org.potential_candidates[org.chosen_candidate].internal_id_org_type1_comment:
    #                    print("Type1 to be added:")
    #                    print(org.potential_candidates[org.chosen_candidate].internal_id) 
    #                    print(org.internal_id_org_type1_needed)
                        dbactions.add_organisation_type(org.potential_candidates[org.chosen_candidate].internal_id, org.internal_id_org_type1_needed)

                else: 
    #                print("new organisation")
                    for org_against_duplication in orgs_list:
    #                    print("in loop for new organisaton")
                        if org_against_duplication.preview == org.potential_candidates[org.chosen_candidate].preview: 
                            # this means, if an organisation not yet in the database appears twice in the record, in different roles
                            org.internal_id = org_against_duplication.id
                            org_type = role_org_type_correspondence[org.role]
                            if  org_type not in org_against_duplication.org_type1: 
                                # Since the type is created automatically from the role, there can be only one type in organisation
                                dbactions.add_organisation_type(org.internal_id, org_type)


    #                        print("New Organisation is a duplicate")
                            break
                    else: 
    #                        print("New Organisation is not a duplicate")
                            org.internal_id = org_ingest(org)
                            org_against_duplication.preview = org.potential_candidates[org.chosen_candidate].preview
                            org_against_duplication.id = org.internal_id
                            org_against_duplication.org_type1 = role_org_type_correspondence[org.role]
                            orgs_list.append(org_against_duplication)
    #                        print("record against duplication: ")
                            print(org_against_duplication)

    # Section on Places
        # There are three constellations
        # (a): A place that is already in Iconobase was identified via an ID. In this case, there is no list of potential candidates. 
        # (b): Several places already in Iconobase were identified through a name search. in this list, there is a list of potential candidates, one of whom has been selected
                # (In cases a and b, no place will have to be added)    
        # (c): Places not in iconobase have been found - whether it be one found via an ID or several found via a name search, they will be in a list of potential candidates
        #          (In this case, a new record for the selected place has to be added)
        # The field place_type1 works different from the corresponding fiels for persons and organisations. It can only have one value, not an array, and it has to be 'Town - historical'
        # in all cases in this module. If only records of the type 'Town - modern' are found, they have to be compied into the 'Town - historical'
        # records (NB: 'Region - historical' would appear extremely rarely, only with a handful of incunables, so I leave it out here)
        
        
        places_list = [] # This list exists to make sure that if the same organisation is mentioned twice in different functions, e.g. as author and publisher, there is only one record created 
        place_against_duplication = Place_against_duplication()
        
        if metadata.bibliographic_information[0].places:
            for place in metadata.bibliographic_information[0].places:
                print("Number of candidates for this place: ")
                print(len(place.potential_candidates))
                print("Number of chosen candidate: ")
                print(place.chosen_candidate)
                no_new_place_chosen_from_list = False
                if place.chosen_candidate != 999: # I make this awkward construction to avoid 'out of range' exceptions
                    if place.potential_candidates[place.chosen_candidate].internal_id:                        
                        no_new_place_chosen_from_list = True

                if place.internal_id: #Scenario (a) above - in this case, no record has to be added
                    if place.internal_id_place_type1_comment: 
                        print("Type needed:")
                        print(place.internal_id_place_type1_needed)
                        #If the place is alredy in Iconobase but has an additional place_type1 in the new entry, a copy with the right place_type1 has to be made
                        place.internal_id = dbactions.copy_place_record(place.internal_id, place.internal_id_place_type1_needed) # It needs to be connected with the id of the new record
                elif no_new_place_chosen_from_list: # Scenario (b) above
                    place.internal_id = place.potential_candidates[place.chosen_candidate].internal_id
                    if place.potential_candidates[place.chosen_candidate].internal_id_place_type1_comment:
                        print("Type1 to be added:")
                        print(place.potential_candidates[place.chosen_candidate].internal_id) 
                        print(place.internal_id_place_type1_needed)
                        place.internal_id = dbactions.copy_place_record(place.potential_candidates[place.chosen_candidate].internal_id, place.internal_id_place_type1_needed) 
                        # It needs to be connected with the id of the new record
                else: 
                    print("new place")
                    for place_against_duplication in places_list: # I have to think it through, but the next lines are perhaps not necessary here. 
                        print("in loop for new place")
                        if place_against_duplication.preview == place.potential_candidates[place.chosen_candidate].preview: 
                            # this means, if an organisation not yet in the database appears twice in the record, in different roles
                            place.internal_id = place_against_duplication.id
                            place_type = "Town - historical"
                            if  place_type not in place_against_duplication.place_type1: 
                                # Since the type is created automatically from the role, there can be only one type in organisation
                                place.internal_id = dbactions.copy_place_record(place.internal_id, place_type)
                                # It needs to be connected with the id of the new record

                            print("New Place is a duplicate")
                            break
                
                    else: 
                            print("New Place is not a duplicate")
                            place.internal_id = place_ingest(place)
                            place_against_duplication.preview = place.potential_candidates[place.chosen_candidate].preview
                            place_against_duplication.id = place.internal_id
                            place_against_duplication.place_type1 = ["Town - historical"]
                            places_list.append(place_against_duplication)
                            print("record against duplication: ")
                            print(place_against_duplication)


    # Section on Repositories
        # Repositories are also organisations, however, there is only one repository per book. Furthermore, it is not part of the bibliographical
        # information as all other links to authority records are. 
        # There is no safeguard against creating two authority records if the same organisation appears as repertory and in the bibliographical information,
        # however, this constellation is neigh impossible. 
    if metadata.repository:
        no_new_org_chosen_from_list = False
        org = metadata.repository[0] # I had to define this as a list, but it always has one element only
        if org.chosen_candidate != 999: # I make this awkward construction to avoid 'out of range' exceptions
            if org.potential_candidates[org.chosen_candidate].internal_id:
                print("Chosen candidate for repository has internal id")
                no_new_org_chosen_from_list = True

        if org.internal_id: #Scenario (a) above - in this case, no record has to be added
            if org.internal_id_org_type1_comment: 
                print("Type for repository needed:")
                print(org.internal_id_org_type1_needed)
                #If the organisation is alredy in Iconobase but has an additional org_type1 in the new entry, it has to be added to the organisation record. 
                dbactions.add_organisation_type(org.internal_id, org.internal_id_org_type1_needed)
        elif no_new_org_chosen_from_list: # Scenario (b) above
            org.internal_id = org.potential_candidates[org.chosen_candidate].internal_id
            if org.potential_candidates[org.chosen_candidate].internal_id_org_type1_comment:
                print("Repository chosen from list - Type1 to be added:")
                print(org.potential_candidates[org.chosen_candidate].internal_id) 
                print(org.internal_id_org_type1_needed)
                dbactions.add_organisation_type(org.potential_candidates[org.chosen_candidate].internal_id, org.internal_id_org_type1_needed)
        else: 
            print("new repository")
            org.potential_candidates[org.chosen_candidate].internal_id = org_ingest(org)




# Section on Manuscripts
    if metadata.material == "m": # If the item has been identified as a manuscript
        new_manuscript = Manuscript_db()
        new_manuscript.id = generate()
        new_repository = Link_to_repository()
        new_repository.place_id = metadata.repository[0].potential_candidates[metadata.repository[0].chosen_candidate].internal_id
        new_repository.id_preferred = metadata.shelfmark
        new_manuscript.repository.append(new_repository)
        new_manuscript.preview = metadata.repository[0].name + ", " + metadata.shelfmark
        book_record_id = new_manuscript.id # I need that one later
        dbactions.insertRecordManuscript(new_manuscript)

# Section on printed books
    if metadata.material == "b": # If the item has been identified as printed book
        print("adding new book")
        new_book = Book_db()
        new_book.id = generate()
        new_book.title = metadata.bibliographic_information[0].title
        new_book.volume_number = metadata.bibliographic_information[0].volume_number
        new_book.part_title = metadata.bibliographic_information[0].part_title
        new_book.printing_date = metadata.bibliographic_information[0].printing_date
        new_book.date_string = metadata.bibliographic_information[0].date_string
        new_book.date_start = metadata.bibliographic_information[0].date_start
        new_book.date_end = metadata.bibliographic_information[0].date_end
        if metadata.bibliographic_information[0].bibliographic_id:
            for bibliographic_id in metadata.bibliographic_information[0].bibliographic_id:
                new_bibliographic_id = External_id()
                new_bibliographic_id = bibliographic_id
                new_book.bibliographic_id.append(new_bibliographic_id)
        if metadata.bibliographic_information[0].persons:
            for person in metadata.bibliographic_information[0].persons:
                new_person = Book_connected_entity_db()
                new_person.role = person.role
                if person.internal_id:
                    new_person.id = person.internal_id
                else:
                    new_person.name = person.name # This is a stopgap measure if a person could not be identified
                new_book.persons.append(new_person)
        if metadata.bibliographic_information[0].organisations:
            for org in metadata.bibliographic_information[0].organisations:
                new_org = Book_connected_entity_db()
                new_org.role = org.role
                if org.internal_id:
                    new_org.id = org.internal_id
                else: 
                    new_org.name = org.name # This is a stopgap measure if an organisation could not be identified
                new_book.organisations.append(new_org)
        if metadata.bibliographic_information[0].places:
            for place in metadata.bibliographic_information[0].places:
                new_place = Book_connected_entity_db()
                new_place.role = place.role
                if place.internal_id:
                    new_place.id = place.internal_id
                else: 
                    new_place.name = place.name # This is a stopgap measure if a place could not be identified
                new_book.places.append(new_place)
        new_book.preview = metadata.bibliographic_information[0].title + " (" + metadata.bibliographic_information[0].date_string + ")"
        book_record_id = new_book.id # I'll need that later
        print(new_book.date_start)
        print("Completed book record")
#        print("New book record: ")
#        print(new_book)
        dbactions.insertRecordBook(new_book)

                
                
# Section on individual pages. 
# This class contains the list of individual pages from the IIIF manifest as well as information on repository and shelf marks. 
# This information will eventually be copied to the individual Artwork and Photo records, once the cropping of images is complete and those records are created.
# It is not clear if this record will be needed in the long term 
    new_pages = Pages_db()
    new_pages.id = generate()
    new_pages.book_record_id = book_record_id
    if metadata.repository[0].internal_id:
        new_pages.repository = metadata.repository[0].internal_id
    else:
        new_pages.repository = metadata.repository[0].potential_candidates[org.chosen_candidate].internal_id
    new_pages.shelfmark = metadata.shelfmark
    new_pages.license = metadata.license
    new_pages.numberOfImages = metadata.numberOfImages
    new_pages.images = metadata.images
    if metadata.material == "m":
        new_pages.preview = metadata.repository[0].name + ", " + metadata.shelfmark
    if metadata.material == "b": 
        new_pages.preview = metadata.bibliographic_information[0].title + " (" + metadata.bibliographic_information[0].printing_date + ")"
    dbactions.insertRecordPages(new_pages)


    return metadata



async def person_ingest(person):
    # This function is about translating the imported information of a person into the information record used for the database. 
    # It directly sends the new records to the function for writing it and only returns its ID to metadata_dissection

    """
    One of its roles is to 'stitch' the new entry into the system by creating connections to internal IDs. It does so in different steps.
        Step 1: Checking the list of connected_entities in the new record, and if one of these entities is already in Iconobase, inserting its ID in the connected_entities record (I check first, if I can do 
        any stitching already with GND IDs so that I don't have to import VIAF IDs for such records. Hence, I first run this step close to the start, and then a second time after I got all the VIAF IDs. )
        Step 2: Checking if the identified connected record gives the new connected record as connected_entity. 
            Step 2a: if yes: adding the internal ID of the new record as connected_entity (+ checking if the connection_types are compatible)
            Step 2b: if no: adding the connection, with a connection type that is the complement to the one used in the original connection
        Steps 1 and 2 happen twice: once, if a connection can already made through the default GND records, once, when it is necessary to download the VIAF records. 
        Step 3: Check if any record already in Iconobase has a connection with the new record, without the new record having a connection with it. 
            If yes, addition of a connection to the extant record with a complementary connection in the new record. 
    """


    list_of_ids_to_check = []
    new_record_viaf_id = ""
    new_record_gnd_id = "" # This can be deleted once VIAF also works for organisations and places
    person_found = {}
    connection_already_made = False
    person_selected = person.potential_candidates[person.chosen_candidate]   
    person_new = Person_db()
    person_new.id = generate()
    person_new.type = "Person"
    person_new.person_type1.append(role_person_type_correspondence[person.role])
    person_new.external_id = person_selected.external_id
    connected_location_comment_is_date = r'(ab|bis|ca.|seit)?(\d \-)' # if the comment for a connection between person and location follows this pattern, it is moved to connection time
    new_record_gnd_id = person_selected.external_id[0].id # I need this only as long as I cannot get VIAF to work for organisations. 
    list_of_ids_to_check.append(person_new.external_id[0].uri) # The VIAF IDs added from this list will later be added to the record
    person_new.name_preferred = person_selected.name_preferred
    person_new.name_variant = person_selected.name_variant
    if person.name not in person_new.name_variant: # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for variants and not a word search. 
        person_new.name_variant.append(person.name)
    person_new.sex = person_selected.sex
    """ Currently, I still use the list of dates_from_source and simply add the newly parsed datestring and start and end dates to it. 
        In a later stage, the entire list will be sent to the parsing function, and only one date will come back for inclusion into the database """
    for date_from_source in person_selected.dates_from_source:
        date_parsed = date_overall_parsing(date_from_source.datestring_raw, date_from_source.date_comments, date_from_source.datetype)
        datestring = date_parsed[0]
        date_start = date_parsed[1]
        date_end = date_parsed[2]
        date_aspect = date_parsed[3]
        date = Date_import()
        date.datestring_raw = date_from_source.datestring_raw
        date.date_comments = date_from_source.date_comments
        date.datetype = date_from_source.datetype
        date.datestring = datestring
        date.date_start = date_start
        date.date_end = date_end
        date.date_aspect = date_aspect
        person_new.dates_from_source.append(date)

    if person_selected.connected_persons:
    # As part of the process of 'stitching' the records of connected persons together with other records already dealing with these persons, I first check if connections can be made via the 
    # GND ID - and if not, I check the VIAF ID. Since donwloading VIAF IDs is a slow process, I try to use get them in one go through async. 
    # Once I extend this to connected organisations and places, I can get their VIAF records in the same process

        # This is step 1 of the stitching process
        for connected_person in person_selected.connected_persons:
            connected_person.connection_comment, connected_person.connection_type = person_relationship_parse("person", connected_person.connection_comment, connected_person.connection_type, person_new.sex)
            for external_id in connected_person.external_id:
                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
                if person_found:
                    connected_person.id = person_found["id"]
                    connected_person.name = person_found["name_preferred"] # Here, the year must be added. One should probably rename it as 'preview'. 
                    add_relationship_in_far_record(person_found, person_new, connected_person.connection_type) # This is step 2, the reciprocal connection
                    break # if a connection with one ID is found, the other connections would be the same. 

            if not person_found and connected_person.external_id:
                    list_of_ids_to_check.append(connected_person.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF
                    # (although the modul for getting IDs from VIAF currently only processes GND and ULAn)
    if person_selected.connected_organisations:    
        for connected_org in person_selected.connected_organisations:
            connected_org.connection_comment, connected_org.connection_type = person_relationship_parse("organisation", connected_org.connection_comment, connected_org.connection_type, person_new.sex)
            for external_id in connected_org.external_id:
                org_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
                if org_found:
                    connected_org.id = org_found["id"]
                    connected_org.name = org_found["name_preferred"] # Here, the year must be added. One should probably rename it as 'preview'. 
                    add_relationship_in_far_record(org_found, person_new, connected_person.connection_type) # This is step 2, the reciprocal connection
                    break # if a connection with one ID is found, the other connections would be the same. 
#           The following two lines are commented out until VIAF can deal with GND organisations
#            if not org_found and connected_org.external_id:
#                    list_of_ids_to_check.append(connected_org.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF
    if person_selected.connected_locations:
        for connected_location in person_selected.connected_locations:
            connected_location.connection_comment, connected_location.connection_type = person_relationship_parse("location", connected_location.connection_comment, connected_location.connection_type, person_new.sex)                    
            for external_id in connected_location.external_id:
                location_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
                if location_found:
                    connected_location.id = location_found["id"]
                    connected_location.name = location_found["name_preferred"]
                    add_relationship_in_far_record(location_found, person_new, connected_location.connection_type) # This is step 2, the reciprocal connection
                    break # if a connection with one ID is found, the other connections would be the same. 
#           The following two lines are commented out until VIAF can deal with GND locations
#            if not location_found and connected_location.external_id:
#                    list_of_ids_to_check.append(connected_location.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF

    # Here, I send the list of all collected IDs for which I need a VIAF ID to the function that contacts VIAF. 
    list_of_viaf_ids = await get_viaf_from_authority(list_of_ids_to_check)
#    print(list_of_viaf_ids)

    person_viaf_url = list_of_viaf_ids[person_new.external_id[0].uri]
    id = External_id()
    id.name = "viaf"
    id.uri = person_viaf_url
    id.id = person_viaf_url[21:]
    new_record_viaf_id = id.id # I need this later
    person_new.external_id.append(id)
    # this has to be expanded for organisations and locations, once this is possible
    # then, to the record of the connected person

    for connected_person in person_selected.connected_persons:
        if connected_person.external_id:
            if connected_person.external_id[0].uri in list_of_viaf_ids:
                person_viaf_url = list_of_viaf_ids[connected_person.external_id[0].uri]
                id = External_id()
                id.name = "viaf"
                id.uri = person_viaf_url
                id.id = person_viaf_url[21:]
                connected_person.external_id.append(id)    

    if person_selected.connected_persons:
        for connected_person in person_selected.connected_persons:                
#            connected_person.connection_comment, connected_person.connection_type = person_relationship_parse("person", connected_person.connection_comment, connected_person.connection_type, person_new.sex)
            if not connected_person.id and connected_person.external_id: # If there is already an id, no 'stitching' is required                               
                for external_id in connected_person.external_id:
                    if external_id.id != "DNB": # If it is, the connection has been made earlier
                    # This is 'stitching' step 1 for the records that can only be connected through VIAF
                        person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
                    if person_found:
                        connected_person.id = person_found["id"]
                        connected_person.name = person_found["name_preferred"] # Here, the year must be added. One should probably rename it as 'preview'. 
                         # if a connection with one ID is found, the other connections would be the same. 
                        add_relationship_in_far_record(person_found, person_new, connected_person.connection_type) # This is step 2, the reciprocal connection
                        break
            

            new_connected_person = Connected_entity()
            new_connected_person.id = connected_person.id
            new_connected_person.name = connected_person.name
            new_connected_person.external_id = connected_person.external_id
            if connected_person.name == "": # if there is no preview, i.e. no connection found
                new_connected_person.name = connected_person.name
            new_connected_person.connection_type = connected_person.connection_type
            new_connected_person.connection_time = connected_person.connection_time 
            new_connected_person.connection_comment = connected_person.connection_comment
            # In theory, one should also replace this time string through a proper date object However, since I don't assume that anything will ever be made with 
            # this information apart from displaying it, this is unnecessary or at least not urgent. 
            person_new.connected_persons.append(new_connected_person)

    if person_selected.connected_organisations:
        for connected_organisation in person_selected.connected_organisations:
            print("now processing connected organisation " + connected_organisation.name)
            new_connected_organisation = Connected_entity()
            new_connected_organisation.id = connected_organisation.id
            new_connected_organisation.external_id = connected_organisation.external_id
            new_connected_organisation.name = connected_organisation.name
            new_connected_organisation.connection_type = connected_organisation.connection_type
            new_connected_organisation.connection_time = connected_organisation.connection_time
            # For connection time see above under new connected person
            person_new.connected_organisations.append(new_connected_organisation)
    if person_selected.connected_locations:
        for connected_location in person_selected.connected_locations:
            # in not few cases, dates are written not into the date field but into the comment field of the connection, or they follow the descriptions "Wohnort" or "Wirkungsort"
            if re.match(connected_location_comment_is_date, connected_location.connection_comment): # This means that the 'comment' field contains information that should have gone into the 'time' field.
                if connected_location.connection_time:
                    connected_location.connection_time = connected_location.connection_time + ", " + connected_location.connection_comment
                else:
                    connected_location.connection_time = connected_location.connection_comment
                connected_location.connection_comment = ""
            elif connected_location.connection_comment[0:12] == "Wirkungsort ":
                connected_location.connection_time = connected_location.connection_comment[12:]
                connected_location.connection_comment = "wirkungsort"
            elif connected_location.connection_comment[0:8] == "Wohnort ":
                connected_location.connection_time = connected_location.connection_comment[8:]
                connected_location.connection_comment = "wohnort"

            new_connected_location = Connected_entity()
            new_connected_location.id = connected_location.id
            new_connected_location.external_id = connected_location.external_id
            new_connected_location.name = connected_location.name
            new_connected_location.connection_type = connected_location.connection_type
            new_connected_location.connection_time = connected_location.connection_time
            new_connected_location.connection_comment = connected_location.connection_comment
            # For connection time see above under new connected person (only relevant for location of activity)
            person_new.connected_locations.append(new_connected_location)
    person_new.comments = person_selected.comments

    # Here comes step 3 of the stitching process: checking if there is any record in Iconobase that has a reference to the new record (only relevant if the new record has no reference to that record)
    # I must define what external_id is! 
    #person_found = list(coll.find({"connected_persons.external_id.name": "viaf", "connected_persons.external_id.id": new_record_viaf_id.id}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1}))

#   The following line should be reinstated once every goes via VIAF, the line afterwards is a stopgap to work with both VIAF and GND
#    person_found = list(coll.find({"connected_persons.external_id.name" : "viaf", "connected_persons.external_id.id" : new_record_viaf_id}, {"id": 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
# record with sex
    list_found = list(coll.find({ "$or": [{"connected_persons.external_id.name" : "viaf", "connected_persons.external_id.id" : new_record_viaf_id}, {"connected_persons.external_id.name" : "GND", "connected_persons.external_id.id" : new_record_gnd_id}]}, {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
    print("far records found: ")
    print(list_found)

    for far_record in list_found:
        far_record_id = far_record["id"]
        if far_record["type"] == "Person":
            for connected_person in person_new.connected_persons:
                connection_already_made = False
                if connected_person.id == far_record_id:
                    connection_already_made = True
                        # This means that a connection has alredady been established by steps 1 and 2 and that nothing needs to be done
                    break
        elif far_record["type"] == "Organisation": 
            for connected_org in person_new.connected_organisations:
                connection_already_made = False
                if connected_org.id == far_record_id:
                    connection_already_made = True
                        # This means that a connection has alredady been established by steps 1 and 2 and that nothing needs to be done
                    break
        elif far_record["type"] == "Place":
            for connected_location in person_new.connected_locations:
                connection_already_made = False
                if connected_location.id == far_record_id:
                    connection_already_made = True
                    print("connection in location found")
                        # This means that a connection has alredady been established by steps 1 and 2 and that nothing needs to be done
                    break
        
        if connection_already_made == False: # i.e., one has to create a connection
            # first getting the data from the 'far record'
            far_record_connected_persons = far_record["connected_persons"]
            far_connection_type = ""
            for far_connected_person in far_record_connected_persons:              
                for far_external_id in far_connected_person["external_id"]:
                    if far_external_id["name"] == "viaf" and far_external_id["id"] == new_record_viaf_id:
                        far_connection_type = far_connected_person["connection_type"]
                        dbactions.add_connection_id_and_name(far_record_id, far_connected_person["name"], person_new.name_preferred, person_new.id) 
                new_connection = Connected_entity()
                new_connection.id = far_record_id
                new_connection.name = far_record["name_preferred"]
                new_connection.connection_type = person_relations.relation_correspondence(far_connection_type, person_new.sex)
    #            new_connection.connection_type = "counterpart to " + far_connection_type
                if far_record["type"] == "Person": 
                    person_new.connected_persons.append(new_connection)
                if far_record["type"] == "Organisation": 
                    person_new.connected_organisations.append(new_connection)
                if far_record["type"] == "Place": 
                    person_new.connected_locations.append(new_connection)
          
    dbactions.insertRecordPerson(person_new)
    return person_new.id




def org_ingest(org):
    # This function is about translating the imported information of a organisation into the information record used for the database. 
    # It directly sends the new records to the function for writing it and only returns its ID to metadata_dissection
    org_selected = org.potential_candidates[org.chosen_candidate]               
    org_new = Organisation_db()
    org_new.id = generate()
    org_new.type = "Organisation"
    org_new.org_type1.append(role_org_type_correspondence[org.role])
    org_new.external_id = org_selected.external_id
    # Here, the VIAF ID is added to the organisation's record
# I have cancelled the next two lines as long as VIAF doesn't work properly with organisation IDs. 
    #new_record_viaf_id = get_viaf_from_authority(org_new.external_id[0].uri)
    #org_new.external_id.append(new_record_viaf_id)
    connection_already_made = False
    org_new.name_preferred = org_selected.name_preferred
    org_new.name_variant = org_selected.name_variant
    if org.name not in org_new.name_variant: # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for variants and not a word search. 
        org_new.name_variant.append(org.name)
    org_new.dates_from_source = org_selected.dates_from_source # A lot of works needs to be done here. 
    if org_selected.connected_persons:
        # The GND has very few standardised abbreviations for relationships, largely 'bezf' (family relationship), 'bezb' (professional relationship) and 'beza' (anything else)
        # Sometimes, the concrete type of relationship is given in a comment field, but it is not standardised. 
        # Hence, the only thing I can come up with is the following: 
            # If there is only the general abbreviation, I replace it with a general English phrase
            # If there is the general abbreviation plus a common word in the comments field, I use an English translation of the concrete relationship)
            # If there is the general abbreviation plus a word in the comments field that is not common (or simply has escaped me), the relationship will be a general English phrase plus the original German comment
        for connected_person in org_selected.connected_persons: 
            match connected_person.connection_type: 
                case "rela":
#                    print(connected_person.connection_comment)
                    if connected_person.connection_comment == "Eigentümer" or connected_person.connection_comment == "Eigentümer":
                        # The word "Eigentümer" is given here twice in two different encodings - oddly, that seems to help. 
                        connected_person.connection_type = "Owner"
                    else:
                        if connected_person.connection_comment:
                            connected_person.connection_type = "connected (" + connected_person.connection_comment + ")"  
                        else: 
                            connected_person.connection_type = "connected"
                case "saml":
                    connected_person.connection_type = "Collector"
                case _:            
                    if connected_person.connection_comment:
                        connected_person.connection_type = "connected (" + connected_person.connection_type + "; " + connected_person.connection_comment + ")"
                    else:
                        connected_person.connection_type = "connected (" + connected_person.connection_type +  ")"             
            new_connected_person = Connected_entity()
            new_connected_person.external_id = connected_person.external_id
            new_connected_person.name = connected_person.name
            new_connected_person.connection_type = connected_person.connection_type
            new_connected_person.connection_time = connected_person.connection_time 
            # In theory, one should also replace this time string through a proper date object However, since I don't assume that anything will ever be made with 
            # this information apart from displaying it, this is unnecessary or at least not urgent. 
            org_new.connected_persons.append(new_connected_person)
    if org_selected.connected_organisations:
            # There are three constellations: precursors, successors, and parent organisations (there are apparently no links to child organisations)
        for connected_organisation in org_selected.connected_organisations:
            match connected_organisation.connection_type:
                case "vorg":          
                    if connected_organisation.connection_comment:
                        connected_organisation.connection_type = "precursor (" + connected_organisation.connection_comment + ")"
                    else: 
                        connected_organisation.connection_type = "precursor"
                case "nach":          
                    if connected_organisation.connection_comment:
                        connected_organisation.connection_type = "successor (" + connected_organisation.connection_comment + ")"
                    else: 
                        connected_organisation.connection_type = "successor"
                case "adue":          
                    if connected_organisation.connection_comment:
                        connected_organisation.connection_type = "parent organisation (" + connected_organisation.connection_comment + ")"
                    else: 
                        connected_organisation.connection_type = "parent organisation"
                case _: #not sure if this will ever happen
                    if connected_organisation.connection_comment:
                        connected_organisation.connection_type = "connected (" + connected_organisation.connection_type + "; " + connected_organisation.connection_comment + ")"
                    else:
                        connected_organisation.connection_type = "connected (" + connected_organisation.connection_type +  ")"
            new_connected_organisation = Connected_entity()
            new_connected_organisation.external_id = connected_organisation.external_id
            new_connected_organisation.name = connected_organisation.name
            new_connected_organisation.connection_type = connected_organisation.connection_type
            new_connected_organisation.connection_time = connected_organisation.connection_time
            # For connection time see above under new connected person
            org_new.connected_organisations.append(new_connected_organisation)
    if org_selected.connected_locations:
        for connected_location in org_selected.connected_locations:
            # For locations, there are two standard relationships, 'orta' for the seat of an organisation, and 'geow' for the area of its responsibility         
            match connected_location.connection_type:
                case "orta":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Seat + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Seat"
                case "geow":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Area of responsibility + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Area of responsibility"
                case _:
                    if connected_location.connection_comment:
                        connected_location.connection_type = "connected location + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "connected (details to be determined)"

            new_connected_location = Connected_entity()
            new_connected_location.external_id = connected_location.external_id
            new_connected_location.name = connected_location.name
            new_connected_location.connection_type = connected_location.connection_type
            new_connected_location.connection_time = connected_location.connection_time
            # For connection time see above under new connected person (only relevant for location of activity)
            org_new.connected_locations.append(new_connected_location)
    org_new.comments = org_selected.comments
    done = dbactions.insertRecordOrganisation(org_new)

    return org_new.id




def place_ingest(place):
    # This function is about translating the imported information of a place into the place record used for the database. 
    # It directly sends the new records to the function for writing it and only returns its ID to metadata_dissection
    print("place_ingest, start, number of potential candidates:")
    print(len(place.potential_candidates))
    print("place_ingest, start, number of chosen candidate")
    print(place.chosen_candidate)
    place_selected = place.potential_candidates[place.chosen_candidate]               
    place_new = Place_db()
    place_new.id = generate()
    place_new.type = "Place"
    place_new.place_type1 = ["Town - historical"]
    place_new.external_id = place_selected.external_id
    place_new.name_preferred = place_selected.name_preferred
    place_new.name_variant = place_selected.name_variant
    if place.name not in place_new.name_variant: # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for variants and not a word search. 
        place_new.name_variant.append(place.name)
    place_new.dates_from_source = place_selected.dates_from_source # A lot of works needs to be done here. 
    if place_selected.connected_persons:
        # The GND has very few standardised abbreviations for relationships, largely 'bezf' (family relationship), 'bezb' (professional relationship) and 'beza' (anything else)
        # Sometimes, the concrete type of relationship is given in a comment field, but it is not standardised. 
        # Hence, the only thing I can come up with is the following: 
            # If there is only the general abbreviation, I replace it with a general English phrase
            # If there is the general abbreviation plus a common word in the comments field, I use an English translation of the concrete relationship)
            # If there is the general abbreviation plus a word in the comments field that is not common (or simply has escaped me), the relationship will be a general English phrase plus the original German comment
        for connected_person in place_selected.connected_persons: 
            match connected_person.connection_type: # I keep the match structure here in case that there is a constellation where I need it, but I doubt htat it will ever happen
                case _:            
                    if connected_person.connection_comment:
                        connected_person.connection_type = "connected (" + connected_person.connection_type + "; " + connected_person.connection_comment + ")"
                    else:
                        connected_person.connection_type = "connected (" + connected_person.connection_type +  ")"             
            new_connected_person = Connected_entity()
            new_connected_person.external_id = connected_person.external_id
            new_connected_person.name = connected_person.name
            new_connected_person.connection_type = connected_person.connection_type
            new_connected_person.connection_time = connected_person.connection_time 
            # In theory, one should also replace this time string through a proper date object However, since I don't assume that anything will ever be made with 
            # this information apart from displaying it, this is unnecessary or at least not urgent. 
        place_new.connected_persons.append(new_connected_person)
    if place_selected.connected_organisations:
            # I am not sure if this will ever be needed, so I have here the minimum requirements, just in case
        for connected_organisation in place_selected.connected_organisations:
            match connected_organisation.connection_type:
                case _: 
                    if connected_organisation.connection_comment:
                        connected_organisation.connection_type = "connected (" + connected_organisation.connection_type + "; " + connected_organisation.connection_comment + ")"
                    else:
                        connected_organisation.connection_type = "connected (" + connected_organisation.connection_type +  ")"
            new_connected_organisation = Connected_entity()
            new_connected_organisation.external_id = connected_organisation.external_id
            new_connected_organisation.name = connected_organisation.name
            new_connected_organisation.connection_type = connected_organisation.connection_type
            new_connected_organisation.connection_time = connected_organisation.connection_time
            # For connection time see above under new connected person
            place_new.connected_organisations.append(new_connected_organisation)
    if place_selected.connected_locations:
        for connected_location in place_selected.connected_locations:
            # For locations, there are two standard relationships, 'orta' for the seat of an organisation, and 'geow' for the area of its responsibility         
            match connected_location.connection_type:
                case "vorg":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "formerly called + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "formerly called"
                case "nach":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "later called + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "later called"
                case "nazw":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "temporarily called + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "temporarily called"
                case "obpa":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "parent location + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "parent location"
                case "orta":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Seat + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Seat"
                case "geow":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Area of responsibility + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Area of responsibility"
                case _:
                    if connected_location.connection_comment:
                        connected_location.connection_type = "connected location + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "connected (details to be determined)"

            new_connected_location = Connected_entity()
            new_connected_location.external_id = connected_location.external_id
            new_connected_location.name = connected_location.name
            new_connected_location.connection_type = connected_location.connection_type
            new_connected_location.connection_time = connected_location.connection_time
            # For connection time see above under new connected person (only relevant for location of activity)
            place_new.connected_locations.append(new_connected_location)
    place_new.comments = place_selected.comments
    place_new.coordinates = place_selected.coordinates # I leave them now as they are, but perhaps I should remove duplicates
    done = dbactions.insertRecordPlace(place_new)

    return place_new.id


#person = Person()
#person_import = Person_import()
#person.chosen_candidate = 0
#person.role = "aut"
#external_id = External_id()
#external_id.id = "12345"
#external_id.name = "GND"
#person_import.external_id.append(external_id)
#person_import.name_preferred = "Lautensack, Paul"
#person_import.name_variant = ["Lautensaccius, Paulus", "Lautensack, Paulus"]
#person_import.sex = "male"
#connected_person = Connected_entity()
#connected_person.name = "Lautensack, Hans"
#connected_person.connection_type = "bezf"
#connected_person.connection_comment = "Sohn"
#person_import.connected_persons.append(connected_person)
#connected_location = Connected_entity()
#connected_location.name = "Bamberg"
#connected_location.connection_type = "ortg"
#person.potential_candidates.append(person_import)

#person_treated = person_ingest(person)
#print(person_treated)







        



        