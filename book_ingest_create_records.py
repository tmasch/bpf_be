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
import dbactions
from pymongo import MongoClient


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

class Person_against_duplication(BaseModel):
    preview : Optional[str] = ""
    id : Optional[str] = ""
    person_type1 : Optional[list[str]]  = []




def metadata_dissection(metadata):


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
            if person.potential_candidates[person.chosen_candidate]: # I make this awkward construction to avoid 'out of range' exceptions
                if person.potential_candidates[person.chosen_candidate].internal_id:
                    no_new_person_chosen_from_list = True

            if person.internal_id: #In this case, no record has to be added
                if person.internal_id_person_type1_needed: 
                    #If the person has an additional person_type1 in the new entry, it has to be added to the person record. 
                    dbactions.add_person_type(person.internal_id, person.internal_id_person_type1_needed)
            elif no_new_person_chosen_from_list:
                if person.internal_id_person_type1_needed:
                    print("Type1 to be added:")
                    print(person.potential_candidates[person.chosen_candidate].internal_id) 
                    print(person.internal_id_person_type1_needed)
                    dbactions.add_person_type(person.potential_candidates[person.chosen_candidate].internal_id, person.internal_id_person_type1_needed)

            else: 
                print("new person")
                for person_against_duplication in persons_list:
                    print("in loop for new person")
                    if person_against_duplication.preview == person.potential_candidates[person.chosen_candidate].preview: 
                        # this means, if a person not yet in the database appears twice in the record, in different roles
                        person.internal_id = person_against_duplication.id
                        person_type = role_person_type_correspondence[person.role]
                        if  person_type not in person_against_duplication.person_type1: 
                            # Since the type is created automatically from the role, there can be only one type in person
                            dbactions.add_person_type(person.internal_id, person_type)


                        print("New Person is a duplicate")
                        break
                else: 
                        print("New person is not a duplicate")
                        person.internal_id = person_ingest(person)
                        person_against_duplication.preview = person.potential_candidates[person.chosen_candidate].preview
                        person_against_duplication.id = person.internal_id
                        person_against_duplication.person_type1 = role_person_type_correspondence[person.role]
                        persons_list.append(person_against_duplication)
                        print("record against duplication: ")
                        print(person_against_duplication)
    return metadata



def person_ingest(person):
    person_selected = person.potential_candidates[person.chosen_candidate]               
    person_new = Person_db()
    person_new.id = generate()
    person_new.type = "Person"
    person_new.person_type1.append(role_person_type_correspondence[person.role])
    person_new.external_id = person_selected.external_id
    person_new.name_preferred = person_selected.name_preferred
    person_new.name_variant = person_selected.name_variant
    if person.name not in person_new.name_variant: # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for variants and not a word search. 
        person_new.name_variant.append(person.name)
    person_new.sex = person_selected.sex
    person_new.dates_from_source = person_selected.dates_from_source # A lot of works needs to be done here. 
    if person_selected.connected_persons:
        # The GND has very few standardised abbreviations for relationships, largely 'bezf' (family relationship), 'bezb' (professional relationship) and 'beza' (anything else)
        # Sometimes, the concrete type of relationship is given in a comment field, but it is not standardised. 
        # Hence, the only thing I can come up with is the following: 
            # If there is only the general abbreviation, I replace it with a general English phrase
            # If there is the general abbreviation plus a common word in the comments field, I use an English translation of the concrete relationship)
            # If there is the general abbreviation plus a word in the comments field that is not common (or simply has escaped me), the relationship will be a general English phrase plus the original German comment
        for connected_person in person_selected.connected_persons:
            match connected_person.connection_type:
                case "bezf":
                    if connected_person.connection_comment: 
                        if connected_person.connection_comment in person_person_connection_type_correspondence:
                            connected_person.connection_type = person_person_connection_type_correspondence[connected_person.connection_comment]
                        else:
                            connected_person.connection_type = "family relation (" + connected_person.connection_comment + ")"
                    else: 
                        connected_person.connection_type = "family relation (to be determined)"
                case "bezb":
                    if connected_person.connection_comment: 
                        if connected_person.connection_comment in person_person_connection_type_correspondence:
                             connected_person.connection_type = person_person_connection_type_correspondence[connected_person.connection_comment]
                        else:
                            connected_person.connection_type = "professional relation (" + connected_person.connection_comment + ")"
                    else: 
                        connected_person.connection_type = "professional relation (to be determined)"
                case "beza":
                    if connected_person.connection_comment:
                        connected_person.connection_type = "connected (" + connected_person.connection_comment + ")"
                    else:
                        connected_person.connection_type = "connected (details to be determined)"
                case _: #not sure if this will ever happen
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
            person_new.connected_persons.append(new_connected_person)
    if person_selected.connected_organisations:
        for connected_organisation in person_selected.connected_organisations:
            # I have the feeling that the only type of relationship that is common here is 'affi', 'affiliated to'. 
            match connected_organisation.connection_type:
                case "affi":          
                    if connected_organisation.connection_comment:
                        connected_organisation.connection_type = "affiliation (" + connected_organisation.connection_comment + ")"
                    else: 
                        connected_organisation.connection_type = "affiliation"
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
            person_new.connected_organisations.append(new_connected_organisation)
    if person_selected.connected_locations:
        for connected_location in person_selected.connected_locations:
            # For locations, there are three standard relationships, for the location of birth, death, and activity. There are a few others that will hardly ever appear. 
            # I don't think that there will be many situations in which the comments field is used - unless, perhaps, if some location assignations are doubtful
            match connected_location.connection_type:
                case "ortg":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Place of birth + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Place of birth"
                case "orts":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Place of death + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Place of death"
                case "ortw":
                    if connected_location.connection_comment:
                        connected_location.connection_type = "Place of activity + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_location.connection_type = "Place of activity"
                case _:
                    if connected_location.connection_comment:
                        connected_location.connection_type = "connected location + (" + connected_location.connection_comment + ")"
                    else: 
                        connected_place.connection_type = "connected (details to be determined)"

            new_connected_location = Connected_entity()
            new_connected_location.external_id = connected_location.external_id
            new_connected_location.name = connected_location.name
            new_connected_location.connection_type = connected_location.connection_type
            new_connected_location.connection_time = connected_location.connection_time
            # For connection time see above under new connected person (only relevant for location of activity)
            person_new.connected_locations.append(new_connected_location)
    person_new.comments = person_selected.comments
    done = dbactions.insertRecordPerson(person_new)

    return person_new.id

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







        



        