"""
This file contains tests for parse_ustc,
the  module for parsing bibliographical
data from the USTC (a global catalogue from historical books,
with rather meagre information, hence to be used as last resort)
"""

#pylint: disable=C0114,C0116,W0622,
import pytest


from dotenv import load_dotenv
#from rich import print
from bpf.parsing import parse_ustc
#from bpf import classes
#from bpf import db_actions


load_dotenv()

async def create_test_svenska():
    """record of a book with a place and a printer but no authors"""
    url = "https://ustc.ac.uk/editions/300254"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record

async def create_test_chroniques():
    """ record of a book with several authors and printers"""
    url = "https://ustc.ac.uk/editions/43331"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record

async def create_test_summerhart():
    """
    record with ID from the VD16
    """
    url = "https://ustc.ac.uk/editions/644002"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record

async def create_test_christoph():
    # record from the ISTC
    url = "https://ustc.ac.uk/editions/743970"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record

async def create_test_ferdinand():
    # record from the VD17
    url = "https://ustc.ac.uk/editions/2704814"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record

async def create_test_lunario():
    # record from the EDIT16
    url = "https://ustc.ac.uk/editions/818885"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record

async def create_test_milton():
    # record from the estc
    url = "https://ustc.ac.uk/editions/3051625"
    record = await parse_ustc.get_ustc_record_for_testing(url)
    return record


@pytest.mark.asyncio
async def test_ustc_get_ustc_id():
    record = await create_test_svenska()
    ustc_id = parse_ustc.ustc_get_ustc_id(record[0])
    assert ustc_id == "300254"

@pytest.mark.asyncio
async def test_ustc_get_external_id():
    """tests parsing external IDs"""
    # for a book title
    record = await create_test_svenska()
    external_id_list = parse_ustc.ustc_get_external_ids(record[1])
    assert external_id_list[0][0] == "II, 106-107"
    assert external_id_list[0][1] == \
        "Isak Collijn, Sveriges bibliografi intill är 1600. I-III (Uppsala, 1927-31)"
    assert external_id_list[0][2] is None
    # for a title from the vd16
    record = await create_test_summerhart()
    external_id_list = parse_ustc.ustc_get_external_ids(record[1])
    assert external_id_list[0][0] == "S 10201"
    assert external_id_list[0][1] == "vd16"
    assert external_id_list[0][2] == "http://gateway-bayern.de/VD16+S+10201"
    # for a title from the ISTC
    record = await create_test_christoph()
    external_id_list = parse_ustc.ustc_get_external_ids(record[1])
    # [0] would be GW, but I don't use that.
    assert external_id_list[1][0] == "ic00473365"
    assert external_id_list[1][1] == "ISTC"
    # for a title in the VD17
    record = await create_test_ferdinand()
    external_id_list = parse_ustc.ustc_get_external_ids(record[1])
    assert external_id_list[0][0] == "12:659962D"
    assert external_id_list[0][1] == "vd17"
    # for a title in the Edit16
    record = await create_test_lunario()
    external_id_list = parse_ustc.ustc_get_external_ids(record[1])
    assert external_id_list[0][0] == "9493"
    assert external_id_list[0][1] == "edit16"


@pytest.mark.asyncio
async def test_get_title():
    record = await create_test_svenska()
    title = parse_ustc.ustc_get_title(record[0])
    assert title == "Svenska mässan"

@pytest.mark.asyncio
async def test_get_imprint():
    record = await create_test_svenska()
    imprint = parse_ustc.ustc_get_imprint(record[0])
    assert imprint == "Uppsala, [Jürgen Richolff], 1541"

@pytest.mark.asyncio
async def test_get_date():
    record = await create_test_svenska()
    date = parse_ustc.ustc_get_date(record[0])
    assert date[0] == "1541"
    assert date[1] == (1541,1,1)
    assert date[2] == (1541,12,31)

@pytest.mark.asyncio
async def test_get_person():
    record = await create_test_svenska()
    person_list = parse_ustc.ustc_get_person(record[0])
    assert person_list[0][0] == "Richolff, Jürgen"
    assert person_list[0][1] == "printer"
    record = await create_test_chroniques()
    person_list = parse_ustc.ustc_get_person(record[0])
    assert person_list[0][0] == "Gilles, Nicole"
    assert person_list[0][1] == "author"
    assert person_list[1][0] == "Sauvage, Denis"
    assert person_list[1][1] == "author"
    assert person_list[4][0] == "Chaudière, Guillaume"
    assert person_list[4][1] == "printer"
    assert person_list[5][0] == "Binet, Denis"
    assert person_list[5][1] == "printer"

@pytest.mark.asyncio
async def test_get_place():
    record = await create_test_svenska()
    place = parse_ustc.ustc_get_place(record[0])
    assert place[0] == "Uppsala"
    assert place[1] == "place of printing"

@pytest.mark.asyncio
async def test_parse_ustc_0():
    # parsing of a USTC record without author
    url = "https://ustc.ac.uk/editions/300254"
    results = await parse_ustc.parse_ustc(url)
    bib = results.nodes[0]
    assert bib.get_attribute("title") == "Svenska mässan"
    assert bib.get_attribute("imprint") == "Uppsala, [Jürgen Richolff], 1541"
    assert bib.external_id[0].external_id == "300254"
    assert bib.external_id[0].name == "ustc"
    assert bib.external_id[0].uri == "https://ustc.ac.uk/editions/300254"
    assert bib.external_id[1].external_id == "II, 106-107"
    assert bib.external_id[1].name == \
        "Isak Collijn, Sveriges bibliografi intill är 1600. I-III (Uppsala, 1927-31)"
    assert bib.external_id[1].uri is None
    assert bib.dates[0].date_string == "1541"
    assert bib.dates[0].date_start== (1541,1,1)
    assert bib.dates[0].date_end == (1541,12,31)
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Richolff, Jürgen"
    assert results.nodes[1].get_attribute("role") == "printer"
    print(results.nodes[2])
    assert results.nodes[2].type == "place"
    assert results.nodes[2].name_preferred == "Uppsala"
    assert results.nodes[2].get_attribute("role") == "place of printing"

@pytest.mark.asyncio
async def test_parse_ustc_1():
    """
    record with several authors and printers
    """
    url = "https://ustc.ac.uk/editions/43331"
    results = await parse_ustc.parse_ustc(url)
    assert results.nodes[0].external_id[0].name == "ustc"
    assert results.nodes[0].external_id[0].external_id == "43331"
    assert results.nodes[0].external_id[0].uri == "https://ustc.ac.uk/editions/43331"
    assert results.nodes[1].name_preferred == "Gilles, Nicole"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[2].name_preferred == "Sauvage, Denis"
    assert results.nodes[2].get_attribute("role") == "author"
    assert results.nodes[3].name_preferred == "Belleforest, François de"
    assert results.nodes[3].get_attribute("role") == "author"
    assert results.nodes[4].name_preferred == "Chappuys, Gabriel"
    assert results.nodes[4].get_attribute("role") == "author"
    assert results.nodes[5].name_preferred == "Chaudière, Guillaume"
    assert results.nodes[5].get_attribute("role") == "printer"
    assert results.nodes[6].name_preferred == "Binet, Denis"
    assert results.nodes[6].get_attribute("role") == "printer"

@pytest.mark.asyncio
async def test_parse_ustc_2():
    """
    record with a reference to the VD16, will parse VD16 instead
    """
    url = "https://ustc.ac.uk/editions/644002"
    results = await parse_ustc.parse_ustc(url)
    assert results.nodes[0].get_attribute("title")[0:74] == \
        ("¬Ein¬ Hübsche frag || von einem Jungling an einen || altẽ Cartheuser/ wie ")
    assert results.nodes[0].external_id[0].external_id == "S 10201"
    assert results.nodes[0].external_id[1].external_id == "644002"
    assert results.nodes[0].external_id[1].name == "ustc"


@pytest.mark.asyncio
async def test_parse_ustc_3():
    """
    record with a reference to the ISTC, will parse ISTc instead
    """
    url = "https://ustc.ac.uk/editions/743970"
    results = await parse_ustc.parse_ustc(url)
    assert results.nodes[1].name_preferred == "Christoph und Wolfgang, Herzöge in Bayern"
    # This is the title from the ISTC, in the IUSTC it is confused
    assert results.nodes[0].external_id[0].external_id == "ic00473365"
    assert results.nodes[0].external_id[1].external_id == "6658"
    assert results.nodes[0].external_id[2].external_id == "743970"


@pytest.mark.asyncio
async def test_parse_ustc_4():
    """
    record with a reference to the vd17, will parse vd17 instead
    """
    url = "https://ustc.ac.uk/editions/2704814"
    results = await parse_ustc.parse_ustc(url)
    assert results.nodes[0].external_id[0].external_id == "12:659962D"
    assert results.nodes[0].external_id[1].external_id == "2704814"

@pytest.mark.asyncio
async def test_parse_ustc_5():
    url = "https://ustc.ac.uk/editions/818885"
    results = await parse_ustc.parse_ustc(url)
    assert results.nodes[0].get_attribute("imprint") == "Vineggia: per Augustino Bindoni, 1554"
    # imprint different in ustc
    assert results.nodes[0].external_id[0].external_id == "9493"
    assert results.nodes[0].external_id[1].external_id == "818885"

@pytest.mark.asyncio
async def test_parse_ustc_6():
    """
    record with a reference to the ESTC, will parse the ESTC instead    
    """
    url = "https://ustc.ac.uk/editions/3051625"
    results = await parse_ustc.parse_ustc(url)
    assert results.nodes[0].external_id[0].external_id == "R17896"
    assert results.nodes[0].external_id[6].external_id == "3051625"
