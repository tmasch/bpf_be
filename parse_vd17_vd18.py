"""
This module has functions for parsing records of both VD17 and VD18
"""
import re
from lxml import etree

import classes
import get_external_data
import parsing_helpers


@classes.func_logger
async def parse_vd17(url_bibliography):
    """
    This function can be used for parsing both the VD17 and the VD18
    """
    print("PARSE VD17")
    print(url_bibliography)
    bi = classes.BibliographicInformation()
    # url_bibliography = r"http://sru.k10plus.de/vd17?version=2.0\
    # &operation=searchRetrieve&query=pica.vds=" + \
    # bibliographic_id_number + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    content=await get_external_data.get_web_data(url_bibliography)
    root = etree.XML(content)
    print("root of XML document")
    print(root)
    records=root.find("zs:records", namespaces=root.nsmap)
    print(records)
    for record in records:
        record_type = vd17_get_record_type(record)
        if record_type != "a":
            bi = classes.BibliographicInformation()
            bi.bibliographic_id = vd17_get_id(record)
            author_list = vd17_get_author(record)
            if author_list:
                bi.persons.extend(author_list)
            #bi.title, bi.volume_number, bi.part_title = vd17_get_title(record) ## commented out
            bi.title = vd17_get_title(record)[0] ## added
            printing_date_raw = vd17_get_date_raw(record)
            if printing_date_raw:
                bi.date_string, bi.date_start, bi.date_end = map_printing_date(
                printing_date_raw
                  )
            #bi.printing_information = vd17_get_printing_information(record) ## commented out
            printer_list = vd17_get_printer(record)
            if printer_list:
                bi.persons.extend(printer_list)
            orgs_list = vd17_get_org(record)
            if orgs_list:
                bi.organisations = orgs_list
            bi.places = vd17_get_place(record)
    return bi
       

@classes.func_logger
def vd17_get_record_type(record):
    """
        Checks the 'Leader' of the record if it is the record for a monograph or a series - 
        in the latter case (pos. 19 = "a"), the record will be discarded. 

    if (
        "a4" in record[0].text
    ):  # The first part of the record is the so-called 'leader'.
        # It is here not constructed according to the usual rules.
        # However, it appears that it contains the signs "a4" only if it describes a series,
        # not an individual book. In this case, the record
        # is not to be used.
        # This needs to be changed!!
        return ""
        
        """
    leader=record.findall("{*}recordData/{*}record/{*}leader")
    leader_text = leader[0].text
    record_type = leader_text[19]
    return record_type

@classes.func_logger
def vd17_get_id(record):
    """
        for step1 in record:
            field = step1
            match field.get("tag"):
                case "024":  # for the VD17 number
                    bid = classes.BibliographicId()
                    for step2 in field:
                        match step2.get("code"):
                            case "a":
                                bid.id = step2.text
                                if bid.id[0:4] == "VD18":
                                    bid.id = bid.id[5:]
                            case "2":
                                bid.name = step2.text
                    if bid.name == "vd17":
                        bid.uri = (
                            r"https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27"
                            + bid.id
                            + "%27"
                        )
                        bi.bibliographic_id.append(
                            bid
                        )  # in the VD17, there is only one ID,
                        # this list is only introduced for the sake of consistence with incunables
                    #                        single_place = (place_name, place_id, place_role)

                    if bid.name == "vd18":
                        bid.uri = (
                            r"https://vd18.k10plus.de/SET=2/TTL=1/CMD?ACT=\
                            SRCHA&IKT=8080&SRT=YOP&TRM=VD18"
                            + bid.id
                            + "&ADI_MAT=B"
                        )

                        bi.bibliographic_id.append(
                            bid
                        )  # in the VD18, there is only one ID,
                        # this list is only introduced for the sake of consistence with incunables
                    #                        single_place = (place_name, place_id, place_role)
                    print("vorher: ")
                    print(bid.id)
                    print("gesamt: ")
                    print(bid)
    
    """
    datafields = find_datafields(record, "024")
    for datafield in datafields:
        bibliographic_id = []
        bid = classes.BibliographicId()
        subfields = find_subfields(datafield,"a")
        if subfields[0][0:4] == "VD18":
            bid.bib_id = subfields[0][5:]
        else:
            bid.bib_id = subfields[0]
        subfields = find_subfields(datafield, "2")
        bid.name = subfields[0]
        if bid.name == "vd17":
            bid.uri = (
                            r"https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27"
                            + bid.bib_id
                            + "%27"
                        )
        elif bid.name == "vd18":
            bid.uri = (
                            r"https://vd18.k10plus.de/SET=2/TTL=1/CMD?ACT=SRCHA&IKT=8080&SRT=YOP&TRM=VD18"
                            + bid.bib_id
                            + "&ADI_MAT=B"
            )
        bibliographic_id.append(bid)
    return bibliographic_id

@classes.func_logger
def vd17_get_author(record):
    """


                case "100":  # for the author
                    pe = classes.Entity()
                    for step2 in field:
                        match step2.get("code"):
                            case "a":
                                pe.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    pe.id = (step2.text)[8:]
                                    # here and elsewhere: to suppress the "(DE-588)"
                                    pe.id_name = "GND"
                    pe.role = "aut"
                    print(pe)
                    bi.persons.append(pe)
                #                    print("vorher:" + pe.name)
                #                    print("nachher: " + bi.persons)

                
    """
    author_list = [] # according to rules, there should only be one author in a 100 field
    # but I am not sure if this is always the case.
    datafields = find_datafields(record, "100")
    for datafield in datafields:
        name = ""

        # I use this class here for any external ID; perhaps one should rename it to ExternalID to make clear
        # that it is used for any indication of an ID in an external authority record. 

        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:

            if subfields[0][0:8] == "(DE-588)":
                id = classes.BibliographicId()
                id.bib_id = subfields[0][8:]
                id.name = "GND"
            # I could also fill id.url field, but I am not sure if it is needed since
            # the full record, including the URL, will be produced through parse_gnd anyway         
            role = "aut"
            author = classes.make_new_role(role=role,person_name=name)
            # This has to be changed to include the ID, but I won't do it
            # since make_new_role will be radiclaly changed because of the
            # change in the data structure
            author_list.append(author)
        return author_list

@classes.func_logger
def vd17_get_title(record):

    """
                case "245":  # for title and volume number
                    for step2 in field:
                        match step2.get("code"):
                            case "a":
                                bi.title = step2.text
                            case "n":
                                bi.volume_number = step2.text
                            case "p":
                                bi.part_title = step2.text

                
    """
    title, volume_number, part_title = "", "", ""
    datafields = find_datafields(record, "245")
    if datafields:
        subfields = find_subfields(datafields[0], "a")
        if subfields:
            title = subfields[0]
        subfields = find_subfields(datafields[0], "n")
        if subfields:
            volume_number = subfields[0]
        subfields = find_subfields(datafields[0], "p")
        if subfields:
            part_title = subfields[0]
    return title, volume_number, part_title

@classes.func_logger
def vd17_get_date_raw(record):
    """            
                case "264":  # for the date
                    for step2 in field:
                        match step2.get("code"):
                            case "c":
                                printing_date_raw = step2.text.strip()
    """
    printing_date_raw = ""
    datafields = find_datafields(record, "264")
    if datafields:
        subfields = find_subfields(datafields[0], "c")
        if subfields:
            printing_date_raw = subfields[0]
    return printing_date_raw


@classes.func_logger
def vd17_get_printing_information(record):
    """
              case "500":  # for the original statement of publication
                    # (in order to manually indicate who is printer and who is publisher)
                    for step2 in field:
                        if "Vorlageform" in step2.text:
                            printing_information_divided = re.match(
                                printing_information_pattern, step2.text
                            )
                            bi.printing_information = printing_information_divided[3]

    """
    printing_information_pattern = r"(.*)(: )(.*)"
    printing_information = ""
    datafields = find_datafields(record, "500")
    for datafield in datafields:
        subfields = find_subfields(datafield, "a")
        if subfields:
            if "Vorlageform" in subfields[0]:
                printing_information_divided = re.match(
                                printing_information_pattern, subfields[0]
                            )
                printing_information = printing_information + printing_information_divided[3]
                            # I can do it in this simple way since, whilst there may be several
                            # '500' fields, only one will contain "Vorlageform"

    return printing_information

@classes.func_logger
def vd17_get_printer(record):
    """

    This function gets all names in the 700 fields, which means all names
    connected to the book apart from the principal author (who is in 100)
                case "700":  # for printers and publishers
                    pe = classes.Entity()
                    for step2 in field:
                        match step2.get("code"):
                            case "a":
                                pe.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    pe.id = (step2.text)[8:]
                                    pe.id_name = "GND"
                                    # person_id_divided = re.match(gnd_pattern, field[step2].text)
                                    # person_id = person_id_divided[2]
                            case "4":
                                if step2.text == "prt":
                                    pe.role = "prt"
                                if step2.text == "pbl":
                                    pe.role = "pbl"
                                if step2.text == "rsp":
                                    pe.role = "rsp"
                                if step2.text == "aut":
                                    pe.role = "aut"
                    if pe.role != "":
                        #                        single_person
                        # = (person_name, person_id, person_role)
                        bi.persons.append(pe)
"""
    datafields = find_datafields(record, "700")
    for datafield in datafields:
        printer_list = []
        name = ""
        role = ""
        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:
            if subfields[0][0:8] == "(DE-588)":
                id = classes.BibliographicId()
                id.bib_id = subfields[0][8:]                        
                id.name = "GND"
        subfields = find_subfields(datafield, "4")
        if subfields:
            if subfields[0] in ["aut", "rsp", "trl", "edt", "pbl", "prt"]:
                role = subfields[0]
                person = classes.make_new_role(role=role,person_name=name)
                # This has to be changed to include the ID, but I won't do it
                # since make_new_role will be radically changed because of the
                # change in the data structure
                printer_list.append(person)
    return printer_list

@classes.func_logger
def vd17_get_org(record):
    """
                case "710":
                    org = classes.Entity()
                    for step2 in field:
                        match step2.get("code"):
                            case "a":
                                org.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    org.id = (step2.text)[8:]
                                    org.id_name = "GND"
                                    # person_id_divided = re.match(gnd_pattern, field[step2].text)
                                    # person_id = person_id_divided[2]
                            case "4":
                                if step2.text == "prt":
                                    org.role = "prt"
                                if step2.text == "pbl":
                                    org.role = "pbl"
                    if org.role != "":
                        #                        single_person =
                        # (person_name, person_id, person_role)
                        bi.organisations.append(org)
    """
    orgs_list = []
    name = ""
    role = ""
    datafields = find_datafields(record, "710")
    for datafield in datafields:
        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:
            id = classes.BibliographicId()
            if subfields[0][0:8] == "(DE-588)":
                id.bib_id = subfields[0][8:]
                id.name = "GND"
        subfields = find_subfields(datafield, "4")
        if subfields:
            if subfields[0] in ["aut", "rsp", "trl", "edt", "pbl", "prt"]:
                role = subfields[0]
                org = classes.make_new_role(role=role,person_name=name)
                # This has to be changed to include the ID, but I won't do it
                # since make_new_role will be radically changed because of the
                # change in the data structure.
                # Question: can this be used for organisations as well as for persons?
                # Or will this be possible with the planned successor for 'role'?
                # If not, one needs a different function here
                orgs_list.append(org)
    return orgs_list

@classes.func_logger
def vd17_get_place(record):
    """                        
                        
                case "751":  # for the places of printing and publishing
                    #                        place_id = ""
                    #                        place_role = ""
                    pl = classes.Entity()
                    for step2 in field:
                        match step2.get("code"):
                            case "a":
                                pl.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    pl.id = (step2.text)[8:]
                                    pl.id_name = "GND"
                            case "4":
                                if step2.text == "pup":
                                    pl.role = "pup"
                                elif step2.text == "mfp":
                                    pl.role = "mfp"
                                elif step2.text == "uvp":
                                    pl.role = "uvp"
                                    # I am not sure if I should not suppress 'uvp'????
"""
    places_list = []
    name = ""
    role = ""
    datafields = find_datafields(record, "751")
    for datafield in datafields:
        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:
            if subfields[0][0:8] == "(DE-588)":
                id = classes.BibliographicId()
                id.bib_id = subfields[0][8:]
                id.name = "GND"
        subfields = find_subfields(datafield, "4")
        if subfields:
            if subfields[0] in ["pup", "mfp", "uvp"]:
                role = subfields[0]
                place = classes.make_new_role(role=role,person_name=name)
                # This has to be changed to include the ID, but I won't do it
                # since make_new_role will be radically changed because of the
                # change in the data structure.
                # Question: can this be used for places as well as for persons?
                # Or will this be possible with the planned successor for 'role'?
                # If not, one needs a different function here
                places_list.append(place)
    return places_list
        

@classes.func_logger
def vd17_map_printing_year_prefix (prefix, year_string, start_year, end_year):
    """
    This function examines the prefix of the printing date and 
    adjusts the date_string and the start_year and end_year 
    accordingly. 
    """
    print("Year in square brackets with Prefix")
    match prefix:
        case "erschienen ":
            date_string = year_string
            start_year = int(year_string)
            end_year = int(year_string)
        case "ca. " | "ca." | "ca " | "circa " | "um " | "erschienen ca. ":
            date_string = "about " + year_string
            start_year = int(year_string) - 2
            end_year = int(year_string) + 2
        case "vor ":  # I include the year for 'before' in the string
            # since I am not sure if it always means 'before Jan 1st'
            date_string = "before " + year_string
            start_year = int(year_string) - 5
            end_year = int(year_string)
        case "nach " | "erschienen nach ":  # cf. comment on "vor "
            date_string = "after " + year_string
            start_year = int(year_string)
            end_year = int(year_string) + 5
        case "nicht vor ":
            date_string = "not before " + year_string
            start_year = int(year_string)
            end_year = int(year_string) + 5
        case "nicht nach ":
            date_string = "not after " + year_string
            start_year = int(year_string) - 5
            end_year = int(year_string)
        case "i.e. ":
            date_string = year_string + " (corrected date)"
            start_year = int(year_string)
            end_year = int(year_string)
    return (date_string, start_year, end_year)


@classes.func_logger
def vd17_map_printing_year_original_spelling(printing_date_raw):
    """
    This function is used if the printing date is given in the
    original spelling. 
    It tries to extract from it a year in Arabic or Roman
    numerals
    """
    year_string = ""
    start_year = ""
    end_year = ""
    year_pattern_arabic_in_text = r"(1\d{3})[\D$]?"
    # should mean 1XXX, then a non-number or end of string
    year_pattern_roman_in_text = r"(M[DCLXVI\. ]*)"

    printing_date_raw = printing_date_raw.replace("[", "")
    printing_date_raw = printing_date_raw.replace("]", "")
    # date_string = date_string.replace("M D", "MD")
    # date_string = date_string.replace("D C", "DC")

    if re.search(year_pattern_arabic_in_text, printing_date_raw):
        # This means that if there is a four-digit date
        # starting with '1' in the text and nothing in square brackets
        year_string = re.search(
            year_pattern_arabic_in_text, printing_date_raw
        ).groups()[0]
        print("four arabic digits found in text")
        date_string = year_string
        start_year = int(year_string)
        end_year = int(year_string)
    if re.search(year_pattern_roman_in_text, printing_date_raw):
        # This means that there is a string in Roman numerals starting with "M"
        year_string = parsing_helpers.convert_roman_numerals(
            re.search(year_pattern_roman_in_text, printing_date_raw).groups()[0]
        )
        date_string = year_string
        print("Year in Roman numerals:")
        print(date_string)
        start_year = int(year_string)
        end_year = int(year_string)
    elif "18. Jh." in printing_date_raw or "18.Jh." in printing_date_raw:
        date_string = "18th century"
        start_year = 1701
        end_year = 1800

    else:
        print("year not digested")
    return(date_string, start_year, end_year)


    

@classes.func_logger
def map_printing_date(printing_date_raw):
    """
    \todo
    """
    year_pattern_isolated = r"\d{4}"
    year_pattern_brackets = r"\[(ca. |ca.|ca |circa |um |vor |nicht vor \
        |nach |nicht nach |erschienen |erschienen ca. |erschienen|\
        |erschienen nach |i.e. )?(\d{4})?([MDCLXVI\.]*)?(\?|\? )?(/\d{2}|/\d{4})?\]"

    start_year = 1000
    end_year = 1000
    date_string = "1000"

    print("Rohdatum: ")
    print(printing_date_raw)
    if (
        re.match(year_pattern_isolated, printing_date_raw)
        and len(printing_date_raw) == 4
    ):
        # This means ca. 80% of the cases, when there is just a four-digit year
        print("Year simple number")
        date_string = printing_date_raw
        start_year = int(printing_date_raw)
        end_year = int(printing_date_raw)
    elif re.search(year_pattern_brackets, printing_date_raw):
        # If there is a date given in brackets, it should be the preferred form to use
        printing_date_divided = re.search(
            year_pattern_brackets, printing_date_raw
        ).groups()
        print("Year in square brackets matched")
        if printing_date_divided[1]:
            print("year string: " + printing_date_divided[1])
            year_string = printing_date_divided[1]
            date_string = year_string
            start_year = int(year_string)
            end_year = int(year_string)
        elif printing_date_divided[2]:
            year_string = parsing_helpers.convert_roman_numerals(
                printing_date_divided[2]
            )
            date_string = year_string
            start_year = int(year_string)
            end_year = int(year_string)
        if printing_date_divided[
            4
        ]:  # if there is a second year given as end of a period
            year_end_string = printing_date_divided[4][1:]
            print("Year_end_string found: ")
            print(year_end_string)
            if len(year_end_string) == 2:  # if there are only two digits
                year_end_string = "17" + year_end_string
            year_string = year_string + " / " + year_end_string
            date_string = year_string
            end_year = int(year_end_string)
        if printing_date_divided[0]:
            date_string, start_year, end_year = \
                vd17_map_printing_year_prefix(printing_date_divided[0], \
                    date_string, start_year, end_year)
        if printing_date_divided[3] == "?" or printing_date_divided[3] == "? ":
            date_string = date_string + "?"
    else:  # This means that there the original datestring
        # from the book that will hopefully contain a legible date
        date_string, start_year, end_year = vd17_map_printing_year_original_spelling(printing_date_raw)
    date_start = (start_year, 1, 1)
    date_end = (end_year, 12, 31)
    return date_string, date_start, date_end




def find_datafields(record,tag_id):
    """
    Returns a list of all datafields of a MARCXML Document with the same field number
    """
    datafields=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
    return datafields

def find_subfields(datafield,subfield_id):
    """
    Returns a list of all subfields of a datafield in a MARCXML 
    Document with the same subfield number
    """
    r=[]
    subfields=datafield.findall("{*}subfield")
    for subfield in subfields:
        key= subfield.get("code")
        value=subfield.text
        if key == subfield_id:
            r.append(value)
    return r
