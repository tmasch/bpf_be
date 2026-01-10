"""
This module contains functions for the Universal Short Title Catalogue
(USTC) records. 
They are only available as rather simply Dictionary elements embedded in a HTML file. 
Since they give less information than most other catalogues, they would only be used
if nothing else is available. 
Hence, a function checks for cross-references to (currently), ISTC, VD16, VD17, Edit16,
and takes records from these catalogues instead. 
"""
import json
from lxml import html


from bpf import classes
from bpf import get_external_data
from bpf import db_actions
from bpf.parsing import parse_istc
from bpf.parsing import parse_vd16
from bpf.parsing import parse_vd17_vd18
from bpf.parsing import parse_edit16
from bpf.parsing import parse_estc

@classes.async_func_logger
async def get_ustc_record_for_testing(url):
    """
    Parses a record of the USTC (in HTML)
    """
    await db_actions.initialise_beanie()
    content = await get_external_data.get_web_data(url)
    doc = html.fromstring(content)
    bib_str = doc.xpath("string(//div[@id='app']/@data-page)")
    bib_raw = json.loads(bib_str)
    bib = bib_raw["props"]["edition"]
    references = bib_raw["props"]["references"]
    return (bib, references)




@classes.async_func_logger
async def parse_ustc(url) -> classes.Graph:
    """
    Parses a record of the USTC (in HTML)
    """
    await db_actions.initialise_beanie()
    content = await get_external_data.get_web_data(url)
    doc = html.fromstring(content)
    record_raw_str = doc.xpath("string(//div[@id='app']/@data-page)")
    record_raw = json.loads(record_raw_str)
    record = record_raw["props"]["edition"]
    references = record_raw["props"]["references"]
    results = classes.Graph()
    bib = classes.Node()

    ustc_id_raw = ustc_get_ustc_id(record)
    ustc_id = classes.ExternalReference()
    ustc_id.name = "ustc"
    ustc_id.external_id = ustc_id_raw
    ustc_id.uri = r"https://ustc.ac.uk/editions/" + ustc_id_raw
    bib.external_id.append(ustc_id)

    external_id_list_raw = ustc_get_external_ids(references)
    for external_id_raw in external_id_list_raw:
        replacement_results = await ustc_use_better_source(external_id_raw)

        if replacement_results:
            replacement_results.nodes[0].external_id.append(ustc_id)
            # add ustc id
            return replacement_results
        external_id = classes.ExternalReference()
        external_id.external_id = external_id_raw[0]
        external_id.name = external_id_raw[1]
        external_id.uri = external_id_raw[2]
        bib.external_id.append(external_id)


    title = ustc_get_title(record)
    bib.set_attribute("title", title)
    imprint = ustc_get_imprint(record)
    bib.set_attribute("imprint", imprint)
    date_raw = ustc_get_date(record)
    if date_raw[0]:
        date = classes.Date()
        date.date_string = date_raw[0]
        date.date_start = date_raw[1]
        date.date_end = date_raw[2]
        bib.dates.append(date)

    results.nodes.append(bib)

    person_list = ustc_get_person(record)
    for person in person_list:
        pe = classes.Node()
        pe.type = "person"
        pe.name_preferred = person[0]
        pe.set_attribute("role", person[1])
        results.nodes.append(pe)
        # a problem: organisations are treated by this database like persons
        # once uthority files for printers are being searched, one needs
        # to be able to select 'organisations', not only 'persons'
    place = ustc_get_place(record)
    if place[0]:
        pl = classes.Node()
        pl.type = "place"
        pl.name_preferred = place[0]
        pl.set_attribute("role", place[1])
        results.nodes.append(pl)



    return results


@classes.func_logger
def ustc_get_ustc_id(record):
    """
    gets the USTC ID
    """
    ustc_id = record.get("sn", "")
    return ustc_id


@classes.func_logger
def ustc_get_external_ids(references):
    """
    gets any external IDs
    """
    id_list = []
    id_name_concordance = {"Incunabula Short Title Catalogue" :"ISTC", \
            "Verzeichnis der Drucke des 16. Jahrhunderts" : "vd16", \
            "Verzeichnis der Drucke des 17. Jahrhunderts" : "vd17", \
            "Censimento nazionale delle edizioni italiane del XVI secolo" : "edit16",
            "English Short Title Catalogue": "estc"}
    for reference in references:
        name = reference.get("title", "")
        external_id = reference.get("detail", "")
        uri = reference.get("link", "")
        name = id_name_concordance.get(name, name)
        id_list.append((external_id, name, uri))
    return id_list

@classes.async_func_logger
async def ustc_use_better_source(external_id):
    """
    If a USTC record has a reference to a bibliographical database
    with richer information (e.g., VD16), this database should be used

    """
    results = None
    if external_id[1] == "ISTC":

        url = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + \
        external_id[0] + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format'\
            + r'facet=Holding%20country&facet=Publication%20country&'\
                + r'nofacets=true&mode=default&aggregations=true&style=full'
        results = await parse_istc.parse_istc(url)
    elif external_id[1] == "vd16":
        results = await parse_vd16.parse_vd16(external_id[2])
    elif external_id[1] == "vd17":
        url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" \
            + external_id[0] + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
        results = await parse_vd17_vd18.parse_vd17(url)
    elif external_id[1] == "edit16":
        id_padded = "0" * (6-len(external_id[0])) + external_id[0]
        url = r"https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE" + id_padded
        results = await parse_edit16.parse_edit16(url)
    elif external_id[1]== "estc":
        url = r'https://datb.cerl.org/estc/' + external_id[0] + r'?_format=mrc'
        results = await parse_estc.parse_estc(url)
    return results


@classes.func_logger
def ustc_get_title(record):
    """
    gets the title
    """
    title = record.get("std_title", "")
    return title


@classes.func_logger
def ustc_get_imprint(record):
    """
    gets the imprint
    (which is in USTC sometimes a transcription as in the ESTC, 
    sometimes merely a list of standardised names of printers and places)
    """
    imprint = record.get("std_imprint", "")
    return imprint

@classes.func_logger
def ustc_get_date(record):
    """
    Gets the date. This appears to be normally just a four-digit number
    (even if days are given in the imprint)
    """
    date_string = record.get("year", "")
    date_start = ()
    date_end = ()
    if date_string:
        date_start = (int(date_string), 1, 1)
        date_end = (int(date_string), 12, 31)
    return date_string, date_start, date_end





@classes.func_logger
def ustc_get_person(record):
    """
    gets any persons (authors, printers) from the USTC
    NB: there is no distinction between printers and publishers
    There are 8 slots for authors and 4 for printers
    """
    person_list = []
    for n in range (1, 8):
        author_name = "author_name_" + str(n)
        person = record.get(author_name, "")

        author_role = "author_role_" + str(n)
        role = record.get(author_role, "")
        if person:
            if role == "":
                role = "author"
            elif role == "Principal Author":
                role = "author"
            elif role == "Additional Author":
                role = "author"
            person_list.append((person, role))
    for n in range (1,4):
        printer_name = "printer_name_" + str(n)
        person = record.get(printer_name, "")
        role = "printer"
        # there are no roles given to printers in this database
        if person:
            person_list.append((person, role))
    return person_list

@classes.func_logger
def ustc_get_place(record):
    """
    gets the place information
    (only one place)
    """
    role = ""
    place = record.get("place", "")
    if place:
        role = "place of printing"
    return place, role
