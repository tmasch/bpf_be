"""
Functions for parsing records from the VD16
(in HTML format)
"""
import re
from lxml import html

from bpf import classes
from bpf import get_external_data
from bpf import db_actions

#url = "https://gateway-bayern.de/VD16+L+7550"

@classes.async_func_logger
async def get_vd16_record_for_testing(url):
    """
    Downloads the record and sends the relevant parcel back
    """
    await db_actions.initialise_beanie()
    content = await get_external_data.get_web_data(url)
#    content = await get_external_data.get_web_data_without_checking_webcall(url)
    doc = html.fromstring(content)
    #print("doc: ")
    #print(doc.text_content())
    table = doc.xpath("//table[@id='marcfields']/tbody")
    return table



@classes.async_func_logger
async def parse_vd16(url) -> classes.Graph:
    """
    Parses a record of the VD16 (in HTML)
    """
    content = await get_external_data.get_web_data(url)
    doc = html.fromstring(content)
    #print("doc: ")
    #print(doc.text_content())
    table = doc.xpath("//table[@id='marcfields']/tbody")
    #print("table: ")
    #print(table[0].text_content())
    results = classes.Graph()
    bi = classes.Node()
    results.nodes.append(bi)
    printer_in_700 = False
    # rarely, there is a detailed entry for the printer/publisher
    # in MARC 700. If so, this should be used, otherwise the
    # shorter entry in 264 subfield b.
    printing_place_in_751 = False
    # ditto for the place of printing
    results.nodes[0].type = "BibliographicInformation"
    title = vd16_get_title(table)
    results.nodes[0].set_attribute("title", title)

    bib_id = vd16_get_id(table)
    if bib_id:
        external_id = classes.ExternalReference()
        external_id.external_id = bib_id[0]
        external_id.name = bib_id[1]
        external_id.uri = bib_id[2]
        results.nodes[0].external_id.append(external_id)

    person_list = vd16_get_person(table)
    #print("going through person_list")
    for person_raw in person_list:
        person = classes.Node()
        person.type = person_raw[0]
        person.name_preferred = person_raw[1]
        if person_raw[2] in ["printer", "publisher"]:
            printer_in_700 = True
        person.set_attribute("role", person_raw[2])
        external_id = classes.ExternalReference()
        external_id.external_id = person_raw[3]
        external_id.name = person_raw[4]
        person.external_id.append(external_id)
    #    print(person)
        results.nodes.append(person)

    org_list = vd16_get_org(table)
    for org_raw in org_list:
        org = classes.Node()
        org.type = org_raw[0]
        org.name_preferred = org_raw[1]
        if org_raw[2] in ["printer", "publisher"]:
            printer_in_700 = True
        org.set_attribute("role", org_raw[2])
        external_id = classes.ExternalReference()
        external_id.external_id = org_raw[3]
        external_id.name = org_raw[4]
        org.external_id.append(external_id)
        results.nodes.append(org)

    place_list = vd16_get_place(table)
    #print("going through places_list")
    for place_raw in place_list:
        place = classes.Node()
        place.type = place_raw[0]
        place.name_preferred = place_raw[1]
        if place_raw[2] in ["place of printing", "place of publication"]:
            printing_place_in_751 = True
        place.set_attribute("role", place_raw[2])
        external_id = classes.ExternalReference()
        external_id.external_id = place_raw[3]
        external_id.name = place_raw[4]
        place.external_id.append(external_id)
    #    print(place)
        results.nodes.append(place)

    imprint_list = vd16_get_imprint(table)
    if imprint_list:
        for imprint in imprint_list:
            results.nodes[0].set_attribute("imprint", imprint)

    imprint_standardised_list = vd16_get_imprint_standardised(table)
    print("going through imprint_standardised")
    for imprint_standardised in imprint_standardised_list:
        if not printing_place_in_751:
            if imprint_standardised[0] and imprint_standardised[0] != "s.l.":
                print("adding place from imprint")
                place = classes.Node()
                place.type = "place"
                place.name_preferred = imprint_standardised[0]
                place.set_attribute("role", "place of printing")
                results.nodes.append(place)
        if not printer_in_700:
            if imprint_standardised[1]:
                print("adding printer from imprint")
                person = classes.Node()
                person.type = "person"
                person.name_preferred = imprint_standardised[1]
                person.set_attribute("role", "printer")
                results.nodes.append(person)
        if len(results.nodes[0].dates) == 0:
            date = classes.Date()
            date.date_string = imprint_standardised[2]
            date.date_start = imprint_standardised[3]
            date.date_end = imprint_standardised[4]
            results.nodes[0].dates.append(date)
    print(results)
    return results

@classes.func_logger
def vd16_get_id(table):
    """ 
    takes the first ID in field MARC 024
    """
    external_id = ""
    id_name = ""
    uri = ""
    id_pattern = r'(VD16 [A-Z]{1,2} \d{1,5})(\. Weitere .*)?'
    id_name = "vd16"
    id_list = vd16_turn_marc_field_into_dict(table, "024")
    id_dict = id_list[0] # id field not repetible
    if id_dict["|a"]:
        id_long = id_dict["|a"]
        id_divided = re.match(id_pattern, id_long)
        if id_divided:
            id_with_prefix = id_divided.groups()[0]
            external_id = id_with_prefix[5:]
            id_for_permalink = id_with_prefix.replace(" ", "+")
            uri = "https://gateway-bayern.de/" + id_for_permalink
    bib_id = (external_id, id_name, uri)
    return bib_id


@classes.func_logger
def vd16_get_person(table):
    """
    Takes information from field MARC 100 (primary author)
    and from field MARC 700 (additional persons)
    NB: MARC 700 normally has only additional authors or editors
    or contributors (the latter are being ignored here)
    """

    node_type = ""
    name = ""
    role_abbreviation = ""
    external_id = ""
    id_name = ""
    person_list = []
    person_record_list = []
    roles_list = {"aut" : "author", "rsp" : "respondent", "trl" : "translator", \
                  "edt" : "editor", "pbl" : "publisher", "prt" : "printer"}
    person_list = vd16_turn_marc_field_into_dict(table, "100")
    person_list_additional = vd16_turn_marc_field_into_dict(table, "700")
    person_list = person_list + person_list_additional
    for person in person_list:

        if "|a" in person:
            name = person["|a"]
            node_type = "person"
        if "|4" in person:
            role_abbreviation = person["|4"]
        if "|0" in person:
            author_id = person["|0"]
            if author_id[0:8] == "(DE-588)":
                author_id = author_id[8:]
                id_name = "GND"
                external_id = author_id
                # omitting code for GND
        if role_abbreviation in roles_list:
            role = roles_list[role_abbreviation]
            person_record = (node_type, name, role, external_id, id_name)
            person_record_list.append(person_record)
    print("list of person records: ")
    print(person_record_list)
    return person_record_list

@classes.func_logger
def vd16_get_org(table):
    """
    Takes information from field MARC 110
    This is only used for organisations as primary
    authors, hence primarily for official publications

    It also parses further organisations from field 710
    """

    node_type = ""
    name = ""
    role_abbreviation = ""
    external_id = ""
    id_name = ""
    org_list = []
    org_record_list = []
    roles_list = {"aut" : "author", "rsp" : "respondent", "trl" : "translator", \
                  "edt" : "editor", "pbl" : "publisher", "prt" : "printer"}
    org_list = vd16_turn_marc_field_into_dict(table, "110")
    org_list_additional = vd16_turn_marc_field_into_dict(table, "710")
    org_list = org_list + org_list_additional
    for org in org_list:
        if "|a" in org:
            name = org["|a"]
            node_type = "organisation"
        if "|4" in org:
            role_abbreviation = org["|4"]
        if "|0" in org:
            author_id = org["|0"]
            if author_id[0:8] == "(DE-588)":
                author_id = author_id[8:]
                id_name = "GND"
                external_id = author_id
                # omitting code for GND
        if role_abbreviation in roles_list:
            role = roles_list[role_abbreviation]
            org_record = (node_type, name, role, external_id, id_name)
            org_record_list.append(org_record)
    return org_record_list


@classes.func_logger
def vd16_get_place(table):
    """
    Takes information from field MARC 751
    This is only used very rare to indicate the place
    of manufacturing or of publication (normally, this
    is merely a string in field 264)
    """
    node_type = ""
    name = ""
    role_abbreviation = ""
    external_id = ""
    id_name = ""
    place_list = []
    place_record_list = []
    roles_list = {"mfp" : "place of printing", "pup" : "place of publication"}
    place_list = vd16_turn_marc_field_into_dict(table, "751")
    for place in place_list:
        if "|a" in place:
            name = place["|a"]
            node_type = "place"
        if "|4" in place:
            role_abbreviation = place["|4"]
        if "|0" in place:
            place_id_raw = place["|0"]
            if place_id_raw[0:8] == "(DE-588)":
                place_id_raw = place_id_raw[8:]
                id_name = "GND"
                external_id = place_id_raw
                # omitting code for GND
        if role_abbreviation in roles_list:
            role = roles_list[role_abbreviation]
            place_record = (node_type, name, role, external_id, id_name)
            place_record_list.append(place_record)
    print("list of place records: ")
    print(place_record_list)
    return place_record_list


@classes.func_logger
def vd16_get_title(table):
    """
    Takes information from field MARC 245 (title)
    """
    title = ""
    title_list = vd16_turn_marc_field_into_dict(table, "245")
    title_dict = title_list[0] # title field not repetible
    if "|a" in title_dict:
        title = title_dict["|a"]
    return title

@classes.func_logger
def vd16_get_imprint(table):
    """
    Takes information from MARC field 250 
    (imprint in original spelling)
    This is displayed to the editors of the 
    database so that they can select correct
    options, and it may be stored and displayed
    to users (not sure about that), but it would n
    not be analyse further
    """
    imprint_list = []
    imprint_list_raw = vd16_turn_marc_field_into_dict(table, "250")
    for imprint in imprint_list_raw:
        # I assume it is never repeated, but I am not sure
        imprint_dict = imprint
        if "|a" in imprint_dict:
            imprint = imprint_dict["|a"]
            imprint_list.append(imprint)
    return imprint_list

@classes.func_logger
def vd16_get_imprint_standardised(table):
    """
    Takes information from MARC field 264
    (imprint in standardised form)
    For most cases, all information about places 
    and printers is taken from here. 
    """
    imprint_list = []
    place = ""
    printer = ""
    printer_additional = ""
    date_raw = ""
    date_string = ""
    date_start = None
    date_end = None
    imprint_list_raw = vd16_turn_marc_field_into_dict(table, "264")
    for imprint in imprint_list_raw:
        # I assume it is never repeated, but I am not sure
        imprint_dict = imprint
        if "|a" in imprint_dict:
            place = imprint_dict["|a"]
        if "|b" in imprint_dict:
            printer = imprint_dict["|b"]
            if " und " in printer:
                printer_divided = printer.split(" und ")
                printer = printer_divided[0]
                printer_additional = printer_divided[1]
        if "|c" in imprint_dict:
            date_raw = imprint_dict["|c"]
            date_string, date_start, date_end = vd16_parse_printing_date(date_raw)
        imprint_standardised = (place, printer, date_string, date_start, date_end)
        imprint_list.append(imprint_standardised)
        if printer_additional:
            imprint_additional = ("", printer_additional, "")
            imprint_list.append(imprint_additional)
    return imprint_list


@classes.func_logger
def vd16_parse_printing_date(date_raw):
    """
    Fills in a date form with the date string 
    and start and end dates for searches. 
    Here, the date is normalyl just a year,
    sometimes "1505-1506" or "1505/1506". 
    I have not yet observed other forms, 
    but just in case this also caters for
    "1505/06"
    """
    date_raw = date_raw.replace("/", "-")
    if "-" in date_raw:
        date_divided = date_raw.split("-")
        year_start = date_divided[0]
        year_end = date_divided[1]
        if len(year_end) == 2:
            # this would be something like "1510/12"
            # I am not sure if this occurs anywhere.
            year_end = "15" + year_end
        date_string = year_start + "-" + year_end
        date_start = (int(year_start), 1, 1)
        date_end = (int(year_end), 12, 31)
    else:
        date_string = date_raw
        date_start = (int(date_raw), 1, 1)
        date_end = (int(date_raw), 12, 31)
    return date_string, date_start, date_end



@classes.func_logger
def vd16_turn_marc_field_into_dict(table, field_number):
    """
    Text the lines with the given field number out of the 
    table with MARC fields, and returns each line as a 
    dict, with the subfield headings (e.g. '|a' as keys
    and the field content as values)
    """
    fields_list = []
    xpath_term = r"tr[th/text()='" + field_number + r"']"
    marc_fields = table[0].xpath(xpath_term)
    for marc_field in marc_fields:
        field_no_header = marc_field.xpath("td")[2]
        field_dict = {}
        strongs = field_no_header.xpath(".//strong")
        for i,s in enumerate(strongs):
            key = s.text_content()
            next_strong = strongs[i+1] if i+1 < len(strongs) else None
            if next_strong is not None:
                content = field_no_header.\
                    xpath(".//text()[preceding::strong[1]=$s and following::strong[1]=$n]",
                s=s, n=next_strong)
            else:
                # last field: collect everything after this strong
                content = field_no_header.xpath(".//text()[preceding::strong[1]=$s]", s=s)
            if len(content) == 2:
                field_dict[key] = content[1].strip()
            else:
                field_dict[key] = content[0].strip()
        fields_list.append(field_dict)
    #print(fields_list)
    return fields_list
