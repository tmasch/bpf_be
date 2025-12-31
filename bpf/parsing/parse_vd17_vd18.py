"""
This module has functions for parsing records of both VD17 and VD18
"""
import re
from lxml import etree

from bpf import classes
from bpf import get_external_data
from bpf.parsing import parsing_helpers
from bpf import db_actions

@classes.async_func_logger
async def get_vd17_record_for_testing(url_bibliography):
    """
    Downloads a record for testing purposes.
    """
    await db_actions.initialise_beanie()
    content = await get_external_data.get_web_data(url_bibliography)
    #content=await get_external_data.get_web_data_without_checking_webcall(url_bibliography)
    root = etree.XML(content)
    print("root of XML document")
    print(root)
    records=root.find("zs:records", namespaces=root.nsmap)
    return records



@classes.async_func_logger
async def parse_vd17(url_bibliography) -> classes.Graph:
    """
    This function can be used for parsing both the VD17 and the VD18
    """
    print("PARSE VD17")
    print(url_bibliography)
    results = classes.Graph()
    #bi = classes.BibliographicInformation()
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
            results = classes.Graph()
            bi = classes.Node()
            results.nodes.append(bi)
            #bi = classes.BibliographicInformation()
            results.nodes[0].type = "BibliographicInformation"
            results.nodes[0].external_id = vd17_get_id(record)
            author_list = vd17_get_author(record)
            if author_list:
                results.nodes.extend(author_list)
            #bi.title, bi.volume_number, bi.part_title = vd17_get_title(record) ## commented out
            title, volume_number, part_title = vd17_get_title(record)
            series_title, series_number = vd17_get_series(record)
            # I presume that there is either a series_title (so that the field for titlea, 245a, \
            # contains the part title, or a part_title, so that 245a contains the series title)
            edition = vd17_get_edition(record)
            if edition:
                if part_title:
                    part_title = part_title + ". " + edition
                else:
                    title = title + ". " + edition
            if series_title:
                results.nodes[0].set_attribute("title", series_title)
                results.nodes[0].set_attribute("volume_number", series_number)
                results.nodes[0].set_attribute("part_title", title)

            else:
                results.nodes[0].set_attribute("title", title)
                # question: should I set the following attributes always, or only if they not ""
                results.nodes[0].set_attribute("volume_number", volume_number)
                results.nodes[0].set_attribute("part_title", part_title)

            printing_date_raw = vd17_get_date_raw(record)
            if printing_date_raw:
                date = classes.Date()
                date.date_string, date.date_start, date.date_end = vd17_map_printing_date(
                printing_date_raw
                  )
                results.nodes[0].dates.append(date)
            #bi.printing_information = vd17_get_printing_information(record) ## commented out
            imprint = vd17_get_imprint(record)
            results.nodes[0].set_attribute("imprint", imprint)
            person_list = vd17_get_person(record)
            if person_list:
                for entry in person_list:
                    person = classes.Node()
                    person.name_preferred = entry[0]
                    person.set_attribute("role", entry[1])
                    person.external_id.append(entry[2])
                    results.nodes.append(person)

            org_list = vd17_get_org(record)
            if org_list:
                for entry in org_list:
                    org = classes.Node()
                    org.name_preferred = entry[0]
                    org.set_attribute("role", entry[1])
                    org.external_id.append(entry[2])
                    results.nodes.append(org)
            if not person_list and not org_list:
                # Sometimes, there is no proper entry for the printer,
                #but his name is mentioned in another place.
                person_list = vd17_get_printer_name(record)
                if person_list:
                    for entry in person_list:
                        person = classes.Node()
                        person.name_preferred = entry[0]
                        person.set_attribute("role", entry[1])
                        results.nodes.append(person)

            place_list = vd17_get_place(record)
            if place_list:
                for entry in place_list:
                    place = classes.Node()
                    place.name_preferred = entry[0]
                    place.set_attribute("role", entry[1])
                    if len(entry) == 3: # 3rd part is often missing
                        place.external_id.append(entry[2])
                    results.nodes.append(place)
        break
    return results


@classes.func_logger
def vd17_get_record_type(record):
    """
        Checks the 'Leader' of the record if it is the record for a monograph or a series - 
        in the latter case (pos. 19 = "a"), the record will be discarded. 

        """
    leader=record.findall("{*}recordData/{*}record/{*}leader")
    leader_text = leader[0].text
    record_type = leader_text[19]
    return record_type

@classes.func_logger
def vd17_get_id(record):
    """
    Gets the ID from VD17/VD18
    """
    bib_ids = []
    datafields = find_datafields(record, "024")
    for datafield in datafields:
        bib_id = classes.ExternalReference()
        subfields = find_subfields(datafield,"a")
        if subfields[0][0:4] == "VD18":
            bib_id.external_id = subfields[0][5:]
        else:
            bib_id.external_id = subfields[0]
        subfields = find_subfields(datafield, "2")
        bib_id.name = subfields[0]
        if bib_id.name == "vd17":
            bib_id.uri = (
                            r"https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27"
                            + bib_id.external_id
                            + "%27"
                        )
        elif bib_id.name == "vd18":
            bib_id.uri = (
                    r"https://vd18.k10plus.de/SET=2/TTL=1/CMD?ACT=SRCHA&IKT=8080&SRT=YOP&TRM=VD18"
                    + bib_id.external_id
                    + "&ADI_MAT=B"
            )
        print("bib_id that was found")
        print(bib_id)
        bib_ids.append(bib_id)
    return bib_ids

@classes.func_logger
def vd17_get_author(record):
    """
    Gets the primary author (from field MARC 100)                
    """
    author_list = [] # according to rules, there should only be one author in a 100 field
    # but I am not sure if this is always the case.
    datafields = find_datafields(record, "100")
    for datafield in datafields:
        person = classes.Node()
        person.type = "person"
        person.name_preferred = ""

        # I use this class here for any external ID; perhaps one should rename
        # it to ExternalID to make clear
        # that it is used for any indication of an ID in an external authority record.

        subfields = find_subfields(datafield, "a")
        if subfields:
            person.name_preferred = subfields[0]
            person.set_attribute("role", "author")
        subfields = find_subfields(datafield, "0")
        if subfields:

            if subfields[0][0:8] == "(DE-588)":
                pe_id = classes.ExternalReference()
                pe_id.external_id = subfields[0][8:]
                pe_id.name = "GND"
            # I could also fill id.url field, but I am not sure if it is needed since
            # the full record, including the URL, will be produced through parse_gnd anyway.
                person.external_id.append(pe_id)
            author_list.append(person)
        return author_list

@classes.func_logger
def vd17_get_title(record):

    """
     Gets title, volume number and part title
     (so for VD17 - I am not yet sure how this
     works for the VD18)
    """
    title = ""
    volume_number = ""
    part_title = ""
    datafields = find_datafields(record, "245")
    if datafields:
        subfields = find_subfields(datafields[0], "a")
        if subfields:
            title = subfields[0]
        subfields = find_subfields(datafields[0], "b") # = subtitle
        if subfields:
            title = title + " : " + subfields[0]
        subfields = find_subfields(datafields[0], "n")
        if subfields:
            volume_number =  subfields[0]
        subfields = find_subfields(datafields[0], "p")
        if subfields:
            part_title =  subfields[0]
    return title, volume_number, part_title

@classes.func_logger
def vd17_get_edition(record):
    """
    Takes references to new editions from field 250
    """
    edition = ""
    datafields = find_datafields(record, "250")
    if datafields:
        subfields = find_subfields(datafields[0], "a")
        if subfields:
            edition = subfields[0]
    return edition


@classes.func_logger
def vd17_get_series(record):
    """
    At least in the VD18, sometimes for multi-volume works
    field 245 contains not the main title but the part_title, 
    and the main title and the volume number are in subfields of
    field 490.
    I wonder if I should not 
    """
    series_title = ""
    series_number = ""
    datafields = find_datafields(record, "490")
    if datafields:
        subfields = find_subfields(datafields[0], "a")
        if subfields:
            series_title = subfields[0]
        subfields = find_subfields(datafields[0], "v")
        if subfields:
            series_number = subfields[0]
    return series_title, series_number




@classes.func_logger
def vd17_get_date_raw(record):
    """            
    gets the raw format for the printing date
    According to cursory tests, the following formats exist:
    there are: 1620, [1620], [ca. 1620], [ca. 1620-1621], 1619 [erschienen] 1620
    VD18 in Addition: Anno 1720, Anno MDCCXX, Im Jahr 1701

    However, the change of cataloguing standards from RAK to RDA may mean that there
    are in future transliterations rather than standardised forms, creating more
    challenges. It may also be possible to take the date from four digits in field 008,
    but I am not sure which pitfalls this would give. 
    """
    printing_date_raw = ""
    datafields = find_datafields(record, "264")
    if datafields:
        subfields = find_subfields(datafields[0], "c")
        if subfields:
            printing_date_raw = subfields[0]
    return printing_date_raw


@classes.func_logger
def vd17_get_imprint(record):
    """
    Copies one of the fields with number 500 for additional printing information
    (to be shown during the ingest process so that the editor can correct some 
    data)

    """
    printing_information_pattern = r"([^:]*)(: )(.*)"
    imprint = ""
    datafields = find_datafields(record, "500")
    for datafield in datafields:
        subfields = find_subfields(datafield, "a")
        if subfields:
            if "Vorlageform" in subfields[0]:
                printing_information_divided = re.match(
                                printing_information_pattern, subfields[0]
                            )
                imprint = printing_information_divided[3]
                            # I can do it in this simple way since, whilst there may be several
                            # '500' fields, only one will contain "Vorlageform"

    return imprint

@classes.func_logger
def vd17_get_person(record):
    """

    This function gets all names in the 700 fields, which means all names
    connected to the book apart from the principal author (who is in 100)
"""
    roles_list = {"aut" : "author", "rsp" : "respondent", "trl" : "translator", \
                  "edt" : "editor", "pbl" : "publisher", "prt" : "printer"}
    datafields = find_datafields(record, "700")
    person_list = []
    for datafield in datafields:
        name = ""
        role = ""
        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:
            if subfields[0][0:8] == "(DE-588)":
                pe_id = classes.ExternalReference()
                pe_id.external_id = subfields[0][8:]
                pe_id.name = "GND"
        subfields = find_subfields(datafield, "4")
        if subfields:
            if subfields[0] in roles_list:
                role = roles_list[subfields[0]]
                person = (name, role, pe_id)
                person_list.append(person)
    return person_list

def vd17_get_printer_name(record):
    """
    This function is only used if there are no 700 fields, i.e.
    if there is no proper record for the printer. 
    IN this case, the name of the printer from field 264 b can be used, but it has
    no GND ID and is hence far less pactical
    
    """
    datafields = find_datafields(record, "264")
    person_list = []
    for datafield in datafields:
        name = ""
        role = ""
        subfields = find_subfields(datafield, "b")
        if subfields:
            name = subfields[0]
            role = "printer"
            person = (name, role)
            person_list.append(person)
    return person_list


@classes.func_logger
def vd17_get_org(record):
    """
    This function gets all names and IDs from 710 fields,
    thus organisations functioning as authors, printers, etc.
    """
    orgs_list = []
    name = ""
    role = ""
    roles_list = {"aut" : "author", "rsp" : "respondent", "trl" : "translator", \
                  "edt" : "editor", "pbl" : "publisher", "prt" : "printer"}
    datafields = find_datafields(record, "710")
    for datafield in datafields:
        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:
            org_id = classes.ExternalReference()
            if subfields[0][0:8] == "(DE-588)":
                org_id.external_id = subfields[0][8:]
                org_id.name = "GND"
        subfields = find_subfields(datafield, "4")
        if subfields:
            if subfields[0] in roles_list:
                role = roles_list[subfields[0]]
                org = (name, role, org_id)
                orgs_list.append(org)
    return orgs_list

@classes.func_logger
def vd17_get_place(record):
    """                        
    Gets places (place or printing, place of publication, place of university
    from field 751, here often without external IDs)
    """
    places_list = []
    roles_list = {"pup" : "place of publication", "mfp" : "place of printing", \
                  "uvp" : "place of university"}
    name = ""
    role = ""
    place_id = ""
    datafields = find_datafields(record, "751")
    for datafield in datafields:
        subfields = find_subfields(datafield, "a")
        if subfields:
            name = subfields[0]
        subfields = find_subfields(datafield, "0")
        if subfields:
            if subfields[0][0:8] == "(DE-588)":
                place_id = classes.ExternalReference()
                place_id.external_id = subfields[0][8:]
                place_id.name = "GND"
        subfields = find_subfields(datafield, "4")
        if subfields:
            if subfields[0] in roles_list:
                role = roles_list[subfields[0]]
                if place_id: # is often not indicated.
                    place = (name, role, place_id)
                else:
                    place = (name, role)
                places_list.append(place)
    return places_list


@classes.func_logger
def vd17_map_printing_year_prefix (prefix, date_string, start_year, end_year):
    """
    This function examines the prefix of the printing date and 
    adjusts the date_string and the start_year and end_year 
    accordingly. 
    """
    print("Year in square brackets with Prefix")
    match prefix:
        case "erschienen ":
            pass
            # no changes needed
        case "ca. " | "ca." | "ca " | "circa " | "um " | "erschienen ca. ":
            date_string = "about " + date_string
            start_year = start_year - 2
            end_year = end_year + 2
        case "vor ":  # I include the year for 'before' in the string
            # since I am not sure if it always means 'before Jan 1st'
            date_string = "before " + date_string
            start_year = start_year - 5
        case "nach " | "erschienen nach ":  # cf. comment on "vor "
            date_string = "after " + date_string
            end_year = end_year + 5
        case "nicht vor ":
            date_string = "not before " + date_string
            end_year = end_year + 5
        case "nicht nach ":
            date_string = "not after " + date_string
            start_year = start_year - 5
        case "i.e. ":
            date_string = date_string + " (corrected date)"
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
    start_year = 0
    end_year = 0
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
def vd17_map_printing_date(printing_date_raw):
    """
    it does not work on the following construction (I do not know hnow common it is
    1630 [erschienen] 1632)
    """
    year_pattern_isolated = r"\d{4}"
    year_pattern_brackets = r"\[(ca. |ca.|ca |circa |um |vor |nicht vor \
        |nach |nicht nach |erschienen |erschienen ca. |erschienen|\
        |erschienen nach |i.e. )?(\d{4})?([MDCLXVI\.]*)?(\?|\? )?(/\d{2}|/\d{4})?\]"
    year_pattern_timespan_without_brackets = r"(\d{4})(-| - )(\d{4})"

    start_year = 0
    end_year = 0
    date_string = ""

    printing_date_raw = printing_date_raw.replace("[?]", "")
    printing_date_raw = printing_date_raw.replace('[MDC]', "MDC")
    printing_date_raw = printing_date_raw.replace('[MDCC]', "MDCC")

    if "[erschienen]" in printing_date_raw:
        # sometimes, there is e.g. "1602 [erschienen] 1612"
        # instead of "1602 [i.e. 1612]"
        printing_date_raw = "i.e. " + printing_date_raw.split("[erschienen]")[1]

    # otherwise, this create havoc with year_pattern_brackets
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
            if len(year_end_string) == 2:  # if there are only two digits
                year_end_string = "17" + year_end_string
            year_string = year_string + " / " + year_end_string
            date_string = year_string
            end_year = int(year_end_string)
        if printing_date_divided[0]: # if there is a prefix
            date_string, start_year, end_year = \
                vd17_map_printing_year_prefix(printing_date_divided[0], \
                    date_string, start_year, end_year)
        if printing_date_divided[3] == "?" or printing_date_divided[3] == "? ":
            date_string = date_string + "?"
    elif re.search(year_pattern_timespan_without_brackets, printing_date_raw):
        printing_date_divided = re.search(
            year_pattern_timespan_without_brackets, printing_date_raw
        ).groups()
        date_string = printing_date_divided[0]+"-"+printing_date_divided[2]
        start_year = int(printing_date_divided[0])
        end_year = int(printing_date_divided[2])


    else:  # This means that there the original datestring
        # from the book that will hopefully contain a legible date
        date_string, start_year, end_year = \
            vd17_map_printing_year_original_spelling(printing_date_raw)
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
