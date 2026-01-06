#pylint: disable=C0114,C0116,W0622,
import pytest
#import pytest_asyncio
from dotenv import load_dotenv
from rich import print
from bpf.parsing import parse_istc
from bpf import classes
from bpf import db_actions
#from beanie import WriteRules

#import classes^^
#import db_actions

#import get_external_data

load_dotenv()

async def create_test_aesopus():
    """
    Create a test  record for an Aesopus
    GW ID has 3 digits
    One Author
    One Place, one printer, one date
    """
    id="ia00121400"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]


async def create_test_albrecht():
    """
    Create a test record for a decree of Albrecht IV
    GW ID for inserted material
    One Author
    Imprint in brackets (I think I ignore this
    One Place, one printer, date with 'not before')
    """
    id = "ia00352720"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]


async def create_test_abbreviamentum():
    """
    Create a test record for a abbreviamentum statutorum
    no Author
    One Place, two printers, date-range
    """
    id = "ia00003000"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]



async def create_test_wine():
    """
    Create a test record for a post-1500 book on wine
    GW ID for Non-Incunabula
    One Author
    Imprint with one place, one printer and one year in 
    square brackets with 'about'
    """
    id ="ia01082050"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]

async def create_test_gulden():
    """
    Creates a test record for a broadsheet on fake coins
    GW ID for not-yet-catalogued
    No author
    Imprint with one place, one printer and one year, 
    all in square brackets
    """
    id = "iz00019000"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]

async def create_test_accoltis():
    """
    Creates a test record
    One author
    Imprint with one place, one printer, one publisher, date by day
    """
    id = "ia00018500"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]

async def create_test_alanus_doctrinale():
    """
    Creates a test record
    One author
    Imprint with one place, two  printers, one publisher, date by day
    """
    id = "ia00178000"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]


async def create_test_alanus():
    """
    Creates a test record
    One author
    Imprint with one place, one printer, for himself and two other publishers, date simple day
    """
    id = "ia00224000"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]


async def create_test_causidicus():
    """
    Creates a test record
    One author
    Imprint with one place, one printer, a date range from a day to a month
    """
    id = "ia00209230"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]


async def create_record_alexis():
    """
    Creates a test record
    One author
    Two imprints, one town, printer and date, the other town n.pr., and date
    
    """
    id = "ia00458640"
    r=await parse_istc.get_istc_record_for_testing(id)
    return r[0]



@pytest.mark.asyncio
async def test_istc_get_bibliographic_id():
    """
    tests different types of GW IDs
    """
    # simple ID
    aesopus = await create_test_aesopus()
    print("record")
    print(aesopus)
    bid = parse_istc.istc_get_bibliographic_id(aesopus)
    assert bid[0][1] == "ISTC"
    assert bid[0][0] == "ia00121400"
    assert bid[0][2] == r'https://data.cerl.org/istc/ia00121400'
    assert bid[1][1] == "GW"
    assert bid[1][0] == "359"
    assert bid[1][2] == r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW00359.htm"

    # ID of an inserted record
    albrecht = await create_test_albrecht()
    bid = parse_istc.istc_get_bibliographic_id(albrecht)
    assert bid[0][1] == "ISTC"
    assert bid[0][0] == "ia00352720"
    assert bid[0][2] == r'https://data.cerl.org/istc/ia00352720'
    assert bid[1][1] == "GW"
    assert bid[1][0] == "0081020N"
    assert bid[1][2] == r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW0081020N.htm"

    # ID of an edition not regarded as incunable in the GW
    wine = await create_test_wine()
    bid = parse_istc.istc_get_bibliographic_id(wine)
    assert bid[0][1] == "ISTC"
    assert bid[0][0] == "ia01082050"
    assert bid[0][2] == r'https://data.cerl.org/istc/ia01082050'
    assert bid[1][1] == "GW"
    assert bid[1][0] == "II Sp.699a"
    assert bid[1][2] == r"https://www.gesamtkatalogderwiegendrucke.de/docs/GWII699A.htm"

    # ID of an edition not yet definitively catalogued in the GW
    gulden = await create_test_gulden()
    bid = parse_istc.istc_get_bibliographic_id(gulden)
    assert bid[0][1] == "ISTC"
    assert bid[0][0] == "iz00019000"
    assert bid[0][2] == r'https://data.cerl.org/istc/iz00019000'
    assert bid[1][1] == "GW"
    assert bid[1][0] == "M52066"
    assert bid[1][2] == r"https://www.gesamtkatalogderwiegendrucke.de/docs/M52066.htm"


@pytest.mark.asyncio
async def test_istc_analyse_prefix():
    """
    Tests the parsing of different prefixes of dates
    (which means both standardising expression and 
    adjusting start and end dates)
    """
    # option about
    date_prefix = "about "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "about "
    assert start_year == 1479
    assert end_year == 1481
    # option before
    date_prefix = "before "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "before "
    assert start_year == 1478
    assert end_year == 1480
    # option shortly before
    date_prefix = "shortly before "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "shortly before "
    assert start_year == 1479
    assert end_year == 1480
    # option not before
    date_prefix = "not before "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "not before "
    assert start_year == 1480
    assert end_year == 1482
# option after
    date_prefix = "after "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "after "
    assert start_year == 1480
    assert end_year == 1482
# option shortly after
    date_prefix = "shortly after "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "shortly after "
    assert start_year == 1480
    assert end_year == 1481
# option not after
    date_prefix = "not after "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "not after "
    assert start_year == 1478
    assert end_year == 1480
# unknown option
    date_prefix = "dsdfsdfsdfsadf "
    start_year = 1480
    end_year = 1480
    string_prefix, start_year, end_year = \
        parse_istc.analyse_prefix(date_prefix, start_year, end_year)
    assert string_prefix == "(unknown prefix - please check) "
    assert start_year == 1480
    assert end_year == 1480

@pytest.mark.asyncio
async def test_istc_analyse_year():
    """"
    Analyses the year in a date
    """
    # simple year
    date_prefix = ""
    date_year = "1480"
    date_year_to = ""
    date_year_between = ""
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == ""
    assert string_year == "1480"
    assert string_year_between == ""
    assert start_year == 1480
    assert end_year == 1480
    # year with prefix
    date_prefix= "About "
    date_year = "1480"
    date_year_to = ""
    date_year_between = ""
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == "about "
    assert string_year == "1480"
    assert string_year_between == ""
    assert start_year == 1479
    assert end_year == 1481

    # Between two dates of the same year
    date_prefix = "Between "
    date_year = ""
    date_year_to = ""
    date_year_between = "1480"
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == "between "
    assert string_year == ""
    assert string_year_between == "1480"
    assert start_year == 1480
    assert end_year == 1480

    # Between two dates in different years
    date_prefix = "Between "
    date_year = "1475"
    date_year_to = ""
    date_year_between = "1480"
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == "between "
    assert string_year == "1475"
    assert string_year_between == "1480"
    assert start_year == 1475
    assert end_year == 1480

    # Date with hyphen (both four digits)
    date_prefix = ""
    date_year = "1475"
    date_year_to = "-1480"
    date_year_between = ""
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == ""
    assert string_year == "1475-1480"
    assert string_year_between == ""
    assert start_year == 1475
    assert end_year == 1480

# Date with hyphen (second only two digits)
    date_prefix = ""
    date_year = "1475"
    date_year_to = "-80"
    date_year_between = ""
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == ""
    assert string_year == "1475-1480"
    assert string_year_between == ""
    assert start_year == 1475
    assert end_year == 1480

# Date with hyphen (second only two digits, with about
    date_prefix = "About "
    date_year = "1475"
    date_year_to = "-1480"
    date_year_between = ""
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == "about "
    assert string_year == "1475-1480"
    assert string_year_between == ""
    assert start_year == 1475
    assert end_year == 1480


    # Date with slash
    date_prefix = ""
    date_year = "1475"
    date_year_to = "/76"
    date_year_between = ""
    string_prefix, string_year, string_year_between, start_year, end_year = \
    parse_istc.analyse_year(date_prefix, date_year, date_year_to, date_year_between)
    assert string_prefix == ""
    assert string_year == "1475 (in modern calendar 1476)"
    assert string_year_between == ""
    assert start_year == 1476
    assert end_year == 1476


@pytest.mark.asyncio
async def test_istc_analyse_month():
    """
    Analyses the month in a date
    """
    # no months given
    date_between_year = ""
    date_between_month = ""
    date_month = ""
    string_month, string_month_between, start_month, end_month = \
        parse_istc.analyse_month(date_between_year, date_between_month, date_month)
    assert string_month == ""
    assert string_month_between == ""
    assert start_month == 1
    assert end_month == 12


    # only one date with a month given
    date_between_year = ""
    date_between_month = ""
    date_month = "Jan. "
    string_month, string_month_between, start_month, end_month = \
        parse_istc.analyse_month(date_between_year, date_between_month, date_month)
    assert string_month == "January "
    assert string_month_between == ""
    assert start_month == 1
    assert end_month == 1

    # two monts given
    date_between_year = ""
    date_between_month = "Sep. "
    date_month = "Jan. "
    string_month, string_month_between, start_month, end_month = \
        parse_istc.analyse_month(date_between_year, date_between_month, date_month)
    assert string_month == "January "
    assert string_month_between == "September "
    assert start_month == 1
    assert end_month == 9

    # two years given, no monthns
    # two monts given
    date_between_year = "1485"
    date_between_month = ""
    date_month = ""
    string_month, string_month_between, start_month, end_month = \
        parse_istc.analyse_month(date_between_year, date_between_month, date_month)
    assert string_month == ""
    assert string_month_between == ""
    assert start_month == 1
    assert end_month == 12


@pytest.mark.asyncio
async def test_istc_anaylyse_day():
    """
    Analyses the day in a date
    """
    # Just one day
    date_between_day = ""
    date_between_year = ""
    date_day = "17"
    end_month = 0
    end_year = 0
    string_day, string_day_between, start_day, end_day = \
        parse_istc.analyse_day(date_between_day, date_between_year, date_day, end_month, end_year)
    assert string_day == "17"
    assert string_day_between == ""
    assert start_day == 17
    assert end_day == 17
    # two days
    date_between_day = "29"
    date_between_year = ""
    date_day = "17"
    end_month = 0
    end_year = 0
    string_day, string_day_between, start_day, end_day = \
        parse_istc.analyse_day(date_between_day, date_between_year, date_day, end_month, end_year)
    assert string_day == "17"
    assert string_day_between == "29"
    assert start_day == 17
    assert end_day == 29

    # Month, no day
    date_between_day = ""
    date_between_year = ""
    date_day = ""
    end_month = 2
    end_year = 1496
    string_day, string_day_between, start_day, end_day = \
        parse_istc.analyse_day(date_between_day, date_between_year, date_day, end_month, end_year)
    assert string_day == ""
    assert string_day_between == ""
    assert start_day == 1
    assert end_day == 29


@pytest.mark.asyncio
async def test_istc_analyse_date():
    """
    Overall test of the date parsing function. 
    using real dates copies from ISTC
    """
    # simple year
    printing_date_raw = "1480"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "1480"
    assert date[1] == (1480,1,1)
    assert date[2] == (1480,12,31)
    # simple day
    printing_date_raw = "11 Aug. 1494"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "11 August 1494"
    assert date[1] == (1494,8,11)
    assert date[2] == (1494,8,11)
    # only year, with hyphen
    printing_date_raw = "1479-80"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "1479-1480"
    assert date[1] == (1479,1,1)
    assert date[2] == (1480,12,31)
    # only year, with prefix
    printing_date_raw = "about 1470"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "about 1470"
    assert date[1] == (1469,1,1)
    assert date[2] == (1471,12,31)
    # exact date, with prefix
    printing_date_raw = "not before 27 Aug. 1492"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "not before 27 August 1492"
    assert date[1] == (1492,8,27)
    assert date[2] == (1494,8,27)

    printing_date_raw = "Not after 27 Aug. 1492"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "not after 27 August 1492"
    assert date[1] == (1490,8,27)
    assert date[2] == (1492,8,27)

    # two dates, in this case the first day, the second only year
    printing_date_raw = "between 8 Feb. 1471 and 1472"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "between 8 February 1471 and 1472"
    assert date[1] == (1471,2,8)
    assert date[2] == (1472,12,31)
    # date with different year in modern calendar
    printing_date_raw = "14 Feb. 1494/95"
    date = parse_istc.istc_analyse_date(printing_date_raw)
    assert date[0] == "14 February 1494 (in modern calendar 1495)"
    assert date[1] == (1495,2,14)
    assert date[2] == (1495,2,14)

@pytest.mark.asyncio
async def test_istc_get_printer_name():
    """
    Tests extracting the printer's name(s)
    """
    # One printer
    await db_actions.initialise_beanie()
    printer_list = []
    printer_name_long = "Caspar Hochfeder"
    printer_list = parse_istc.istc_get_printer_name(printer_name_long)
    assert printer_list[0][0] == "person"
    assert printer_list[0][1] == "Caspar Hochfeder"
    #assert printer_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[0][2] == "printer"
    # two printers with different names
    printer_list = []
    printer_name_long = "John Lettou and William de Machlinia"
    printer_list = parse_istc.istc_get_printer_name(printer_name_long)
    assert printer_list[0][0] == "person"
    assert printer_list[0][1] == "John Lettou"
    assert printer_list[1][1] == "William de Machlinia"
    # two printers with the same surname
    printer_list = []
    printer_name_long = "Bernardinus and Ambrosius de Rovellis"
    printer_list = parse_istc.istc_get_printer_name(printer_name_long)
    assert printer_list[0][0] == "person"
    assert printer_list[1][0] == "person"
    assert printer_list[0][1] == "Bernardinus Rovellis"
    assert printer_list[1][1] == "Ambrosius de Rovellis"
    # Here, the expected result is not beautiful, the 'de' should appear
    # in both cases. However, (a) such situations are rare and (b), the
    # names inserted into the database will normally be names from the GND, anyway.
    # Hence, there is probably no need to create a rule that 'de', 'von' etc.
    # should stay with the surname.

@pytest.mark.asyncio
async def test_istc_get_publisher_name():
    """
    Tests extracting the publisher's name(s), if distinct from the printers'
    """
    await db_actions.initialise_beanie()
    # one publisher
    publisher_list = []
    publisher_name_long = "Andreas Torresanus"
    printer_name_long = " Simon de Luere"
    publisher_list = parse_istc.istc_get_publisher_name(publisher_name_long, printer_name_long)
    assert publisher_list[0][1]
    #assert publisher_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert publisher_list[0][2] == "publisher"
    # publishers with different names
    publisher_list = []
    publisher_name_long = "Antonius de Cistis and Henricus de Colonia"
    printer_name_long = "Ugo Rugerius"
    publisher_list = parse_istc.istc_get_publisher_name(publisher_name_long, printer_name_long)
    assert publisher_list[0][0] == "person"
    assert publisher_list[1][0] == "person"
    assert publisher_list[0][1] == "Antonius de Cistis"
    assert publisher_list[1][1] == "Henricus de Colonia"
    # publishers sharing surname
    publisher_list = []
    publisher_name_long = "Bastianus and Raphael de Orlandis"
    printer_name_long = "dfsadfdsfs fsfsdfd"
    publisher_list = parse_istc.istc_get_publisher_name(publisher_name_long, printer_name_long)
    assert publisher_list[0][1] == "Bastianus Orlandis"
    assert publisher_list[1][1] == "Raphael de Orlandis"
    # printer for himself and other publishers
    publisher_list = []
    publisher_name_long = "himself and Marcus Mazola and Antonius de Vignono"
    # in the original it has 'himself and for',
    # but the 'for' would be removed earlier on in the parsing.
    printer_name_long = "Paulus de Butzbach "
    publisher_list = parse_istc.istc_get_publisher_name(publisher_name_long, printer_name_long)
    assert publisher_list[0][1] == "Paulus de Butzbach"
    assert publisher_list[1][1] == "Marcus Mazola"
    assert publisher_list[2][1] == "Antonius de Vignono"


@pytest.mark.asyncio
async def test_istc_parse_imprint_0():
    """
    tests the function for parsing the whole imprint
    One place, one printer, one date
    """
    await db_actions.initialise_beanie()
    results = classes.Graph()
    bi = classes.Node()
    results.nodes.append(bi)
    aesopus = await create_test_aesopus()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(aesopus["imprint"][0])
    assert date_string == "23 May 1487"
    assert date_start == (1487, 5, 23)
    assert date_end == (1487, 5, 23)
    assert place_list[0][0] == "place"
    assert place_list[0][1] == "Augsburg"
    assert printer_list[0][0] == "person"
    assert printer_list[0][1] == "Johann Schobsser"
    assert printer_list[0][2] == "printer"
    assert not publisher_list

@pytest.mark.asyncio
async def test_istc_parse_imprint_1():
    """
    tests the function for parsing the whole imprint
    One place, one printer, one date (with a range)
    """
    await db_actions.initialise_beanie()
    albrecht = await create_test_albrecht()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(albrecht["imprint"][0])
    assert date_string == "not before 8 April 1485"
    assert date_start == (1485, 4, 8)
    assert date_end == (1487, 4, 8)
    assert place_list[0][1] == "Augsburg"
    assert printer_list[0][1] == "Johann Bämler"
    assert not publisher_list

@pytest.mark.asyncio
async def test_istc_parse_imprint_2():
    """
    tests the function for parsing the whole imprint
    One place, two printers, date-range
    """
    await db_actions.initialise_beanie()
    abbreviamentum = await create_test_abbreviamentum()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(abbreviamentum["imprint"][0])
    assert date_string == "about 1481-1482"
    assert date_start == (1481, 1, 1)
    assert date_end == (1482, 12, 31)
    assert place_list[0][0] == "place"
    assert place_list[0][1] == "London"
    #assert place_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[0][2] == "place of printing"
    assert printer_list[0][1] == "John Lettou"
    #assert printer_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[0][2] == "printer"
    assert printer_list[1][1] == "William de Machlinia"
    #assert printer_list[1].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[1][2] == "printer"
    assert not publisher_list


@pytest.mark.asyncio
async def test_istc_parse_imprint_3():
    """
    tests the function for parsing the whole imprint
    One place, one printer, one publisher, date-range
    """
    await db_actions.initialise_beanie()
    results = classes.Graph()
    bi = classes.Node()
    results.nodes.append(bi)
    accoltis = await create_test_accoltis()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(accoltis["imprint"][0])
    assert date_string == "11 August 1494"
    assert date_start == (1494, 8, 11)
    assert date_end == (1494, 8, 11)
    assert place_list[0][0] == "place"
    assert place_list[0][1] == "Pavia"
    #assert place_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[0][2] == "place of printing"
    assert place_list[1][1] == "Pavia"
    #assert place_list[1].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[1][2] == "place of publication"
    assert printer_list[0][1] == "Antonius de Carcano"
    #assert printer_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[0][2] == "printer"
    assert publisher_list[0][1] == "Gabriel de Grassis"
    #assert publisher_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert publisher_list[0][2] == "publisher"


@pytest.mark.asyncio
async def test_istc_parse_imprint_4():
    """
    tests the function for parsing the whole imprint
    One place, two printers, one publisher date by day"""
    await db_actions.initialise_beanie()
    alanus = await create_test_alanus_doctrinale()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(alanus["imprint"][0])
    assert date_string == "10 September 1500"
    assert date_start == (1500, 9, 10)
    assert date_end == (1500, 9, 10)
    assert place_list[0][0] == "place"
    assert place_list[0][1] == "Cologne"
    #assert place_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[0][2] == "place of printing"
    assert place_list[1][1] == "Cologne"
    #assert place_list[1].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[1][2] == "place of publication"
    assert printer_list[0][1] == "Heinrich Quentell"
    #assert printer_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[0][2] == "printer"
    assert printer_list[1][1] == "'Retro Minores'"
    #assert printer_list[1].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[1][2] == "printer"
    assert publisher_list[0][1] == "Heinrich Quentell"
    #assert publisher_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert publisher_list[0][2] == "publisher"

@pytest.mark.asyncio
async def test_istc_parse_imprint_5():
    """
    tests the function for parsing the whole imprint
    One place, one printer, for himself and two other publishers
    """
    await db_actions.initialise_beanie()
    alanus = await create_test_alanus()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(alanus["imprint"][0])
    assert date_string == "12 January 1479"
    assert date_start == (1479, 1, 12)
    assert date_end == (1479, 1, 12)
    assert place_list[0][0] == "place"
    assert place_list[0][1] == "Mantua"
    #assert place_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[0][2] == "place of printing"
    assert place_list[1][1] == "Mantua"
    #assert place_list[1].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[1][2] == "place of publication" == "place of publication"
    assert printer_list[0][1] == "Paulus de Butzbach"
    #assert printer_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[0][2] == "printer"
    assert publisher_list[0][1] == "Paulus de Butzbach"
    #assert publisher_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert publisher_list[0][2] == "publisher"
    assert publisher_list[1][1] == "Marcus Mazola"
    #assert publisher_list[1].get_attribute("chosen_candidate_id") == "-1"
    assert publisher_list[1][2] == "publisher"
    assert publisher_list[2][1] == "Antonius de Vignono"
    #assert publisher_list[2].get_attribute("chosen_candidate_id") == "-1"
    assert publisher_list[2][2] == "publisher"

@pytest.mark.asyncio
async def test_istc_parse_imprint_6():
    """
    tests the function for parsing the whole imprint
    One place, one printer, for himself and two other publishers
    """
    await db_actions.initialise_beanie()
    causidicus = await create_test_causidicus()
    place_list, date_string, date_start, date_end, printer_list, publisher_list = \
        parse_istc.parse_istc_imprint(causidicus["imprint"][0])
    assert date_string == "between October 1485 and 24 December 1485"
    assert date_start == (1485, 10, 1)
    assert date_end == (1485, 12, 24)
    assert place_list[0][0] == "place"
    assert place_list[0][1] == "Haarlem"
    #assert place_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert place_list[0][2] == "place of printing"
    assert printer_list[0][1] == "Jacob Bellaert"
    #assert printer_list[0].get_attribute("chosen_candidate_id") == "-1"
    assert printer_list[0][2] == "printer"
    assert len(publisher_list) == 0
    # It would be prettier if '1485 were not repeated in the string.
    # However, I regard the way the date has been written here as
    # incorrect, so it is probably not worth changing it.


@pytest.mark.asyncio
async def test_parse_istc_0():
    """
    Test or putting everything together. 
    More tests are probably not needed, since the different constellations in 
    imprint and ID have been tested before, and this is only about the title
    and the assembly of the parts. 
    
    """
    await db_actions.initialise_beanie()
    istc_number = "ia00121400"
    url = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + \
    istc_number + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format'\
        + r'facet=Holding%20country&facet=Publication%20country&'\
            + r'nofacets=true&mode=default&aggregations=true&style=full'
    results = await parse_istc.parse_istc(url)
    assert results.nodes[0].type == "BibliographicInformation"
    assert results.nodes[0].get_attribute("title") == \
        "Vita, after Rinucius, et Fabulae, Lib. I-IV, " \
        + "prose version of Romulus [German]. Add: Fabulae extravagantes. Fabulae novae " \
            +"(Tr: Rinucius). Fabulae Aviani. Fabulae collectae [German] (Tr: Heinrich Steinhöwel)"
    assert results.nodes[0].external_id[0].name == "ISTC"
    assert results.nodes[0].external_id[0].external_id == "ia00121400"
    assert results.nodes[0].external_id[0].uri == r'https://data.cerl.org/istc/ia00121400'
    assert results.nodes[0].external_id[1].name == "GW"
    assert results.nodes[0].external_id[1].external_id == "359"
    assert results.nodes[0].external_id[1].uri == \
        r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW00359.htm"
    assert results.nodes[0].dates[0].date_string == "23 May 1487"
    assert results.nodes[0].dates[0].date_start == (1487, 5, 23)
    assert results.nodes[0].dates[0].date_end == (1487, 5, 23)
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Aesopus"
    #assert results.nodes[1].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[2].type == "place"
    assert results.nodes[2].name_preferred == "Augsburg"
    #assert results.nodes[2].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[2].get_attribute("role") == "place of printing"
    assert results.nodes[3].type == "person"
    assert results.nodes[3].name_preferred == "Johann Schobsser"
    #assert results.nodes[3].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[3].get_attribute("role") == "printer"

@pytest.mark.asyncio
async def test_parse_istc_1():
    # This is a special case, it has two connected
    # GW numbers and two imprints
    await db_actions.initialise_beanie()
    istc_number = "ia00458640"
    url = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + \
    istc_number + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format'\
        + r'facet=Holding%20country&facet=Publication%20country&'\
            + r'nofacets=true&mode=default&aggregations=true&style=full'
    results = await parse_istc.parse_istc(url)
    assert results.nodes[0].type == "BibliographicInformation"
    assert results.nodes[0].get_attribute("title") == "Les faintises du monde"
    assert results.nodes[0].external_id[0].name == "ISTC"
    assert results.nodes[0].external_id[0].external_id == "ia00458640"
    assert results.nodes[0].external_id[0].uri == r'https://data.cerl.org/istc/ia00458640'
    assert results.nodes[0].external_id[1].name == "GW"
    assert results.nodes[0].external_id[1].external_id == "1242"
    assert results.nodes[0].external_id[1].uri == \
        r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW01242.htm"
    assert results.nodes[0].external_id[2].name == "GW"
    assert results.nodes[0].external_id[2].external_id == "1243"
    assert results.nodes[0].external_id[2].uri == \
        r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW01243.htm"
    assert results.nodes[0].dates[0].date_string == "about 1496"
    assert results.nodes[0].dates[0].date_start == (1495, 1, 1,)
    assert results.nodes[0].dates[0].date_end == (1497, 12, 31)
    assert results.nodes[0].dates[1].date_string == "about 1495"
    assert results.nodes[0].dates[1].date_start == (1494, 1, 1,)
    assert results.nodes[0].dates[1].date_end == (1496, 12, 31)

    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Alexis, Guilielmus"
    #assert results.nodes[1].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[2].type == "place"
    assert results.nodes[2].name_preferred == "Lyons"
    #assert results.nodes[2].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[2].get_attribute("role") == "place of printing"
    assert results.nodes[3].type == "person"
    assert results.nodes[3].name_preferred == "Martin Havard"
    #assert results.nodes[3].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[3].get_attribute("role") == "printer"
    assert results.nodes[4].type == "place"
    assert results.nodes[4].name_preferred == "Paris?"
    #assert results.nodes[4].get_attribute("chosen_candidate_id") == "-1"
    assert results.nodes[4].get_attribute("role") == "place of printing"
    # There is no printer connected to Paris, since
    # only "n.pr." (no printer) is given, hence
    # the parser ignores it.
