#pylint: disable=C0114,C0116,W0622,
import pytest

#import pytest_asyncio
from dotenv import load_dotenv
#from rich import print
from bpf.parsing import parse_edit16
#from bpf.parsing import parse_istc
#from bpf import classes
#from bpf import db_actions

#from beanie import WriteRules

#import classes^^
#import db_actions

#import get_external_data

load_dotenv()

async def create_test_ariosto():
    """
    has dfferent printer and publisher
    """
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE002694"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record

async def create_test_cavalli():
    """has only printers"""
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE068234"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record

async def create_test_venezia():
    """has only place and date of publication"""
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE001204"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record

async def create_test_praecepta():
    """
    has author with title and numbers (Byzantine Emperor)
    """
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE004578"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record


async def create_test_acta():
    """has an organisation as author"""
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE012947"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record


async def create_test_bulla():
    """has two printers written into one line"""
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE054041"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record

async def create_test_dante():
    """
    has author, author of comments, different publisher and printer
    """
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE001162"
    record = await parse_edit16.get_edit16_record_for_testing(url)
    return record

@pytest.mark.asyncio
async def test_edit16_get_id():
    record = await create_test_ariosto()
    result = parse_edit16.edit16_get_bibliographic_id(record)
    print("URI retrieved from function")
    assert result[0] == "edit16"
    assert result[1] == "https://edit16.iccu.sbn.it/titolo/CNCE002694"
    assert result[2] == "2694"

@pytest.mark.asyncio
async def test_edit16_get_title():
    record = await create_test_ariosto()
    title = parse_edit16.edit16_get_title(record)

    assert title == "Il Furioso di m. Lodouico Ariosto, ornato di varie figure, "\
    + "con cinque canti d'vn nuouo libro, & altre stanze del medesimo, nuouamente aggiunti: "\
        + "con belle allegorie: & nel fine, vna breue espositione de gli oscuri vocabuli: "\
            + "con la tauola di tutto quello che nell'opera si contiene."

@pytest.mark.asyncio
async def test_edit16_get_imprint():
    #has both printer and publisher
    record = await create_test_ariosto()
    imprint = parse_edit16.edit16_get_imprint(record)
    assert imprint == "Published: In Lione: appresso Bastiano di Bartholomeo Honorati, 1556; " \
    + "Printed: Stampato in Lione: per Iacopo Fabro"
    # has only printer
    record = await create_test_cavalli()
    imprint = parse_edit16.edit16_get_imprint(record)
    assert imprint == "Impressa in Venetia: per Iohane Baptista Sessa, 1502 a di 29 Zenaro"
    # only place and date of puablication
    record = await create_test_venezia()
    imprint = parse_edit16.edit16_get_imprint(record)
    assert imprint == "In Venetia, 1501"

@pytest.mark.asyncio
async def test_edit16_get_date():
    record = await create_test_ariosto()
    date = parse_edit16.edit16_get_date(record)
    assert date[0] == "1556"
    assert date[1] == (1556,1,1)
    assert date[2] == (1556,12,31)


@pytest.mark.asyncio
async def test_edit16_get_person():
    """
    Tests retrieving person names (authors, printers etc)
    """
    record = await create_test_ariosto()
    pl = parse_edit16.edit16_get_person(record)
    assert pl[0][0] == "Ariosto, Ludovico"
    assert pl[0][1] == "author"
    assert pl[0][2] == r"IT\ICCU\CNCA\000866"
    assert pl[0][3] == []
    assert pl[0][4] == []
    assert pl[1][0] == "Honorat, S©♭bastien"
    assert pl[1][1] == "publisher"
    assert pl[1][2] == r"IT\ICCU\BVEV\016947"
    assert pl[1][3] == ["Onorati, Sebastiano", "Honorati, Bastiano", "Honoratis, Sebastianus de"]
    assert pl[1][4] == [r'IT\ICCU\CNCT\003970', r'IT\ICCU\CNCT\004829', r'IT\ICCU\CNCT\004831']

@pytest.mark.asyncio
async def test_edit16_get_person_name_and_id_out_of_subfields():
    """
    Tests the retrieval of data of one person from subfields
    """
    record = await create_test_ariosto()
    field = record["700"]
    person_raw_list = parse_edit16.edit16_get_person_name_and_id_out_of_subfields(field)
    assert person_raw_list[0][0] == "Ariosto, Ludovico"
    assert person_raw_list[0][1] == ""
    assert person_raw_list[0][2] == r"IT\ICCU\CNCA\000866"
    field = record["712"]
    person_raw_list = parse_edit16.edit16_get_person_name_and_id_out_of_subfields(field)
    assert person_raw_list[0][0] == "Honorat, S©♭bastien"
    assert person_raw_list[0][1] == "publisher"
    assert person_raw_list[0][2] == r"IT\ICCU\BVEV\016947"
    # person_name for a ruler
    record = await create_test_praecepta()
    field = record["700"]
    person_raw_list = parse_edit16.edit16_get_person_name_and_id_out_of_subfields(field)
    assert person_raw_list[0][0] == "Basilius <imperatore d'Oriente ; 1.>"
    ### two persons in one line
    record = await create_test_bulla()
    field = record["712"]
    person_raw_list = parse_edit16.edit16_get_person_name_and_id_out_of_subfields(field)
    assert person_raw_list[0][0] == "Dorico, Valerio"
    assert person_raw_list[0][1] == "publisher"
    assert person_raw_list[0][2] == ""
    assert person_raw_list[1][0] == "Dorico, Luigi"
    assert person_raw_list[1][1] == "publisher"
    assert person_raw_list[1][2] == ""


@pytest.mark.asyncio
async def test_edit16_add_variants_and_variant_ids():
    record = await create_test_ariosto()
    person_raw = ["Honorat, S©♭bastien", "publisher", r"IT\ICCU\BVEV\016947"]
    person_complete = parse_edit16.edit16_add_variants_and_variant_ids(record, person_raw)
    assert person_complete[0] == "Honorat, S©♭bastien"
    assert person_complete[1] == "publisher"
    assert person_complete[2] == r"IT\ICCU\BVEV\016947"
    assert person_complete[3] == \
        ["Onorati, Sebastiano", "Honorati, Bastiano", "Honoratis, Sebastianus de"]
    assert person_complete[4] == \
        [r'IT\ICCU\CNCT\003970', r'IT\ICCU\CNCT\004829', r'IT\ICCU\CNCT\004831']

@pytest.mark.asyncio
async def test_edit16_get_place():
    """
    Test for finding places. 
    In this example the place-name appears twice
    in the record and is deduplicated
    """
    record = await create_test_ariosto()
    place = parse_edit16.edit16_get_place(record)
    assert place[0] == "Lione"
    assert len(place) == 1

@pytest.mark.asyncio
async def test_edit16_get_org():
    """
    Test for finding organisations
    (in this example the organsation
    is the author)
    """
    record = await create_test_acta()
    org_complete_list = parse_edit16.edit16_get_org(record)
    assert len(org_complete_list) == 1
    assert org_complete_list[0][0] == "Concilio di Trento"
    assert org_complete_list[0][1] == "author"
    assert org_complete_list[0][2] == r'IT\ICCU\CNCA\003434'
    assert org_complete_list[0][3] == ["Concilium Tridentinum <1545-1563>"]
    assert org_complete_list[0][4] == [r'IT\ICCU\CNCV\008382']


@pytest.mark.asyncio
async def test_edit16_0():
    # Dante: author, commentator, separate printer and publisher
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE001162"
    results = await parse_edit16.parse_edit16(url)
    assert results.nodes[0].get_attribute("title").startswith("Comedia "\
                            + "del diuino poeta Danthe Alighier")
    assert results.nodes[0].get_attribute("imprint") == "Published: In Vinegia: "\
        + "ad instantia di m. Gioanni Giolitto da Trino, 1536; Printed: In Vineggia: "\
        + "per m. Bernardino Stagnino, 1536"
    assert results.nodes[0].type == "BibliographicInformation"
    assert results.nodes[0].external_id[0].name == "edit16"
    assert results.nodes[0].external_id[0].external_id == "1162"
    assert results.nodes[0].external_id[0].uri == r'https://edit16.iccu.sbn.it/titolo/CNCE001162'
    assert results.nodes[0].dates[0].date_string == "1536"
    assert results.nodes[0].dates[0].date_start == (1536,1,1)
    assert results.nodes[0].dates[0].date_end == (1536,12,31)
    assert results.nodes[1].type == "person"
    assert results.nodes[1].name_preferred == "Alighieri, Dante"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[1].external_id[0].name == "edit16"
    assert results.nodes[1].external_id[0].external_id == r"IT\ICCU\CNCA\000318"
    assert results.nodes[2].type == "person"
    assert results.nodes[2].name_preferred == "Landino, Cristoforo"
    assert results.nodes[2].external_id[0].name == "edit16"
    assert results.nodes[2].external_id[0].external_id == r"IT\ICCU\CNCA\000138"
    assert results.nodes[2].get_attribute("role") == "author"
    assert results.nodes[2].get_attribute("name_variant") == "Landinus"
    # I don't know yet to to check the next name_variant
    assert results.nodes[2].external_id[1].name == "edit16"
    assert results.nodes[2].external_id[1].external_id == r"IT\ICCU\CNCV\023016"
    assert results.nodes[2].external_id[2].name == "edit16"
    assert results.nodes[2].external_id[2].external_id == r"IT\ICCU\CNCV\023018"
    assert results.nodes[4].type == "person"
    assert results.nodes[4].name_preferred == "Stagnino, Bernardino <1.>"
    assert results.nodes[4].external_id[0].name == "edit16"
    assert results.nodes[4].external_id[0].external_id == r"IT\ICCU\BVEV\023173"
    assert len(results.nodes[4].external_id) == 5
    assert results.nodes[4].get_attribute("role") == "publisher"
    assert results.nodes[5].type == "place"
    assert results.nodes[5].name_preferred == "Venezia"
    assert len(results.nodes) == 6


@pytest.mark.asyncio
async def test_edit16_1():
    """
    with organisation as author
    """
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE012947"
    results = await parse_edit16.parse_edit16(url)
    bib = results.nodes[0]
    assert bib.type == "BibliographicInformation"
    assert bib.get_attribute("title").startswith("Acta "\
                + "ac decreta sacrosanctae Tridentinae Synodi. ")
    assert bib.dates[0].date_string == "1548"
    assert bib.dates[0].date_start == (1548,1,1)
    assert bib.dates[0].date_end == (1548,12,31)
    assert bib.get_attribute("imprint") == \
        "Published: Mediol.: apud Innocentium Ciconiariam, 1548; "\
            + "Printed: Mediolani, calendis Martii 1548"
    assert bib.external_id[0].name == "edit16"
    assert bib.external_id[0].external_id == "12947"
    person = results.nodes[1]
    assert person.type == "person"
    assert person.name_preferred == "Cicognara, Innocenzo"
    assert person.get_attribute("role") == "publisher"
    assert person.external_id[0].name == "edit16"
    assert person.external_id[0].external_id == r"IT\ICCU\CNCV\900111"
    assert len(person.external_id) == 6
    org = results.nodes[2]
    assert org.type == "organisation"
    assert org.name_preferred == "Concilio di Trento"
    assert org.external_id[0].name == "edit16"
    assert org.external_id[0].external_id == r"IT\ICCU\CNCA\003434"
    assert org.get_attribute("name_variant") == "Concilium Tridentinum <1545-1563>"
    assert org.external_id[1].external_id == r'IT\ICCU\CNCV\008382'
    place = results.nodes[3]
    assert place.name_preferred == "Milano"
    assert len(results.nodes) == 4


@pytest.mark.asyncio
async def test_edit16_2():
    """
    with no place
    """
    url = "https://edit16.iccu.sbn.it/c/titoli/unimarc/export?id=CNCE041185"
    results = await parse_edit16.parse_edit16(url)
    bib = results.nodes[0]
    assert bib.type == "BibliographicInformation"
    assert bib.get_attribute("title").startswith ("Litterae S.D.N. Gregorii Papae 13")
    assert bib.external_id[0].name == "edit16"
    assert bib.external_id[0].external_id == "41185"
    assert bib.external_id[0].uri == r'https://edit16.iccu.sbn.it/titolo/CNCE041185'
    assert bib.dates[0].date_string == "1579"
    assert bib.dates[0].date_start == (1579,1,1)
    assert bib.dates[0].date_end == (1579,12,31)
    org = results.nodes[1]
    assert org.type == "organisation"
    assert org.name_preferred == "Agostiniani"
    assert org.external_id[0].name == "edit16"
    assert org.external_id[0].external_id == r"IT\ICCU\CNCA\000487"
    assert len(org.external_id) == 8
    assert len(results.nodes) == 2
