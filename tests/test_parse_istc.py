#pylint: disable=C0114,C0116,W0622,
import pytest
#import pytest_asyncio
from dotenv import load_dotenv
from rich import print
from bpf.parsing import parse_istc
#from beanie import WriteRules

#import classes
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



@pytest.mark.asyncio
async def test_istc_get_bibliographic_id():
    aesopus = await create_test_aesopus()
    print("record")
    print(aesopus)
    bid = parse_istc.istc_get_bibliographic_id(aesopus)
    assert bid[0].name == "ISTC"
    assert bid[0].external_id == "ia00121400"
    assert bid[0].uri == r'https://data.cerl.org/istc/ia00121400'
    assert bid[1].name == "GW"
    assert bid[1].external_id == "359"
    assert bid[1].uri == r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW00359.htm"

    albrecht = await create_test_albrecht()
    bid = parse_istc.istc_get_bibliographic_id(albrecht)
    assert bid[0].name == "ISTC"
    assert bid[0].external_id == "ia00352720"
    assert bid[0].uri == r'https://data.cerl.org/istc/ia00352720'
    assert bid[1].name == "GW"
    assert bid[1].external_id == "0081020N"
    assert bid[1].uri == r"https://www.gesamtkatalogderwiegendrucke.de/docs/GW0081020N.htm"

    wine = await create_test_wine()
    bid = parse_istc.istc_get_bibliographic_id(wine)
    assert bid[0].name == "ISTC"
    assert bid[0].external_id == "ia01082050"
    assert bid[0].uri == r'https://data.cerl.org/istc/ia01082050'
    assert bid[1].name == "GW"
    assert bid[1].external_id == "II Sp.699a"
    assert bid[1].uri == r"https://www.gesamtkatalogderwiegendrucke.de/docs/GWII699A.htm"

    gulden = await create_test_gulden()
    bid = parse_istc.istc_get_bibliographic_id(gulden)
    assert bid[0].name == "ISTC"
    assert bid[0].external_id == "iz00019000"
    assert bid[0].uri == r'https://data.cerl.org/istc/iz00019000'
    assert bid[1].name == "GW"
    assert bid[1].external_id == "M52066"
    assert bid[1].uri == r"https://www.gesamtkatalogderwiegendrucke.de/docs/M52066.htm"
    

@pytest.mark.asyncio
async def test_istc_analyse_prefix():
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
async def test_istc_analyse_moth():
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
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "1480"
    assert date_start == (1480,1,1)
    assert date_end == (1480,12,31)
    # simple day
    printing_date_raw = "11 Aug. 1494"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "11 August 1494"
    assert date_start == (1494,8,11)
    assert date_end == (1494,8,11)
    # only year, with hyphen
    printing_date_raw = "1479-80"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "1479-1480"
    assert date_start == (1479,1,1)
    assert date_end == (1480,12,31)
    # only year, with prefix
    printing_date_raw = "about 1470"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "about 1470"
    assert date_start == (1469,1,1)
    assert date_end == (1471,12,31)
    # exact date, with prefix
    printing_date_raw = "not before 27 Aug. 1492"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "not before 27 August 1492"
    assert date_start == (1492,8,27)
    assert date_end == (1494,8,27)

    printing_date_raw = "Not after 27 Aug. 1492"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "not after 27 August 1492"
    assert date_start == (1490,8,27)
    assert date_end == (1492,8,27)

    # two dates, in this case the first day, the second only year
    printing_date_raw = "between 8 Feb. 1471 and 1472"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "between 8 February 1471 and 1472"
    assert date_start == (1471,2,8)
    assert date_end == (1472,12,31)
    # date with different year in modern calendar
    printing_date_raw = "14 Feb. 1494/95"
    date_string, date_start, date_end = parse_istc.istc_analyse_date(printing_date_raw)
    assert date_string == "14 February 1494 (in modern calendar 1495)"
    assert date_start == (1495,2,14)
    assert date_end == (1495,2,14)

