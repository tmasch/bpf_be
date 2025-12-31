"""Parses records from EDIT16, the Italien 
equivalent to the VD16 (in UNIMARC)"""

from pymarc import MARCReader
from bpf import get_external_data
from bpf import db_actions
from bpf import classes

@classes.async_func_logger
async def get_edit16_record_for_testing(url):
    """
    Gets a complete Edit16 Unimarc record for testing 
    indvidual functions
    """
    await db_actions.initialise_beanie()
    record = None
    content = await get_external_data.get_web_data(url)
    record_list = MARCReader(content)
    for item in record_list:
        record = item
        break
    return record

@classes.async_func_logger
async def parse_edit16(url):
    """
    Parses a record from edit16 (UNIMAARC), 
    callng up the get-functons for the 
    indivdual fields. 
    """
    await db_actions.initialise_beanie()
    content = await get_external_data.get_web_data(url)
    record_list = MARCReader(content)
    for item in record_list:
        record = item
        break
        # I make this construction since there is only one hit,
        # and [0] does not seem to work with iterators.
    results = classes.Graph()
    bi = classes.Node()
    bi.type = "BibliographicInformation"
    results.nodes.append(bi)
    id_raw = edit16_get_bibliographic_id(record)
    bib_id = classes.ExternalReference()
    bib_id.name = id_raw[0]
    bib_id.uri = id_raw[1]
    bib_id.external_id = id_raw[2]
    results.nodes[0].external_id.append(bib_id)

    title = edit16_get_title(record)
    results.nodes[0].set_attribute("title", title)

    imprint = edit16_get_imprint(record)
    if imprint:
        results.nodes[0].set_attribute("imprint", imprint)

    date_raw = edit16_get_date(record)
    if date_raw[0]:
        date = classes.Date()
        date.date_string = date_raw[0]
        date.date_start = date_raw[1]
        date.date_end = date_raw[2]
        results.nodes[0].dates.append(date)

    person_list = edit16_get_person(record)
    for person_raw in person_list:
        person = classes.Node()
        person.type = "person"
        person.name_preferred = person_raw[0]
        person.set_attribute("role", person_raw[1])
        person_id = classes.ExternalReference()
        person_id.name = "edit16"
        person_id.external_id = person_raw[2]
        person.external_id.append(person_id)
        for name_variant in person_raw[3]:
            person.set_attribute("name_variant", name_variant)
        for id_variant in person_raw[4]:
            person_id_variant = classes.ExternalReference()
            person_id_variant.name = "edit16"
            person_id_variant.external_id = id_variant
            person.external_id.append(person_id_variant)
        results.nodes.append(person)

    org_list = edit16_get_org(record)
    for org_raw in org_list:
        org = classes.Node()
        org.type = "organisation"
        org.name_preferred = org_raw[0]
        org.set_attribute("role", org_raw[1])
        org_id = classes.ExternalReference()
        org_id.name = "edit16"
        org_id.external_id = org_raw[2]
        org.external_id.append(org_id)
        for name_variant in org_raw[3]:
            org.set_attribute("name_variant", name_variant)
        for id_variant in org_raw[4]:
            org_id_variant = classes.ExternalReference()
            org_id_variant.name = "edit16"
            org_id_variant.external_id = id_variant
            org.external_id.append(org_id_variant)
        results.nodes.append(org)

    place_list = edit16_get_place(record)
    for place_name in place_list:
        place = classes.Node()
        place.type = "place"
        place.name_preferred = place_name
        place.set_attribute("role", "place of printing")
        results.nodes.append(place)
    return results

@classes.func_logger
def edit16_get_bibliographic_id(record):
    """
    Returns the EDIT ID and the URL of the record
    """
    id_fields = record.get_fields('003')
    uri = id_fields[0].data
    name = "edit16"
    external_id = uri[38:].lstrip("0")
    return name, uri, external_id

@classes.func_logger
def edit16_get_title(record):
    """Returns the title UNIMARC 200, subfield a"""
    title = record["200"]["a"]
    # It appears that Edit16 puts title, additions to title
    # and statement of responsibility (== MARC 245 subfield a, b + c)
    # all into subfield a, hence nothing more is needed
    #if ord(title[0]) == 8471:
    #    title = title[1:]
    title = title.replace(chr(8471), "")
    # Removing the marker for non-sorting articles at the start
    return title

@classes.func_logger
def edit16_get_imprint(record):
    """
    Returns the imprint in original spelling
    """
    place_of_publication = ""
    publisher = ""
    publishing_date = ""
    place_of_printing = ""
    printer = ""
    printing_date = ""
    i = record["210"]
    if "a" in i:
        place_of_publication = i["a"]
    if "c" in i:
        publisher = i["c"]
    if "d" in i:
        publishing_date = i["d"]
    if "e" in i:
        place_of_printing = i["e"]
    if "g" in i:
        printer = i["g"]
    if "h" in i:
        printing_date = i["h"]
    if place_of_publication and publisher:
        place_of_publication = place_of_publication + ": "
    if (place_of_publication or publisher) and publishing_date:
        publishing_date = ", " + publishing_date
    if place_of_printing and printer:
        place_of_printing = place_of_printing + ": "
    if (place_of_printing or printer) and printing_date:
        printing_date = ", " + printing_date
    if (place_of_publication or publisher or publishing_date) and \
        (place_of_printing or printer or printing_date):
        place_of_publication = "Published: " + place_of_publication
        place_of_printing = "; Printed: " + place_of_printing
    imprint = place_of_publication + publisher + publishing_date + \
        place_of_printing + printer + printing_date
    return imprint

@classes.func_logger
def edit16_get_date(record):
    """
    Returns the date
    (I take it from the Fingerprint since the date in 210
    often has the months and days in original spelling)
    """
    fingerprint = ""
    date_string = ""
    date_start = ""
    date_end = ""
    if "012" in record:
        if "a" in record["012"]:
            fingerprint = record["012"]["a"]
            date_string = fingerprint[24:28]
            date_start = (int(date_string), 1, 1)
            date_end = (int(date_string), 12, 31)
    elif "100" in record:
        if "a" in record["100"]:
            processing_data = record["100"]["a"]
            date_string = processing_data[9:13]
            date_start = (int(date_string), 1,1)
            date_end = (int(date_string), 12, 31)
    return date_string, date_start, date_end


@classes.func_logger
def edit16_get_person(record):
    """
    Returns the person records form the following fields
    700, 701, 702 (for authors - I am not sure if 701 or 702 are ever flled)
    712 (for printers - this is supposed to be an organisation field but it 
    seems to have been consistently used for printers.)
    Additional names and IDs for printers are added from fields 791
    """
    person_raw_list = []
    person_complete_list = []
    # field 700 (first author)
    for p in record.get_fields("700"):
        person_raw_result = edit16_get_person_name_and_id_out_of_subfields(p)
        for person_raw in person_raw_result:
            if person_raw[1] == "": #if no role is given for the person
                person_raw[1] = "author"
            person_raw_list.append(person_raw)
    # field 701 (additional authors - not sure if this is ever used)
    for p in record.get_fields("701"):
        person_raw_result = edit16_get_person_name_and_id_out_of_subfields(p)
        for person_raw in person_raw_result:
            if person_raw[1] == "": #if no role is given for the person
                person_raw[1] = "author"
            person_raw_list.append(person_raw)
    # field 702 (additional authors - is used sometimes)
    for p in record.get_fields("702"):
        person_raw_result = edit16_get_person_name_and_id_out_of_subfields(p)
        for person_raw in person_raw_result:
            if person_raw[1] == "": #if no role is given for the person
                person_raw[1] = "author"
            person_raw_list.append(person_raw)
    # field 712 (used - against the cataloguing rules - for publishers)
    for p in record.get_fields("712"):
        person_raw_result = edit16_get_person_name_and_id_out_of_subfields(p)
        for person_raw in person_raw_result:
            if person_raw[0] == "s.n.":
                continue
            if person_raw[1] == "": #if no role is given for the person
                person_raw[1] = "publisher"
            person_raw_list.append(person_raw)
    for person in person_raw_list:
        person_complete = edit16_add_variants_and_variant_ids(record, person)
        person_complete_list.append(person_complete)
    return person_complete_list

@classes.func_logger
def edit16_get_org(record):
    """
    returns organisations from fields 710 and 711
    (field 712 is used for publishers, not for organisations,
    and is parsed in edit16_get_person)
    """
    org_raw_list = []
    org_complete_list = []
    for o in record.get_fields("710"):
        org_raw_result = edit16_get_person_name_and_id_out_of_subfields(o)
        for org_raw in org_raw_result:
            if org_raw[1] == "": #if no role is given for the person
                org_raw[1] = "author"
            org_raw_list.append(org_raw)
    for o in record.get_fields("711"):
        org_raw_result = edit16_get_person_name_and_id_out_of_subfields(o)
        for org_raw in org_raw_result:
            if org_raw[1] == "": #if no role is given for the person
                org_raw[1] = "author"
            org_raw_list.append(org_raw)
    for org in org_raw_list:
        org_complete = edit16_add_variants_and_variant_ids(record, org)
        org_complete_list.append(org_complete)
    return org_complete_list


@classes.func_logger
def edit16_get_person_name_and_id_out_of_subfields(p):
    """
    Returns person_name (composed of several subfields)
    and id (divided from one subfield) from a person field
    Also used for orgs. 
    """
    person_name = ""
    person_role = ""
    person_id = ""
    person_raw_list = []
    roles_list = {"730" : "translator", \
                  "340" : "editor", "650" : "publisher", "610" : "printer"}

    if "a" in p:
        if " & " in p["a"]:
            person_name_divided = p["a"].split(" & ")
            if "4" in p:
                if p["4"] in roles_list:
                    person_role = roles_list[p["4"]]
            for person_name in person_name_divided:
                person_raw = [person_name, person_role, ""]
                person_raw_list.append(person_raw)
                # Two persons in a person record is probably only used for
                # publishers. It appears that they never used subfields b and c
                # The ID is an ID for both publishers together and not relevant here,
                # hence it is not copied.
        else:
            person_name = p["a"]
            if "b" in p:
                person_name = person_name + p["b"]
                # b is apparently impossible without a
            if "c" in p:
                c_list = p.get_subfields("c")
                for c in c_list:
                    person_name = person_name + c
                    # subfield c is repeated if there are
                    # both a title and a numeral, they
                    # have a format that allows direct
                    # concatenation without separators
            if "3" in p:
                person_id = p["3"]
            if "4" in p:
                if p["4"] in roles_list:
                    person_role = roles_list[p["4"]]
            person_raw = [person_name, person_role, person_id]
            person_raw_list.append(person_raw)
    return person_raw_list


@classes.func_logger
def edit16_add_variants_and_variant_ids(record, person_raw):
    """
    Adds the name variants and their IDs (no clue why the latter exist)
    to each person record
    """
    variant_name_list = []
    variant_id_list = []
    variant_list = record.get_fields("790")
    variant_list_2 = record.get_fields("791")
    variant_list.extend(variant_list_2)
    for variant_record in variant_list:
        if "z" in variant_record:
            if variant_record["z"].startswith(person_raw[0]):
                # I use this because subfield z of the variant sometimes has also dates.
                if "a" in variant_record:
                    variant_name_list.append(variant_record["a"])
                if "3" in variant_record:
                    variant_id_list.append(variant_record["3"])
    person_raw.append(variant_name_list)
    person_raw.append(variant_id_list)
    person_complete = person_raw
    return person_complete


@classes.func_logger
def edit16_get_place(record):
    """
    Returns the place name from field 620
    (deduplicating if necessary)
    """
    place_list = []
    for p in record.get_fields("620"):
        if "d" in p:
            place = p["d"]
            if place not in place_list and place != "s.l.":
                place_list.append(place)
    return place_list
