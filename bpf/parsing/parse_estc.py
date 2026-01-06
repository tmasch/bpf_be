"""
For parsing records of the Electronic Short Title Catalogue
(historical books from English-speaking countries)
"""

import re
from pymarc import MARCReader
from bpf import get_external_data
from bpf import db_actions
from bpf import classes

@classes.async_func_logger
async def get_estc_record_for_testing(url):
    """
    Gets a complete ESTC MARC record for testing 
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
async def parse_estc(url) -> classes.Graph:
    """
    Parses a record from ESTC (MARC), 
    callng up the get-functons for the 
    indivdual fields. 
    It has one unusual element: person nodes can have 
    an additional attribute 'person_date' with the date
    as indicated as a string. It might be helpful to display
    it in the process of matching the entries with authority files, but
    it is not parsed in any way since the proper date would be taken
    from authority files. 
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
    # parsing bibliographic IDs
    bi.type = "BibliographicInformation"
    id_list = estc_get_bibliographic_id(record)
    for id_raw in id_list:
        external_id = classes.ExternalReference()
        external_id.external_id = id_raw[0]
        external_id.name = id_raw[1]
        if id_raw[2]:
            external_id.uri = id_raw[2]
        bi.external_id.append(external_id)
    title = estc_get_title(record)
    bi.set_attribute("title", title)
    imprint_list, date_raw_list = estc_get_imprint(record)
    for imprint in imprint_list:
        bi.set_attribute("imprint", imprint)
    for date_raw in date_raw_list:
        date_string, date_start, date_end = estc_analyse_date(date_raw)
        date = classes.Date()
        date.date_string = date_string
        date.date_start = date_start
        date.date_end = date_end
        bi.dates.append(date)
    results.nodes.append(bi)
    person_list = estc_get_person(record)
    for person in person_list:
        pe = classes.Node()
        pe.type = "person"
        pe.name_preferred = person[0]
        pe.set_attribute("person_date", person[1])
        pe.set_attribute("role", person[2])
        results.nodes.append(pe)
    org_list = estc_get_org(record)
    for org_raw in org_list:
        org = classes.Node()
        org.type = "organisation"
        org.name_preferred = org_raw[0]
        org.set_attribute("role", org_raw[1])
        results.nodes.append(org)
    place_list = estc_get_place(record)
    for place in place_list:
        pl = classes.Node()
        pl.type = "place"
        pl.name_preferred = place[0]
        pl.set_attribute("role", place[1])
        results.nodes.append(pl)


    return results



@classes.func_logger
def estc_get_bibliographic_id(record):
    """
    returns both the ESTC ID and IDs from other bibliographies
    """
    id_list = []
    id_fields = record.get_fields('001')
    external_id = id_fields[0].data
    id_name = "estc"
    uri = r'https://datb.cerl.org/estc/' + external_id
    bibliographic_id = (external_id, id_name, uri)
    id_list.append(bibliographic_id)
    additional_ids = record.get_fields('510')
    for additional_id in additional_ids:
        print("additional ID found")
        id_name = ""
        external_id = ""
        if "a" in additional_id:
            id_name = additional_id["a"]
            if id_name[-1] == ",":
                # is at least sometimes included
                id_name = id_name[0:-1]
        if "c" in additional_id:
            external_id = additional_id["c"]
            print("external_id found")
            print(external_id)
        bibliographic_id = (external_id, id_name, "")
        id_list.append(bibliographic_id)
    return id_list

@classes.func_logger
def estc_get_title(record):
    """
    Returns the title and subtitle (MARC 245 a + b)
    Apparently, the responsibility statement is here 
    never 245 c but always included in 245 b
    """
    if "245" in record:
        title = ""
        if "a" in record["245"]:
            title = record["245"]["a"]
        if "b" in record["245"]:
            title = title + " " + record["245"]["b"]
        title = title.rstrip(" ,")
    return title

@classes.func_logger
def estc_get_imprint(record):
    """
    Returns the imprint as a string
    Annoyingly, at least in many cases, 
    the ESTC does not contain any names of printers
    and publishers in standardised spelling. 
    Hence, when entering records, it will be necessary
    to manually supply them, based on the imprint. 
    """
    imprint_raw_list = record.get_fields("260")
    imprint_list = []
    date_raw_list = []
    for imprint_raw in imprint_raw_list:
        imprint = ""
        date_raw = ""
        if "a" in imprint_raw:
            imprint = imprint_raw["a"]
        if "b" in imprint_raw:
            if imprint_raw["b"] != "s.n.":
                imprint = imprint + " " + imprint_raw["b"]
        if "c" in imprint_raw:
            imprint = imprint + " " + imprint_raw["c"]
            date_raw = imprint_raw["c"]
        imprint = imprint.strip()
        imprint = imprint.replace("  ", " ")
        imprint_list.append(imprint)
        date_raw_list.append(date_raw)
        return imprint_list, date_raw_list

def estc_analyse_date(date_raw):
    """
    Returns the date both as a string and as tuples for the start and end. 
    If the dates are given in Roman numerals they are repeated in a relatively
    standardised format in square brackets that can easily be parsed - in other cases,
    they are rather irregular so that only some standard situations are parsed 
    (also owing to the fact that relatively few English books are currently available
    through IIIF). 
    Months and days are never parsed automatically. 
    """
    pattern_date_in_brackets = r'(\[.{3,}\])'
    pattern_date_outside_brackets = r'(\d{4})'
    date_brackets = ""
    date_string = ""
    date_start = ()
    date_end = ()
    if "[" in date_raw:
        date_raw_divided = re.search(pattern_date_in_brackets, date_raw).groups()
        if len(date_raw_divided) == 1:
            date_brackets = date_raw_divided[0]
            date_brackets = date_brackets[1:-1]
    elif "]" in date_raw: #only closing square brackets
        date_brackets = date_raw[0:-1]
    if date_brackets:
        date_string, date_start, date_end = estc_analyse_date_in_brackets(date_brackets)
    else:
        if "-" in date_raw:
            dash_pattern = r'(\d{4})(.*?)(\d{2,4})'
            date_divided = re.search(dash_pattern, date_raw)
            if date_divided:
                date_from = date_divided.groups()[0]
                date_to = date_divided.groups()[2]
                if len(date_to) < 4: # date_to misses the front digits
                    date_to = date_from[0:4-len(date_to)] + date_to
                date_string = date_from + "-" + date_to
                date_start = (int(date_from),1,1)
                date_end = (int(date_to),12,31)
        else:
            date_raw_divided = re.search(pattern_date_outside_brackets, date_raw).groups()
            if len(date_raw_divided) == 1:
                date_string = date_raw_divided[0]
                date_start = (int(date_string),1,1)
                date_end = (int(date_string),12,31)
    return date_string, date_start, date_end


@classes.func_logger
def estc_analyse_date_in_brackets(date_brackets):
    """
    If the date is in Roman numerals or somewhat problematic,
    the ESTC gives a date in brackets that would be preferably
    used for parsing. NB: it is probably less consistent than the 
    dates int he ISTC, hence the rather 'messy' search for different
    elements rather than one complex regular expression. 
    """
    date_string = ""
    date_start = ()
    date_end = ()
    if "i.e." in date_brackets:
        date_brackets = date_brackets.replace("i.e.,", "i.e.")
        id_est_pattern = r'(i\.e\. )(ca\. )?(\d{4})(\?)?'
        date_brackets_divided = re.search(id_est_pattern, date_brackets)
        if date_brackets_divided:
            date_raw = date_brackets_divided.groups()[2]
            date_start = (int(date_raw), 1, 1)
            date_end = (int(date_raw), 12, 31)
            if date_brackets_divided.groups()[1]:
                date_string = "about " + date_raw + " (corrected date)"
                # if there is both a "ca." before and a "?" after, the 'uncertain' is omitted
                date_start = (int(date_raw)-2, 1, 1)
                date_end = (int(date_raw)+ 2, 12, 31)
            elif date_brackets_divided.groups()[3]:
                date_string = date_raw + " (corrected date - uncertain)"
            else:
                date_string = date_raw + " (corrected date)"
    elif "between" in date_brackets:
        between_pattern = r'(\d{4})(.*?)(\d{4})(\??)'
        date_brackets_divided = re.search(between_pattern, date_brackets)
        if date_brackets_divided:
            date_from = date_brackets_divided.groups()[0]
            date_to = date_brackets_divided.groups()[2]
            date_string = "between " + date_from + " and " + date_to
            date_start = (int(date_from), 1, 1)
            date_end = (int(date_to), 12, 31)
            if date_brackets_divided.groups()[3]:
                date_string = date_string + " (uncertain)"
    elif "ca." in date_brackets:
        circa_pattern = r'(ca. )(\d{4})'
        date_brackets_divided = re.search(circa_pattern, date_brackets)
        if date_brackets_divided:
            date_raw = date_brackets_divided.groups()[1]
            date_string = "about " + date_raw
            date_start = (int(date_raw)-2, 1, 1)
            date_end = (int(date_raw)+2, 12, 31)
            # I ignore any question-marks because 'about' is uncertain enough
    elif "-" in date_brackets:
        dash_pattern = r'(\d{4})(.*?)(\d{4})(\?)?'
        date_brackets_divided = re.search(dash_pattern, date_brackets)
        if date_brackets_divided:
            date_from = date_brackets_divided.groups()[0]
            date_to = date_brackets_divided.groups()[2]
            date_string = date_from + "-" + date_to
            date_start = (int(date_from), 1, 1)
            date_end = (int(date_to), 12, 31)
            if date_brackets_divided.groups()[3]:
                date_string = date_string + " (uncertain)"
    elif "?" in date_brackets:
        # this means only records where the ? s the only additional sign.
        # combinations of other comments with the question-mark have been
        # treated above
        question_pattern = r'(\d{4})(\?)'
        date_brackets_divided = re.search(question_pattern, date_brackets)
        if date_brackets_divided:
            date_raw = date_brackets_divided.groups()[0]
            print("date_raw")
            print(date_raw)
            date_string = date_raw + " (uncertain)"
            date_start = (int(date_raw), 1, 1)
            date_end = (int(date_raw), 12, 31)
    else:
        pattern_minimal = r'(\d{4})'
        date_brackets_divided = re.search(pattern_minimal, date_brackets)
        if date_brackets_divided:
            date_string = date_brackets_divided.groups()[0]
            date_start = (int(date_string),1,1)
            date_end = (int(date_string), 12, 31)
    return date_string, date_start, date_end

@classes.func_logger
def estc_get_person(record):
    """
    Takes the person name and the relationship indicator 
    from fields MARC 100 (primary author) and MARC 700 (additional persons)
    Apparently, there are only names, no IDs
    NB: here, 'engraver' is indicated regularly - hence, I take this information
    - I'll have either to remove it, or find a way to put it into Artwork records
    """
    person_list = []
    roles_list = {"author" : "author",  "tr" : "translator", "trans" : "translator", \
                  "translator" : "translator", "ed" : "editor", "editor" : "editor", \
                    "bookseller" : "publisher", "publisher" : "publisher", "printer" : "printer",\
                          "egr" : "engraver", "engraver" : "engraver"}

    if "100" in record: # cannot be repeated
        pe_name = ""
        pe_dates = ""
        pe_role = ""
        if "a" in record["100"]:
            pe_name = record["100"]["a"]
            pe_name = pe_name.rstrip(",")
        if "b" in record["100"]:
            pe_name = pe_name + " " + record["100"]["b"]
        if "c" in record["100"]:
            pe_name = pe_name + " " + record["100"]["c"]
            pe_name = pe_name.rstrip(",")
        if "d" in record["100"]:
            pe_dates = record["100"]["d"].rstrip(" ,.")
        pe_role = "author"
        person_list.append((pe_name, pe_dates, pe_role))
    person_list_raw = record.get_fields("700")
    for person_raw in person_list_raw:
        pe_name = ""
        pe_dates = ""
        pe_role = ""
        if "a" in person_raw:
            pe_name = person_raw["a"]
            pe_name = pe_name.rstrip(",")
        if "b" in person_raw:
            pe_name = pe_name + " " + person_raw["b"]
        if "c" in person_raw:
            pe_name = pe_name + " " + person_raw["c"]
            pe_name = pe_name.rstrip(",")
        if "d" in person_raw:
            pe_dates = person_raw["d"].rstrip(" ,.")
        if "e" in person_raw and "t" not in person_raw:
            # fields with "t" do not refer to persons but to included texts
            role = person_raw["e"]
            role = role.rstrip(".")
            if role in roles_list:
                pe_role = roles_list[role]
                person_list.append((pe_name, pe_dates, pe_role))
    return person_list


@classes.func_logger
def estc_get_org(record):
    """
    Takes the organsiation name and the relationship indicator 
    from fields MARC 110 (primary organisation) and MARC 710 (additional organisation)
    Apparently, there are only names, no IDs
    """
    org_list = []
    roles_list = {"author" : "author",  "tr" : "translator", "trans" : "translator", \
                  "translator" : "translator", "ed" : "editor", "editor" : "editor", \
                    "bookseller" : "publisher", "publisher" : "publisher", "printer" : "printer",\
                          "egr" : "engraver", "engraver" : "engraver"}

    if "110" in record: # cannot be repeated
        org_name = ""
        if "a" in record["110"]:
            org_name = record["110"]["a"]
        if "b" in record["110"]:
            org_name = org_name + " " + record["110"]["b"]
        org_name = org_name.rstrip(",")
        org_role = "author"
        org_list.append((org_name, org_role))
    org_list_raw = record.get_fields("710")
    for org_raw in org_list_raw:
        if "a" in org_raw:
            org_name = org_raw["a"]
        if "b" in org_raw:
            org_name = org_name + " " + org_raw["b"]
        org_name = org_name.rstrip(",")

        if "e" in org_raw and "t" not in org_raw:
            # fields with "t" do not refer to persons but to included texts
            role = org_raw["e"]
            role = role.strip(".")
            if role in roles_list:
                org_role = roles_list[role]
                org_list.append((org_name, org_role))
    return org_list

@classes.func_logger
def estc_get_place(record):
    """
    parses the place-name in MARC 752 subfield d
    
    """
    place_list = []
    place_list_raw = record.get_fields("752")
    for place_raw in place_list_raw:
        if "d" in place_raw:
            place_name = place_raw["d"]
            place_name = place_name.rstrip(".")
            place_role = "place of publication"
            place_list.append((place_name, place_role))
    return place_list
