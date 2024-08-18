#pylint: disable=C0301,E1101,C0116,C0103,C0303,C0302
"""
This module contains functions that transform the information taken from several bibliographic resources (in books_parsing manifest, books_parsing_bibliographies and gndparse), 
according to the selections made by the user in NewRessource.vue, into a format ready for importing it into Iconobase. 
There is normally, depending on the material, either one Manuscript or one Book record. 
If there are any persons, organisations (including repositories) and places connected to the book or manuscript that do not yet have an authority record in the database, authority records for them are created first, and then the book or manuscript record is linked to them. 
In a future setting, these authority records should not be created automatically, but first displayed to the user to see if anything should be added or corrected. 
Furthermore, now the 'secondary' references (e.g., if we have the Place of Birth of a printer) are merely copied into the record. 
Later, there should be a search if there are already records for 
"""

#from typing import Optional
import logging
from nanoid import generate
#import requests
#from pydantic import BaseModel

import db_actions
import classes
from ingest_organisation import ingest_organisation
from ingest_person import ingest_person
from ingest_place import ingest_place
import parsing_helpers
#dbname = db_actions.get_database()
#coll=dbname['bpf']

logger = logging.getLogger(__name__)




#class Person_against_duplication(BaseModel): 
#    """
#    I have these classes here and not in 'classes' because they are only needed in these functions.
#    """
#    preview : Optional[str] = ""
#    id : Optional[str] = ""
#    person_type1 : Optional[list[str]]  = []

#class Org_against_duplication(BaseModel):
#    """
#\todo
#    """
#    preview : Optional[str] = ""
#    id : Optional[str] = ""
#    org_type1 : Optional[list[str]]  = []

#class Place_against_duplication(BaseModel):
#    """
#\todo
#    """
#    preview : Optional[str] = ""
#    id : Optional[str] = ""
#    place_type1 : Optional[list[str]]  = []

@classes.func_logger
async def metadata_dissection(metadata):
    print("creating metadata records")
    persons_list = await metadata_persons(metadata)
    print("-------------------------------------- organisations")
    orgs_list = await metadata_organisations(metadata)
    print("-------------------------------------- places")
    places_list = await metadata_place(metadata)
    print("-------------------------------------- repositories")
    org = await metadata_repositories(metadata)
    print("-------------------------------------- manuscript")
    if metadata.material == "m": # If the item has been identified as a manuscript
        new_manuscript = await populate_manuscript_from_metadata(metadata)
        db_actions.insert_record_manuscript(new_manuscript)
        record_id=new_manuscript.id
    print("-------------------------------------- book")
    if metadata.material == "b": # If the item has been identified as printed book
        new_book = await populate_book_from_metadata(metadata)
        db_actions.insert_record_book(new_book)
        record_id=new_book.id

    print("--------------------------------------")
    new_pages = await populate_pages_from_metadata(metadata,record_id,org)
    db_actions.insert_record_pages(new_pages)

    return 1

@classes.func_logger
async def metadata_persons(metadata):

    if metadata.bibliographic_information or metadata.making_processes:
        # Section on Person
        # There are three constellations
        # (a): A person that is already in Iconobase was identified via an ID. In this case, there is no list of potential candidates. 
        # (b): Several persons already in Iconobase were identified through a name search. in this list, there is a list of potential candidates, one of whom has been selected
        #       (In cases a and b, no person has to be added, but possibly some person_type1 has to be added)
        # (c): Persons not in iconobase have been found - whether it be one found via an ID or several found via a name search, they will be in a list of potential candidates
        #          (In this case, a new record for the selected person has to be added, and it will come with the person_type1 required by the role of the person)
        persons_entered_list = [] # This list contains both persons from the bibliographical record and artists
        persons_list = [] # This list exists to make sure that if the same person is mentioned twice in different functions, e.g. as author and publisher, there is only one record created 
        person_against_duplication = classes.PersonAgainstDuplication()
        
        if metadata.bibliographic_information[0].persons:
            for person in metadata.bibliographic_information[0].persons:
                persons_entered_list.append(person)
#            persons_entered_list = metadata.bibliographic_information[0].persons
#            print("--------------------------------------")
#            print("Persons in metadata.bibliographic_information[0]: ")
#            print(metadata.bibliographic_information[0].persons)
            print("--------------------------------------")
            print("Making_processes in metadata: ")
            print(metadata.making_processes)
        if metadata.making_processes:
            for making_process in metadata.making_processes:
                if making_process.person.name:
                    persons_entered_list.append(making_process.person)
    #                print("--------------------------------------")
    #                print("Persons in metadata.bibliographic_information[0] after adding making_process to persons_list: ")
    #                print(metadata.bibliographic_information[0].persons)
        
        if len(persons_entered_list) > 0:
            for person in persons_entered_list:
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
                        db_actions.add_person_type(person.internal_id, person.internal_id_person_type1_needed)
                elif no_new_person_chosen_from_list: # Scenario (b) above
                    person.internal_id = person.potential_candidates[person.chosen_candidate].internal_id
                    if person.potential_candidates[person.chosen_candidate].internal_id_person_type1_comment:
    #                    print("Type1 to be added:")
    #                    print(person.potential_candidates[person.chosen_candidate].internal_id) 
    #                    print(person.internal_id_person_type1_needed)
                        db_actions.add_person_type(person.potential_candidates[person.chosen_candidate].internal_id, person.internal_id_person_type1_needed)

                else: 
    #                print("new person")
                    for person_against_duplication in persons_list:
    #                    print("in loop for new person")
                        if person_against_duplication.preview == person.potential_candidates[person.chosen_candidate].preview:
                            # this means, if a person not yet in the database appears twice in the record, in different roles
                            person.internal_id = person_against_duplication.id
                            person_type = parsing_helpers.map_role_to_person_type(person.role)
                            if  person_type not in person_against_duplication.person_type1: 
                                # Since the type is created automatically from the role, there can be only one type in person
                                db_actions.add_person_type(person.internal_id, person_type)


    #                        print("New Person is a duplicate")
                            break
                    else: 
    #                        print("New person is not a duplicate")
                        person.internal_id = await ingest_person(person)
                        person_against_duplication.preview = person.potential_candidates[person.chosen_candidate].preview
                        person_against_duplication.id = person.internal_id
                        person_against_duplication.person_type1 = parsing_helpers.map_role_to_person_type(person.role)
                        persons_list.append(person_against_duplication)
    #                       print("record against duplication: ")
    #                       print(person_against_duplication)
    return persons_list

@classes.func_logger
async def metadata_organisations(metadata):
    print("Organisation")
    if metadata.bibliographic_information:
    # Section on Organisations
        # There are three constellations
        # (a): An organisation that is already in Iconobase was identified via an ID. In this case, there is no list of potential candidates. 
        # (b): Several organisations already in Iconobase were identified through a name search. in this list, there is a list of potential candidates, one of whom has been selected
        #       (In cases a and b, no organisation has to be added, but possibly some org_type1 has to be added)
        # (c): Organisations not in iconobase have been found - whether it be one found via an ID or several found via a name search, they will be in a list of potential candidates
        #          (In this case, a new record for the selected organisation has to be added, and it will come with the org_type1 required by the role of the person)

        
        
        orgs_list = [] # This list exists to make sure that if the same organisation is mentioned twice in different functions, e.g. as author and publisher, there is only one record created 
        org_against_duplication = classes.OrgAgainstDuplication()
        
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
                        db_actions.add_organisation_type(org.internal_id, org.internal_id_org_type1_needed)
                elif no_new_org_chosen_from_list: # Scenario (b) above
                    org.internal_id = org.potential_candidates[org.chosen_candidate].internal_id
                    if org.potential_candidates[org.chosen_candidate].internal_id_org_type1_comment:
    #                    print("Type1 to be added:")
    #                    print(org.potential_candidates[org.chosen_candidate].internal_id) 
    #                    print(org.internal_id_org_type1_needed)
                        db_actions.add_organisation_type(org.potential_candidates[org.chosen_candidate].internal_id, org.internal_id_org_type1_needed)

                else: 
    #                print("new organisation")
                    for org_against_duplication in orgs_list:
    #                    print("in loop for new organisaton")
                        if org_against_duplication.preview == org.potential_candidates[org.chosen_candidate].preview: 
                            # this means, if an organisation not yet in the database appears twice in the record, in different roles
                            org.internal_id = org_against_duplication.id
                            org_type = parsing_helpers.map_role_to_organisation_type(org.role)
                            if  org_type not in org_against_duplication.org_type1: 
                                # Since the type is created automatically from the role, there can be only one type in organisation
                                db_actions.add_organisation_type(org.internal_id, org_type)


    #                        print("New Organisation is a duplicate")
                            break
                    else: 
    #                        print("New Organisation is not a duplicate")
                        org.internal_id = await ingest_organisation(org)
                        org_against_duplication.preview = org.potential_candidates[org.chosen_candidate].preview
                        org_against_duplication.id = org.internal_id
                        org_against_duplication.org_type1 = parsing_helpers.map_role_to_organisation_type(org.role)
                        orgs_list.append(org_against_duplication)
    #                        print("record against duplication: ")
                        print(org_against_duplication)
    return orgs_list

@classes.func_logger
async def metadata_place(metadata):
    if metadata.bibliographic_information or metadata.making_processes:
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
        
        
        places_entered_list = [] # This list contains both places from the bibliographical record and places of making
        places_list = [] # This list exists to make sure that if the same organisation is mentioned twice in different functions, e.g. as author and publisher, there is only one record created 
        place_against_duplication = classes.PlaceAgainstDuplication()
        
        if metadata.bibliographic_information[0].places:
            for place in metadata.bibliographic_information[0].places:
                places_entered_list.append(place)
        if metadata.making_processes:
            for making_process in metadata.making_processes:
                if making_process.place.name:
                    places_entered_list.append(making_process.place)
        if len(places_entered_list) > 0:
            for place in places_entered_list:
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
                        place.internal_id = db_actions.copy_place_record(place.internal_id, place.internal_id_place_type1_needed) # It needs to be connected with the id of the new record
                elif no_new_place_chosen_from_list: # Scenario (b) above
                    place.internal_id = place.potential_candidates[place.chosen_candidate].internal_id
                    if place.potential_candidates[place.chosen_candidate].internal_id_place_type1_comment:
                        print("Type1 to be added:")
                        print(place.potential_candidates[place.chosen_candidate].internal_id) 
                        print(place.internal_id_place_type1_needed)
                        place.internal_id = db_actions.copy_place_record(place.potential_candidates[place.chosen_candidate].internal_id, place.internal_id_place_type1_needed) 
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
                                place.internal_id = db_actions.copy_place_record(place.internal_id, place_type)
                                # It needs to be connected with the id of the new record

                            print("New Place is a duplicate")
                            break
                
                    else: 
                        print("New Place is not a duplicate")
                        place.internal_id = await ingest_place(place)
                        place_against_duplication.preview = place.potential_candidates[place.chosen_candidate].preview
                        place_against_duplication.id = place.internal_id
                        place_against_duplication.place_type1 = ["Town - historical"]
                        places_list.append(place_against_duplication)
                        print("record against duplication: ")
                        print(place_against_duplication)
    return places_list

@classes.func_logger
async def metadata_repositories(metadata):
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
                db_actions.add_organisation_type(org.internal_id, org.internal_id_org_type1_needed)
        elif no_new_org_chosen_from_list: # Scenario (b) above
            org.internal_id = org.potential_candidates[org.chosen_candidate].internal_id
            if org.potential_candidates[org.chosen_candidate].internal_id_org_type1_comment:
                print("Repository chosen from list - Type1 to be added:")
                print(org.potential_candidates[org.chosen_candidate].internal_id) 
                print(org.internal_id_org_type1_needed)
                db_actions.add_organisation_type(org.potential_candidates[org.chosen_candidate].internal_id, org.internal_id_org_type1_needed)
        else: 
            print("new repository")
            org.potential_candidates[org.chosen_candidate].internal_id = await ingest_organisation(org)
    return org

@classes.func_logger
async def populate_manuscript_from_metadata(metadata):
# Section on Manuscripts
    print("checking manuscript")
#    book_record_id=""
#    if metadata.material == "m": # If the item has been identified as a manuscript
    print("creating manuscript record")
    new_manuscript = classes.ManuscriptDb()
    new_manuscript.id = generate()
    print(new_manuscript.id)
    new_repository = classes.LinkToRepository()
    new_repository.place_id = metadata.repository[0].potential_candidates[metadata.repository[0].chosen_candidate].internal_id
    new_repository.id_preferred = metadata.shelfmark
    new_manuscript.repository.append(new_repository)
    new_manuscript.preview = metadata.repository[0].name + ", " + metadata.shelfmark

#        book_record_id = new_manuscript.id # I need that one later
#    print(book_record_id)
    return new_manuscript

@classes.func_logger
async def populate_book_from_metadata(metadata):
# Section on printed books
#    book_record_id=""
#        print("adding new book")
    new_book = classes.BookDb()
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
            new_bibliographic_id = classes.ExternalId()
            new_bibliographic_id = bibliographic_id
            new_book.bibliographic_id.append(new_bibliographic_id)
    if metadata.bibliographic_information[0].persons:
#            print("-------------------------------------------------------------------")
#            print("persons in metadata.bibliographic_information[0].persons at the end of metadata_dissection: ")
#            print(metadata.bibliographic_information[0].persons)
        for person in metadata.bibliographic_information[0].persons:
            new_person = classes.BookConnectedEntityDb()
            new_person.role = person.role
            if person.internal_id:
                new_person.id = person.internal_id
            else:
                new_person.name = person.name # This is a stopgap measure if a person could not be identified
            new_book.persons.append(new_person)
    if metadata.bibliographic_information[0].organisations:
        for org in metadata.bibliographic_information[0].organisations:
            new_org = classes.BookConnectedEntityDb()
            new_org.role = org.role
            if org.internal_id:
                new_org.id = org.internal_id
            else: 
                new_org.name = org.name # This is a stopgap measure if an organisation could not be identified
            new_book.organisations.append(new_org)
    if metadata.bibliographic_information[0].places:
        for place in metadata.bibliographic_information[0].places:
            new_place = classes.BookConnectedEntityDb()
            new_place.role = place.role
            if place.internal_id:
                new_place.id = place.internal_id
            else: 
                new_place.name = place.name # This is a stopgap measure if a place could not be identified
            new_book.places.append(new_place)
    new_book.preview = metadata.bibliographic_information[0].title + " (" + metadata.bibliographic_information[0].date_string + ")"


#        book_record_id = new_book.id # I'll need that later
#        print(new_book.date_start)
#        print("Completed book record")
#    print("insert book done")
#    print(book_record_id)
    return new_book

@classes.func_logger
async def populate_pages_from_metadata(metadata,book_record_id,org):
# Section on individual pages. 
# This class contains the list of individual pages from the IIIF manifest as well as information on repository and shelf marks. 
# This information will eventually be copied to the individual Artwork and Photo records, once the cropping of images is complete and those records are created.
# It is not clear if this record will be needed in the long term
    print("creating pages record")
#    stuff = classes.BookDb()
    new_pages = classes.PagesDb()
#    classes.PagesDb()
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
    if metadata.making_processes:
        for making_process in metadata.making_processes:
            print("adding making process: ")
            print(making_process)
            if making_process.person.name == "" and making_process.place.name == "" and making_process.date.datestring_raw == "":
                pass
            else:
                making_process_db = classes.MakingProcessDb()
                making_process_db.process_type = making_process.process_type
                if making_process.person.internal_id:
                    person = classes.ConnectedEntity()
                    person.id = making_process.person.internal_id # is apparently always there, if a person has been chosen
#                    print("role of person")
#                    print(making_process.person.role)
                    person.connection_type = making_process.person.role
#                    print("role of person inserted: ")
#                    print(person.connection_type)
                    person.name = making_process.person.potential_candidates[making_process.person.chosen_candidate].name_preferred # later to be replaced wth preview                 
                    making_process_db.person = person
#                    print("complete making process")
#                    print(making_process_db)
                if making_process.place.internal_id:
                    print("Place as entered in making_processs")
                    print(making_process.place)
                    place = classes.ConnectedEntity()
                    place.id = making_process.place.internal_id # is apparently always there, if a place has been chosen
#                    print("role of person")
#                    print(making_process.person.role)
                    place.connection_type = making_process.place.role
#                    print("role of person inserted: ")
#                    print(person.connection_type)
                    place.name = making_process.place.potential_candidates[making_process.place.chosen_candidate].name_preferred # later to be replaced wth preview                 
                    making_process_db.place = place
                    print("complete making process")
                    print(making_process_db)
                if making_process.date.datestring:
                    date = classes.Date()
                    date.date_string = making_process.date.datestring
                    print(making_process.date.datestring)
                    print(date.date_string)
                    date.date_start = making_process.date.date_start
                    date.date_end = making_process.date.date_end
                    making_process_db.date = date
                new_pages.making_processes.append(making_process_db)



    return new_pages
