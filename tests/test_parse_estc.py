"""
This file contains tests for parse_estc,
the  module for parsing bibliographical
data from the ESTC (historical books from English-speaking countries)
"""

#pylint: disable=C0114,C0116,W0622,
import pytest


from dotenv import load_dotenv
#from rich import print
from bpf.parsing import parse_estc
#from bpf import classes
#from bpf import db_actions


load_dotenv()

async def create_test_paris():
    """
    has one additional ID
    """
    url = r"https://datb.cerl.org/estc/R216895?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record

async def create_test_master():
    """
    has no additional ID
    """
    url = "https://datb.cerl.org/estc/T87462?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record

async def create_test_processionale():
    """
    has imprint fully in square brackets
    """
    url = "https://datb.cerl.org/estc/S93709?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record


async def create_test_diurnale():
    """
    has printers and booksellers in 700 fields
    """
    url = "https://datb.cerl.org/estc/S124979?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record


async def create_test_solon():
    """
    has year in imprint with Prefix Anno Domini, not in sqare brackets
    """
    url = "https://datb.cerl.org/estc/S101151?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record

async def create_test_america():
    """
    has organisation as printer
    """
    url = "https://datb.cerl.org/estc/S122779?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record

async def create_test_assertio():
    """ 
    has an author with 100 subfields b and c
    """
    url = "https://datb.cerl.org/estc/S123359?_format=mrc"
    record = await parse_estc.get_estc_record_for_testing(url)
    return record


@pytest.mark.asyncio
async def test_estc_get_bibliographic_id():
    """
    Tests the function to get the main bibliographic information from field 001
    and additional bibliographic information from field 510
    """
    record = await create_test_paris()
    e_id = parse_estc.estc_get_bibliographic_id(record)
    assert e_id[0][0] == "R216895"
    assert e_id[0][1] == "estc"
    assert e_id[0][2] == "https://datb.cerl.org/estc/R216895"
    assert e_id[1][0] == "P358"
    assert e_id[1][1] == "Wing (CD-ROM, 1996)"

    record = await create_test_master()
    e_id = parse_estc.estc_get_bibliographic_id(record)
    assert e_id[0][0] == "T87462"
    assert e_id[0][1] == "estc"
    assert e_id[0][2] == "https://datb.cerl.org/estc/T87462"
    assert len(e_id) == 1

@pytest.mark.asyncio
async def test_estc_get_title():
    """
    Tests the function to get the complete title
    """
    record = await create_test_master()
    title = parse_estc.estc_get_title(record)
    assert title == "The history of the College of Corpus Christi and the B. Virgin Mary " \
        + "(commonly called Bene't) in the University of Cambridge, From its Foundation to the "\
        + "present Time. In Two Parts. I. Of its Founders, Benefactors and Masters. II. Of its "\
            "other principal Members. By Robert Masters, B. D. Fellow of the College, "\
                + "and of the Society of Antiquaries of London."

@pytest.mark.asyncio
async def test_estc_get_imprint():
    """
    Tests the function to get the full imprint as string
    """
    record = await create_test_paris()
    imprint_list, date_raw = parse_estc.estc_get_imprint(record)
    assert imprint_list[0] == "Londini : excudebat Richardus Hodgkinson [and Miles Flesher], " \
        + "1641. Sumptibus Cornelii Bee & Laurentii Sadler, in vico vulgaritèr dicto " \
            + "Little Britaine, [1641]"
    assert date_raw[0] == "[1641]"
    ###all in square brackets
    record = await create_test_processionale()
    imprint_list, date_raw = parse_estc.estc_get_imprint(record)
    assert imprint_list[0] == "[Rouen : s.n., ca. 1525]"
    assert date_raw[0] == "ca. 1525]"
    #### date not in square brackets
    record = await create_test_solon()
    imprint_list, date_raw = parse_estc.estc_get_imprint(record)
    assert date_raw[0] == "Anno Domini, 1594. "



def test_estc_analyse_date():
    """
    Tests the functions to get the date and to get a date in square brackets
    """
    date_raw = "[1641]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1641"
    assert date_start == (1641,1,1)
    assert date_end == (1641,12,31)
    date_raw = "ca. 1525]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "about 1525"
    assert date_start == (1523,1,1)
    assert date_end == (1527,12,31)
    date_raw = "anno Domini, 1594. "
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1594"
    assert date_start == (1594,1,1)
    assert date_end == (1594,12,31)
    date_raw = "MDCCXXXIII. [1733, i.e. 1734]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1734 (corrected date)"
    assert date_start == (1734,1,1)
    assert date_end == (1734,12,31)
    date_raw = "MDCCXXXIII. [1733, i.e., 1734]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1734 (corrected date)"
    assert date_start == (1734,1,1)
    assert date_end == (1734,12,31)
    date_raw = "MDCCXXXIII. [1733, i.e., 1734?]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1734 (corrected date - uncertain)"
    assert date_start == (1734,1,1)
    assert date_end == (1734,12,31)
    date_raw = "[between 1711 and 1769?]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "between 1711 and 1769 (uncertain)"
    assert date_start == (1711,1,1)
    assert date_end == (1769,12,31)
    date_raw = "1604 [i.e. ca. 1610?]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "about 1610 (corrected date)"
    assert date_start == (1608,1,1)
    assert date_end == (1612,12,31)
    date_raw = "[ca. 1520]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "about 1520"
    assert date_start == (1518,1,1)
    assert date_end == (1522,12,31)
    date_raw = "[1659?]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1659 (uncertain)"
    assert date_start == (1659,1,1)
    assert date_end == (1659,12,31)
    date_raw = "[1632-1635?]"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1632-1635 (uncertain)"
    assert date_start == (1632,1,1)
    assert date_end == (1635,12,31)
    date_raw = "1704-35"
    date_string, date_start, date_end = parse_estc.estc_analyse_date(date_raw)
    assert date_string == "1704-1735"
    assert date_start == (1704,1,1)
    assert date_end == (1735,12,31)

@pytest.mark.asyncio
async def test_estc_get_person():
    """
    Tests the function to get person information from fields 100 and 700
    """
    record = await create_test_paris()
    person_list = parse_estc.estc_get_person(record)
    assert person_list[0][0] == "Paris, Matthew"
    assert person_list[0][1] == "1200-1259"
    assert person_list[0][2] == "author"
    assert person_list[1][0] == "Watts, William"
    assert person_list[1][1] == "1590?-1649"
    assert person_list[1][2] == "editor"
    record = await create_test_diurnale()
    person_list = parse_estc.estc_get_person(record)
    assert person_list[0][0] == "Hopyl, Wolfgang"
    assert person_list[0][1] == "-1522"
    assert person_list[0][2] == "printer"
    assert person_list[1][0] == "Jacobi, Henry"
    assert person_list[1][1] == "-1514"
    assert person_list[1][2] == "publisher"
    assert person_list[2][0] == "Birckman, Franz"
    assert person_list[2][1] == "-1530"
    assert person_list[2][2] == "publisher"
    record = await create_test_assertio()
    person_list = parse_estc.estc_get_person(record)
    assert person_list[0][0] == "Henry VIII, King of England"
    assert person_list[0][1] == "1491-1547"
    assert person_list[0][2] == "author"
    assert person_list[1][0] == "Holbein, Hans"
    assert person_list[1][1] == "1497-1543"
    assert person_list[1][2] == "engraver"
    assert person_list[2][0] == "Pynson, Richard"
    assert person_list[2][1] == "-1530"
    assert person_list[2][2] == "printer"

@pytest.mark.asyncio
async def test_estc_get_org():
    """
    Tests the function to get organisation identification from fields 110 and 710
    """
    record = await create_test_america()
    org_list = parse_estc.estc_get_org(record)
    assert org_list[0][0] == "England and Wales. Sovereign (1625-1649 : Charles I)"
    assert org_list[0][1] == "author"
    assert org_list[1][0] == "Assigns of John Bill"
    assert org_list[1][1] == "printer"

@pytest.mark.asyncio
async def test_estc_get_place():
    """
    Tests the function to get place identification from field 752
    """
    record = await create_test_america()
    place_list = parse_estc.estc_get_place(record)
    assert place_list[0][0] == "London"
    assert place_list[0][1] == "place of publication"

@pytest.mark.asyncio
async def test_parse_estc_0():
    """
    Test of the full function. 
    This record has title wth subtitle, two bibliographical references,
    author, editor, and place

    """
    url = "https://datb.cerl.org/estc/R216895?_format=mrc"
    results = await parse_estc.parse_estc(url)
    bib = results.nodes[0]
    assert bib.type == "BibliographicInformation"
    assert bib.external_id[0].external_id == "R216895"
    assert bib.external_id[0].name == "estc"
    assert bib.external_id[1].name == "Wing (CD-ROM, 1996)"
    assert bib.external_id[1].external_id == "P358"
    assert bib.get_attribute("title").startswith("Matthæi Paris monachi Albanensis Angli, "\
            + "Historia major. Juxta exemplar Londinense")#
    assert bib.get_attribute("imprint") == "Londini : excudebat Richardus Hodgkinson " \
        + "[and Miles Flesher], 1641. Sumptibus Cornelii Bee & Laurentii Sadler, in vico "\
            + "vulgaritèr dicto Little Britaine, [1641]"
    assert bib.dates[0].date_string == "1641"
    assert bib.dates[0].date_start == (1641,1,1)
    assert bib.dates[0].date_end == (1641,12,31)
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Paris, Matthew"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[1].get_attribute("person_date") == "1200-1259"
    assert results.nodes[2].type == "person"
    assert results.nodes[2].name_preferred == "Watts, William"
    assert results.nodes[2].get_attribute("person_date") == "1590?-1649"
    assert results.nodes[2].get_attribute("role") == "editor"
    assert results.nodes[3].type == "place"
    assert results.nodes[3].name_preferred == "London"
    assert results.nodes[3].get_attribute("role") == "place of publication"

@pytest.mark.asyncio
async def test_parse_estc_1():
    """
    has an organisation as printer
    """
    url = "https://datb.cerl.org/estc/S122779?_format=mrc"
    results = await parse_estc.parse_estc(url)
    bib = results.nodes[0]
    assert bib.type == "BibliographicInformation"
    assert bib.get_attribute("title") == "By the King. A proclamation forbidding the disorderly "\
        + "trading with the saluages in New England in America, especially the furnishing of the "\
        + "natiues in those and other parts of America by the English with weapons, "\
            + "and habiliments of warre."
    assert bib.get_attribute("imprint") == "[Imprinted at London : by Robert Barker, printer to "\
        + "the Kings most excellent Maiestie: and by the assignes of Iohn Bill, 1630.]"
    assert bib.external_id[0].external_id == "S122779"
    assert bib.external_id[0].name == "estc"
    assert bib.external_id[1].name == "Steele, R. Tudor and Stuart proclamations"
    assert bib.external_id[1].external_id == "1627"
    assert bib.external_id[2].name == "STC (2nd ed.)"
    assert bib.external_id[2].external_id == "8969"
    assert bib.dates[0].date_string == "1630"
    assert bib.dates[0].date_start == (1630,1,1)
    assert bib.dates[0].date_end == (1630,12,31)
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Barker, Robert"
    assert results.nodes[1].get_attribute("person_date") == "-1645"
    assert results.nodes[1].get_attribute("role") == "printer"
    assert results.nodes[2].type == "organisation"
    assert results.nodes[2].name_preferred =="England and Wales. Sovereign (1625-1649 : Charles I)"
    assert results.nodes[2].get_attribute("role") == "author"
    assert results.nodes[3].type == "organisation"
    assert results.nodes[3].name_preferred == "Assigns of John Bill"
    assert results.nodes[3].get_attribute("role") == "printer"
    assert results.nodes[4].type == "place"
    assert results.nodes[4].name_preferred == "London"
    assert results.nodes[4].get_attribute("role") == "place of publication"
