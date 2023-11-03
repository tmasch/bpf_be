import urllib.request
import requests
import xml.etree.ElementTree
from classes import *
import re
from dbactions import *
url_replacement = {" " : "%20", "ä" : "%C3%A4", "ö" : "%C3%B6", "ü" : "%C3%BC", "ß" : r"%C3%9F"} #perhaps more signs will have to be added here later
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.bpf
coll = db.bpf





def get_viaf_from_gnd(gnd_id):
    # This function takes the GND ID as a string and returns the VIAF ID as a string
    urn_gnd = r'http://viaf.org/viaf/sourceID/DNB|' + gnd_id
    urn_viaf = requests.get(urn_gnd)
    ### I don't continue because the API apparently does not give the result I need. 
    


def person_identification(person):
# This function is used for every person named in the bibliographic record (author, editor, printer etc.)
# It will first search if a record for this person is already in the MongoDB database (this section has not yet been written)
    candidates = []
    if person.id:
        person_found = coll.find_one({"external_id": {"$elemMatch": {"name": person.id_name, "id": person.id}}}, {"_id": 1, "name_preferred": 1})
        if person_found:
            person.internal_id = str(person_found["_id"])
            person.internal_id_preview = person_found["name_preferred"] # The date should be added, but I first have to write how it is to be parsed
        else:
            if person.id_name == "GND": # I will have to create similar things for other authority files
                authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + person.id + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
                person.potential_candidates = gnd_parsing_person(authority_url)
    else:
        candidates_result = coll.find({"name_preferred" : person.name}, {"_id": 1, "name_preferred" : 1})
        for candidate_result in candidates_result:
            candidate = Person_import()   
            candidate.internal_id = str(candidate_result["_id"])
            candidate.name_preferred = candidate_result["name_preferred"]

            person.potential_candidates.append(candidate)
        candidates_result = coll.find({"name_variant" : person.name}) #I search first for the preferred names (assuming that it is more likely there will be a good match, and only later for the variants)
        for candidate_result in candidates_result:
            candidate.internal_id = str(candidate_result["_id"])
            candidate.name_preferred = candidate_result["name_preferred"]
            if candidate.id not in person.potential_candidates:
                person.potential_candidates.append(candidate)
#                print(person.potential_candidates)
        if not person.potential_candidates: #if nothing has been found
            person_name_search = person.name
            for old, new in url_replacement.items():
                person_name_search = person_name_search.replace(old, new)
            print(person_name_search)
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Per%3D' + person_name_search + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
            print(authority_url)
            person.potential_candidates = gnd_parsing_person(authority_url)
        if not person.potential_candidates: #if still nothing has been found, a keyword search is performed instead of a string search. 
            name_divided = person_name_search.split("%20")
            name_query = ""           
            for word in name_divided:
                search_phrase = r"Per=" + word + r"%20and%20" # I don't get it, but the thing only works if the "=" is written as such and not as Percent code. Above, it is different. 
                name_query = name_query + search_phrase
            authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=' + name_query + r'BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'    
            print(authority_url)
            person.potential_candidates = gnd_parsing_person(authority_url)
    if len(person.potential_candidates) == 1: # If there is only one entry for this person, it is by default selected (although the user can also run a new search, once this is established)
        person.chosen_candidate = 0

    
    return person         
                

    
    # This is currently unconnected
#    if not person.id:
#        for old, new in url_replacement.items():
#            person.name = person.name.replace(old, new)
#        authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Per%3D' + person.name + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
#    print(authority_url)

    # End of the unconnected section
    
def gnd_parsing_person(authority_url):
    potential_persons_list = []
    url = urllib.request.urlopen(authority_url)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    #print(root)
    
    for record in root[2]:
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
                case "035":
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                pe_id = External_id()
                                pe_id.name = "GND"
                                pe_id.id = step2.text[8:] #The latter cuts out the prefix '(DE-588)'.
                                if not pe.external_id: # Sometimes, the record containing the GND ID appears twice, hence it should not be added a second time. 
                                    pe.external_id.append(pe_id)
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
                            case "c": # For rulers, comments on Territory, title and time of ruling. 
                                # I put that now into a comment field. Once I have all the structure for persons' offices I might try to make an automatic import,
                                # but I fear it is too messy to make it worthwhile. 
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
                                    conn_pe.connection_time = step2.text
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
                                    conn_org.connection_time = step2.text
                    pe.connected_organisations.append(conn_org)
                case "548":
                    date = Date_import()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                date.datestring = step2.text
                            case "4":
                                if step2.text[0:4] != "http": # in this subfield are both the relation codes and a URI for the relation codes, I don't need the latter
                                    date.datetype = step2.text
                    if date.datetype == "datl":
                        date_preview = " (" + date.datestring + ")"
                    if date.datetype == "datw" and date_preview == "": # only shown in the preview if there is no datl
                        date_preview = " (active: " + date.datestring + ")" 
                    pe.dates_from_source.append(date)
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
                                    conn_pl.connection_time = step2.text
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
        if pe.comments:                
            comments_preview = " (" + pe.comments + ")"
        if pe.name_variant:
            name_variant_preview = ", also called: "
            for variant in pe.name_variant:
                name_variant_preview = name_variant_preview + variant + "; "
            name_variant_preview = name_variant_preview[:-2]

        pe.preview = pe.name_preferred + date_preview + ortg_preview + ortw_preview + orts_preview + name_variant_preview + comments_preview
        potential_persons_list.append(pe)
        print(potential_persons_list)
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
    
    return potential_persons_list


person = Person()
person.id_name = "GND"
#person.id = "11900108X" #Lautensack
#person.id = "118650130" # Aristotle
#person.id = "118780743" #Louis XVIII
person.name = "Lautensack, Paul"
#person.name = "Rubens, Peter Paul"
#person.name = "Andreas Asula"
record = person_identification(person)




