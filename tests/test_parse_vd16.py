#pylint: disable=C0114,C0116,W0622,
import pytest

#import pytest_asyncio
from dotenv import load_dotenv
from rich import print
from bpf.parsing import parse_vd16
#from bpf import classes
from bpf import db_actions

#from beanie import WriteRules

#import classes^^
#import db_actions

#import get_external_data

load_dotenv()

async def create_test_luther():
    """
    Creates test record for title with 1 author, 1 place
    one printer, one date
    """
    url = "https://gateway-bayern.de/VD16+L+7550"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    print("table in create_test_luther")
    print(len(table))
    return table

async def create_test_zeitung():
    """
    Creates test record for publication without author
    """
    url = "https://gateway-bayern.de/VD16+G+1923"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table


async def create_test_erasmus():
    """
    Creates test record for two printers in one 264b field
    """
    url = "https://gateway-bayern.de/VD16+E+3365"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table


async def create_test_pelbart():
    """
    Creates test record for two 264 fields
    """
    url = "https://gateway-bayern.de/VD16+ZV+24944"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table

async def create_test_reichstag():
    """
    Creates test record with organisation as author
    (field 110)
    """
    url = "https://gateway-bayern.de/VD16+R+796"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table

async def create_test_eidyllia():
    """
    Creates test record with two authors (in 100 and 700)
    """
    url = "https://gateway-bayern.de/VD16+ZV+30000"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table


async def create_test_poemata():
    """
    Creates test record with one author, one person and one
    organisation as printers
    """
    url = "https://gateway-bayern.de/VD16+ZV+33000"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table


async def create_test_carmen():
    """
    Creates test record with printing place in field MARC 751
    """
    url = "https://gateway-bayern.de/VD16+ZV+34000"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table


async def create_test_ordnung():
    """
    Creates test record with s.l. instead of a place
    """
    url = "https://gateway-bayern.de/VD16+ZV+34302"
    table = await parse_vd16.get_vd16_record_for_testing(url)
    return table


@pytest.mark.asyncio
async def test_vd16_get_id():
# first case: multiple IDs given
    table = await create_test_luther()
    bib_id = parse_vd16.vd16_get_id(table)
    assert bib_id.name == "vd16"
    assert bib_id.external_id == "L 7550"
    assert bib_id.uri == "https://gateway-bayern.de/VD16+L+7550"

@pytest.mark.asyncio
async def test_vd16_get_person():
    # one author
    table = await create_test_luther()
    name, role, id = parse_vd16.vd16_get_person(table)[0]
    assert name == "Luther, Martin"
    assert role == "author"
    assert id.name == "GND"
    assert id.external_id == "118575449"
    # no author
    table = await create_test_zeitung()
    author_list = parse_vd16.vd16_get_person(table)
    assert len(author_list) == 0
    # two authors
    table = await create_test_eidyllia()
    author_list = parse_vd16.vd16_get_person(table)
    assert author_list[0][0] == "Iteander, Samuel"
    assert author_list[0][1] == "author"
    assert author_list[0][2].name == "GND"
    assert author_list[0][2].external_id == "119719797"
    assert author_list[1][0] == "Olympius, Thomas"
    assert author_list[1][1] == "author"
    assert author_list[1][2].name == "GND"
    assert author_list[1][2].external_id == "119777800"
    # one author, one printer
    table = await create_test_poemata()
    person_list = parse_vd16.vd16_get_person(table)
    assert person_list[0][0] == "Finckelthusius, Laurentius"
    assert person_list[0][1] == "author"
    assert person_list[0][2].name == "GND"
    assert person_list[0][2].external_id == "119671751"
    assert person_list[1][0] == "Möllemann, Stephan"
    assert person_list[1][1] == "printer"
    assert person_list[1][2].name == "GND"
    assert person_list[1][2].external_id == "11976329X"


@pytest.mark.asyncio
async def test_vd16_get_org_as_author():
    """
    Tests function that gets organisations
    given as authors (MARC field 110)
    Here is no GND ID given - I did not find
    any example that includes such a reference
    """
    table = await create_test_reichstag()
    org_list = parse_vd16.vd16_get_org(table)
    assert org_list[0][0] == "Reichstag, Augsburg 1548"
    assert org_list[0][1] == "author"
    assert org_list[0][2] is None


@pytest.mark.asyncio
async def test_vde16_get_place():
    table = await create_test_carmen()
    place_list = parse_vd16.vd16_get_place(table)
    assert place_list[0][0] == "Wittenberg"
    assert place_list[0][1] == "place of printing"
    assert place_list[0][2].name == "GND"
    assert place_list[0][2].external_id == "4066640-2"


@pytest.mark.asyncio
async def test_vd16_get_title():
    table = await create_test_luther()
    title = parse_vd16.vd16_get_title(table)
    assert title == "Wie das Gesetze || vnd Euãgelion recht gr#[ue]nd||lich zuvnterscheiden "\
        + "sind.|| D.Mart.Luthers || predigt.|| Jtem/ was Christus vnd || sein K#[oe]nigreich "\
        + "sey/ Aus || dem Propheten Michea || Capit.v.geprediget.||"
    # probably no point to try out other titles

@pytest.mark.asyncio
async def test_vd16_get_imprint():
    # imprint present
    table = await create_test_luther()
    imprint = parse_vd16.vd16_get_imprint(table)
    assert imprint[0] == "Wittemberg M.D.xxxij.|| (Gedruckt ... || durch Hans Weis.|| )"


@pytest.mark.asyncio
async def test_vd16_parse_printing_date():
    date = parse_vd16.vd16_parse_printing_date("1510")
    assert date.date_string == "1510"
    assert date.date_start == (1510,1,1)
    assert date.date_end == (1510,12,31)
    date = parse_vd16.vd16_parse_printing_date("1510-1515")
    assert date.date_string == "1510-1515"
    assert date.date_start == (1510,1,1)
    assert date.date_end == (1515,12,31)
    date = parse_vd16.vd16_parse_printing_date("1510/1515")
    assert date.date_string == "1510-1515"
    assert date.date_start == (1510,1,1)
    assert date.date_end == (1515,12,31)
    date = parse_vd16.vd16_parse_printing_date("1510/11")
    assert date.date_string == "1510-1511"
    assert date.date_start == (1510,1,1)
    assert date.date_end == (1511,12,31)

@pytest.mark.asyncio
async def test_vd16_get_standardised_imprint():
    """
    Test for the function that gets the 
    standardised imprint consisting of 
    place, printer, and year
    """
    # field with one place, printer, year
    table = await create_test_luther()
    imprint = parse_vd16.vd16_get_imprint_standardised(table)
    assert imprint[0][0] == "Wittenberg"
    assert imprint[0][1] == "Weiß, Hans"
    assert imprint[0][2].date_string == "1532"
    assert imprint[0][2].date_start == (1532,1,1)
    assert imprint[0][2].date_end == (1532,12,31)
    # field with one place, two printers, one year
    table = await create_test_erasmus()
    imprint = parse_vd16.vd16_get_imprint_standardised(table)
    assert imprint[0][0] == "Basel"
    assert imprint[0][1] == "Froben, Hieronymus d.Ä."
    assert imprint[0][2].date_string == "1548"
    assert imprint[0][2].date_start == (1548,1,1)
    assert imprint[0][2].date_end == (1548,12,31)
    assert imprint[1][0] == ""
    assert imprint[1][1] == "Episcopius, Nik. d.Ä."
    assert imprint[1][2] == ""
    # two fields
    table = await create_test_pelbart()
    imprint = parse_vd16.vd16_get_imprint_standardised(table)
    assert imprint[0][0] == "Lyon"
    assert imprint[0][1] == "Sacon, Jacques"
    assert imprint[0][2].date_string == "1509"
    assert imprint[0][2].date_start == (1509,1,1)
    assert imprint[0][2].date_end == (1509,12,31)
    assert imprint[1][0] == "Nürnberg"
    assert imprint[1][1] == "Koberger, Anton d.Ä."
    assert imprint[1][2].date_string == "1509"
    assert imprint[1][2].date_start == (1509,1,1)
    assert imprint[1][2].date_end == (1509,12,31)

@pytest.mark.asyncio
async def test_parse_vd16_0():
    """
    Test for the overall function, using example
    with author, and place and printer only in the 
    short imprint - hence, the standard format. 
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+L+7550"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].type == "BibliographicInformation"
    assert results.nodes[0].get_attribute("title") == "Wie das Gesetze || vnd Euãgelion recht "\
        + "gr#[ue]nd||lich zuvnterscheiden sind.|| D.Mart.Luthers || predigt.|| Jtem/ was "\
        + "Christus vnd || sein K#[oe]nigreich sey/ Aus || dem Propheten Michea || "\
        + "Capit.v.geprediget.||"
    assert results.nodes[0].get_attribute("imprint") == "Wittemberg M.D.xxxij.|| "\
        + "(Gedruckt ... || durch Hans Weis.|| )"
    assert results.nodes[0].external_id[0].name == "vd16"
    assert results.nodes[0].external_id[0].external_id == "L 7550"
    assert results.nodes[0].external_id[0].uri == "https://gateway-bayern.de/VD16+L+7550"
    assert results.nodes[0].dates[0].date_string == "1532"
    assert results.nodes[0].dates[0].date_start == (1532,1,1)
    assert results.nodes[0].dates[0].date_end == (1532,12,31)
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Luther, Martin"
    assert results.nodes[1].external_id[0].name == "GND"
    assert results.nodes[1].external_id[0].external_id == "118575449"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[2].type == "place"
    assert results.nodes[2].name_preferred == "Wittenberg"
    assert results.nodes[2].get_attribute("role") == "place of printing"
    assert results.nodes[2].external_id == []
    assert results.nodes[3].type == "person"
    assert results.nodes[3].name_preferred == "Weiß, Hans"
    assert results.nodes[3].get_attribute("role") == "printer"


@pytest.mark.asyncio
async def test_parse_vd16_1():
    """
    tests text without author, with printer etc. in imprint
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+G+1923"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].external_id[0].external_id == "G 1923"
    assert results.nodes[1].type == "place"
    assert results.nodes[1].name_preferred == "Augsburg"
    assert results.nodes[2].type == "person"
    assert results.nodes[2].name_preferred == "Wörli, Josias"


@pytest.mark.asyncio
async def test_parse_vd16_2():
    """
    tests text with two printers in one 264 subfield b
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+E+3365"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].external_id[0].external_id == "E 3365"
    assert results.nodes[2].type == "place"
    assert results.nodes[2].name_preferred == "Basel"
    assert results.nodes[2].get_attribute("role") == "place of printing"
    assert results.nodes[3].type == "person"
    assert results.nodes[3].name_preferred == "Froben, Hieronymus d.Ä."
    assert results.nodes[3].get_attribute("role") == "printer"
    assert results.nodes[4].type == "person"
    assert results.nodes[4].name_preferred == "Episcopius, Nik. d.Ä."
    assert results.nodes[4].get_attribute("role") == "printer"


@pytest.mark.asyncio
async def test_parse_vd16_3():
    """
    tests texts with an organisation as primary author (field 110)
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+R+796"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].external_id[0].external_id == "R 796"
    assert results.nodes[1].type == "organisation"
    assert results.nodes[1].name_preferred == "Reichstag, Augsburg 1548"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[2].type == "place"
    assert results.nodes[2].name_preferred == "Mainz"
    assert results.nodes[2].get_attribute("role") == "place of printing"
    assert results.nodes[3].type == "person"
    assert results.nodes[3].name_preferred == "Schöffer, Ivo"
    assert results.nodes[3].get_attribute("role") == "printer"

@pytest.mark.asyncio
async def test_parse_vd16_4():
    """
    tests texts with two authors
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+ZV+30000"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].external_id[0].external_id == "ZV 30000"
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Iteander, Samuel"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[1].external_id[0].external_id == "119719797"
    assert results.nodes[2].type == "person"
    assert results.nodes[2].name_preferred == "Olympius, Thomas"
    assert results.nodes[2].external_id[0].external_id == "119777800"
    assert results.nodes[2].get_attribute("role") == "author"
    assert results.nodes[3].type == "place"
    assert results.nodes[3].name_preferred == "Wittenberg"
    assert results.nodes[3].get_attribute("role") == "place of printing"
    assert results.nodes[4].type == "person"
    assert results.nodes[4].name_preferred == "Gronenberg, Simon"
    assert results.nodes[4].get_attribute("role") == "printer"


@pytest.mark.asyncio
async def test_parse_vd16_5():
    """
    tests texts with one author, and both a person and an organisation
    as printers
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+ZV+33000"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].external_id[0].external_id == "ZV 33000"
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Finckelthusius, Laurentius"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[1].external_id[0].external_id == "119671751"
    assert results.nodes[2].type == "person"
    assert results.nodes[2].name_preferred == "Möllemann, Stephan"
    assert results.nodes[2].external_id[0].external_id == "11976329X"
    assert results.nodes[2].get_attribute("role") == "printer"
    assert results.nodes[3].type == "organisation"
    assert results.nodes[3].name_preferred == "Typographia Stephani Myliandri"
    assert results.nodes[3].get_attribute("role") == "printer"
    assert results.nodes[3].external_id[0].external_id == "1172902399"
    assert results.nodes[4].type == "place"
    assert results.nodes[4].name_preferred == "Rostock"
    assert results.nodes[4].get_attribute("role") == "place of printing"
    assert results.nodes[4].external_id[0].external_id == "4050610-1"
    assert len(results.nodes) == 5


@pytest.mark.asyncio
async def test_parse_vd16_6():
    """
    tests texts with s.l. in the imprint
    
    """
    await db_actions.initialise_beanie()
    url = "https://gateway-bayern.de/VD16+ZV+34302"
    results = await parse_vd16.parse_vd16(url)
    assert results.nodes[0].external_id[0].external_id == "ZV 34302"
    assert results.nodes[1].type == "person"
    assert results.nodes[2].type == "organisation"
    assert results.nodes[3].type == "organisation"
    assert len(results.nodes) == 4
    # this means that there is no record for the place.
