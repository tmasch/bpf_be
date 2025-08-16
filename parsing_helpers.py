#pylint: disable=C0301,C0116
"""
Collection of routines for general parsing issues
"""
import re

import classes
import person_relations



@classes.func_logger
def map_role_to_place_type(role):
    role_place_type_correspondence = {"pup" : "Town - historical", "mfp" : "Town - historical", "uvp" : "Town - historical", "Place of Making" : "Town - historical"}
    place_type=role_place_type_correspondence[role]
    return place_type

@classes.func_logger
def map_role_to_organisation_type(role):
    role_org_type_correspondence = {"aut" : "Author", "edt" : "Author", "prt" : "Printer", "pbl" : "Printer", "col" : "Collection","art" : "Artist"}
    organisation_type=role_org_type_correspondence[role]
    return organisation_type

@classes.func_logger
def map_role_to_person_type(role):
    role_person_type_correspondence = {"aut" : "Author", "edt" : "Author", "rsp" : "Author", "prt" : "Printer", "pbl" : "Printer", "art" : "Artist"}
    person_type=role_person_type_correspondence[role]
    print("Role: "+role+" Person type: "+person_type)
    return person_type

@classes.func_logger
def map_person_to_connection_type(person):
    person_person_connection_type_correspondence = {"Vater" : "father", "Mutter" : "mother", "Bruder" : "brother", "Schwester" : "sister", "Sohn" : "son", "Tochter" : "daughter", \
                                         "Onkel" : "uncle", "Tante" : "aunt", "Neffe" : "nephew", "Nichte" : "niece", "Enkel" : "grandson", "Enkelin" : "granddaughter", 
                                         "Großvater" : "grandfather", "Großmutter" : "grandmother", "Ehemann" : "husband", "1. Ehemann" : "first husband", "2. Ehemann" : "second husband", \
                                         "3. Ehemann" : "third husband", "4. Ehemann" : "fourth husband", "5. Ehemann" : "fifth husband", "6. Ehemann" : "sixth husband", \
                                         "Ehefrau" : "wife", "1. Ehefrau" : "first wife", "2. Ehefrau" : "second wife", "3. Ehefrau" : "third wife", "4. Ehefrau" : "fourth wife", \
                                         "5. Ehefrau" : "fifth wife", "6. Ehefrau" : "sixth wife", "Adoptivvater" : "adoptive father", "Adoptivmutter" : "adoptive mother", \
                                         "Adoptivsohn" : "adopted son", "Adoptivtochter" : "adopted daughter", "Schwiegervater" : "father-in-law", "Schwiegermutter" : "mother-in-law", \
                                            "Schwiegersohn" : "son-in-law", "Schwiegertochter" : "daughter-in-law", "Schwager" : "brother-in-law", "Schwägerin" : "sister-in-law", \
                                                "Schüler" : "pupil", "Lehrer" : "teacher"}
    connection_type=person_person_connection_type_correspondence[person]
    return connection_type

@classes.func_logger
def parse_relationship(main_entity_type, connected_entity_type, connection_comment, connection_type, person_new_sex):
# This module is a transmission for the terms that describe a relationship - it does some preliminary parsing and then calls a function in person_relations, that contains lists of the relevant translations
    connection_type_raw = ""
    connection_comment_pattern = r'([^,\(]*)([,\()])(.*)'
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
    if main_entity_type == "person":
        if connected_entity_type == "person":
            connection_type, connection_comment = person_relations.gnd_person_person_relation(connection_type_raw, person_new_sex, connection_type)
        elif connected_entity_type == "organisation":
            connection_type, connection_comment = person_relations.gnd_person_org_relation(connection_type_raw, person_new_sex, connection_type)
        elif connected_entity_type == "location":
            connection_type, connection_comment = person_relations.gnd_person_place_relation(connection_type_raw, person_new_sex, connection_type)
    elif main_entity_type == "organisation":
        if connected_entity_type == "person":
            connection_type, connection_comment = person_relations.gnd_org_person_relation(connection_type_raw, person_new_sex, connection_type)
        elif connected_entity_type == "organisation":
            connection_type, connection_comment = person_relations.gnd_org_org_relation(connection_type_raw, person_new_sex, connection_type)
        elif connected_entity_type == "location":
            connection_type, connection_comment = person_relations.gnd_org_place_relation(connection_type_raw, person_new_sex, connection_type)
    elif main_entity_type == "location":
        if connected_entity_type == "person":
            connection_type, connection_comment = person_relations.gnd_place_person_relation(connection_type_raw, person_new_sex, connection_type)
        elif connected_entity_type == "organisation":
            connection_type, connection_comment = person_relations.gnd_place_org_relation(connection_type_raw, person_new_sex, connection_type)
        elif connected_entity_type == "location":
            connection_type, connection_comment = person_relations.gnd_place_place_relation(connection_type_raw, person_new_sex, connection_type)
    return(connection_comment, connection_type)


@classes.func_logger
def convert_roman_numerals(roman_number):
    """This function translates a Roman numeral written according to rules 
     (permitting two "I", "X" or "C" left of a higher value) into Arabic numbers"""
    roman_number = roman_number.upper()
    roman_number = roman_number.replace(".", "")
    roman_number = roman_number.replace(" ", "")
    roman_number = roman_number.replace("J", "I")
    l = len(roman_number)
    print("length: " + str(l))
    result = 0
    for x in range(0, l):
        match roman_number[x]:
            case "M":
                result = result + 1000
            case "D":
                result = result + 500
            case "C":
                if l-x > 2: # if there are at least four characters following
                    if roman_number[x+1] == "M" or (roman_number[x+1] == "C" \
                        and roman_number[x+2] == "M"):
                        result = result - 100
                    elif roman_number[x+1] == "D" or (roman_number[x+1] == "C" \
                        and roman_number[x+2] == "D"):
                        result = result - 100
                    else:
                        result = result + 100
                elif l-x == 2: #if it is the penultima charachter
                    if roman_number[x+1] == "M" or roman_number[x+1] == "D":
                        result = result - 100
                    else:
                        result = result + 100
                else: #if it is the ultimate character
                    result = result + 100
            case "L":
                result = result + 50
            case "X":
                if l-x > 2: # if there are at least four characters following
                    if roman_number[x+1] == "C" or (roman_number[x+1] == "X" \
                            and roman_number[x+2] == "C"):
                        result = result - 10
                    elif roman_number[x+1] == "L" or (roman_number[x+1] == "X" \
                            and roman_number[x+2] == "L"):
                        result = result - 10
                    else:
                        result = result + 10
                elif l-x == 2: #if it is the penultima charachter
                    if roman_number[x+1] == "C" or roman_number[x+1] == "L":
                        result = result - 10
                    else:
                        result = result + 10
                else:
                    result = result + 10
            case "V":
                result = result + 5
            case "I":
                if l-x > 2: # if there are at least four characters following
                    if roman_number[x+1] == "X" or (roman_number[x+1] == "I" \
                        and roman_number[x+2] == "X"):
                        result = result - 1
                    elif roman_number[x+1] == "V" or (roman_number[x+1] == "I" \
                        and roman_number[x+2] == "V"):
                        result = result - 1
                    else:
                        result = result + 1
                elif l-x == 2: #if it is the penultima charachter
                    if roman_number[x+1] == "X" or roman_number[x+1] == "V":
                        result = result - 1
                    else:
                        result = result + 1
                else:
                    result = result + 1
    return str(result)

@classes.func_logger
def convert_english_ordinal_suffix(number):
    """
This function returns the suffix transforming an English number into an ordinal
    """
    if len(number) > 1 and number[-2] == "1": #it cannot be longer, but shorter
        abbreviation = "th"
    else:
        if number[-1] == "1":
            abbreviation = "st"
        elif number[-1] == "2":
            abbreviation = "nd"
        elif number[-1] == "3":
            abbreviation = "rd"
        else:
            abbreviation = "th"
    return abbreviation


#perhaps more signs will have to be added here later
# I also exclude "." - this is permitted in an URL, but the search dislikes it



#There is a problem - "Place of Making" could also go with "Region - historical" - I ignore that for the moment.
#from pymongo import MongoClient


encoding_list = {"Ö": "Ö", "ä": "ä", "ö": "ö", "ü": "ü", "é": "é"}
#class InvalidDateException(Exception):
#    pass

#class InvalidMonthException(Exception):
#    pass

#class InvalidDayException(Exception):
#    pass

#class InvalidDateStringException(Exception):
#    pass

#class InvalidDateRangeException(Exception):
#    pass




#from dbactions import *
url_replacement = {" " : "%20", "ä" : "%C3%A4", "ö" : "%C3%B6", "ü" : "%C3%BC", "Ä" : "%C3%84", "Ö" : "%C3%96", "Ü": "%C3%9C", \
                   "ß" : r"%C3%9F", "(" : "", ")" : "", "," : "",  "." : "" , "-" : "", \
                    "â": "%C3%A2", "ê" : "%C3%AA", "î" : "%C3%AE", "ô": "%C3%B4", "û" : "%C3%BB", "&" : "", \
                        "á" : "%C3%A1", "é" : "%C3%A9", "í" : "%C3%AD", "ó" : "%C3%B3", "ú": "%C3%BA", \
                        "à" : "%C3%A0", "è" : "%C3%A8", "ì": "%C3%AC", "ò" : "%C3%B2", "ù" : "%C3%B9", \
                        "Č" : "%C4%8C", "č" : "%C4%8D", "Ř": "%C5%98", "ř" : "%C5%99", "Š" : "%C5%A0", "š" : "%C5%A1"}

@classes.func_logger
def turn_umlaut_to_unicode(text):
    """
    Many texts from outside sources, most notably the GND, have a strange
    encoding that treats letters with umlaut or accents into two letters. 
    This module replaces them with the correct unicode character. 
    The list is still incomlete. 
    """
    encoding_list = {"Ö": "Ö", "Ü": "Ü", "ä": "ä", "ö": "ö", "ü": "ü", "é": "é", "ě" : "ě" }
    for old, new in encoding_list.items():
        text = text.replace(old, new)
    return text
    