"""
Tests for parsing bibliographical records from the VD17 and VD18
"""

#pylint: disable=C0114,C0116,W0622,
import pytest
#import pytest_asyncio
from dotenv import load_dotenv
from rich import print
from bpf.parsing import parse_vd17_vd18
#from bpf import classes
from bpf import db_actions
#from beanie import WriteRules

#import classes
#import db_actions

#import get_external_data

load_dotenv()

async def create_test_occo():
    """
    VD17
    Creates test record for a book on coins
    one author, one place, organisation as printer, year
    """
    bib_id = "23:230233Z"
    url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + \
        bib_id  + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record




async def create_test_rance():
    """
    VD18
    Creates test recordfor a book by Abbé de Rancé
    one author, one place, one printer and one publisher, one year
    """
    bib_id = "14620189"
    url = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18' \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record


async def create_test_khraysser():
    """
    VD17
    Creates test record
    one author, two places, printer, publisher
    simple title without additions or subtitle
    """
    bib_id = "12:125035V"
    url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record


async def create_test_confessio():
    """
    VD17
    one author, one place, printer, publisher (not properly marked in the record)
    title,volume number, part title. 
    """
    bib_id = "7:706624Z"
    url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record


async def create_test_reglemens():
    """
    VD18
    one author, one place, one publisher
    title and volume number, no part title
    """
    bib_id = "80336132"
    url = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18' \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record

async def create_test_baudrand():
    """
    VD18
    One author, one place, one publisher
    has series titel and series number
    """
    bib_id = "15354199"
    url = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18' \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record


async def create_test_biblia():
    """
    VD18
    Publisher is an organisation
    """
    bib_id = "90986598"
    url = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18' \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record


async def create_test_trithemius_opera():
    """
    vd17
    is a series > should be expluded
    """
    bib_id = "23:231165H"
    url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record


async def create_test_hueffer():
    """
    vd18
    with indication of an edition
    """
    bib_id = "80531490"
    url = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18' \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    record = await parse_vd17_vd18.get_vd17_record_for_testing(url)
    return record



@pytest.mark.asyncio
async def test_vd17_get_bib_id():
    """
    tests getting IDs of publications
    """
    # VD17
    occo = await create_test_occo()
    for record in occo:
        bib_id = parse_vd17_vd18.vd17_get_id(record)
        print("bib_ids")
        print(bib_id)
        assert bib_id[0].external_id == "23:230233Z"
        assert bib_id[0].name == "vd17"
        assert bib_id[0].uri == \
            r'https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%2723:230233Z%27'
    # VD18
    rance = await create_test_rance()
    for record in rance:
        bib_id = parse_vd17_vd18.vd17_get_id(record)
        print("bib_ids")
        print(bib_id)
        break # I only need the first record, but subscription with [0] does not seem to work.
    assert bib_id[0].external_id == "14620189"
    assert bib_id[0].name == "vd18"
    assert bib_id[0].uri == \
        r'https://vd18.k10plus.de/SET=2/TTL=1/CMD?ACT=SRCHA&IKT=8080&SRT=YOP&TRM=VD18' \
            + r'14620189&ADI_MAT=B'


@pytest.mark.asyncio
async def test_vd17_get_record_type():
    await db_actions.initialise_beanie()
    occo = await create_test_occo()
    for record in occo:
        record_type = parse_vd17_vd18.vd17_get_record_type(record)
        assert record_type == " "
    opera = await create_test_trithemius_opera()
    for record in opera:
        record_type = parse_vd17_vd18.vd17_get_record_type(record)
        assert record_type == "a"

@pytest.mark.asyncio
async def test_vd17_get_author():
    await db_actions.initialise_beanie()
    #VD17
    occo = await create_test_occo()
    for record in occo:
        author_list = parse_vd17_vd18.vd17_get_author(record)
        assert author_list[0].name_preferred == "Occo, Adolf"
        assert author_list[0].type == "person"
        assert author_list[0].get_attribute("role") == "author"
        assert author_list[0].external_id[0].name == "GND"
        assert author_list[0].external_id[0].external_id == "117079510"
    #VD18
    rance = await create_test_rance()
    for record in rance:
        author_list = parse_vd17_vd18.vd17_get_author(record)
        break
    assert author_list[0].name_preferred == "Rancé, Armand Jean Le Bouthillier de"
    assert author_list[0].type == "person"
    assert author_list[0].get_attribute("role") == "author"
    assert author_list[0].external_id[0].name == "GND"
    assert author_list[0].external_id[0].external_id == "118598244"

@pytest.mark.asyncio
async def test_vd17_get_title():
    await db_actions.initialise_beanie()
    # VD17 -title only
    khraysser = await create_test_khraysser()
    for record in khraysser:
        title, volume_number, part_title = parse_vd17_vd18.vd17_get_title(record)
        assert title ==\
              "Compendium Electoralis Iuris Bavarici, Daß ist: Ein kurtze Verfassung der " \
                + "Landtrecht/ Gerichts-Malefitz/ und anderer Ordnungen/ der ChurFürstenthumb "\
                    + "Obern unnd Nidern Bayrn"


    #VD17 - title and subtitle
    occo = await create_test_occo()
    for record in occo:
        title, volume_number, part_title = parse_vd17_vd18.vd17_get_title(record)
        assert title ==\
              "Impp. Romanorum Numismata : A Pompeio Magno Ad Heraclium"


    # VD17 - title and volume title
    confessio = await create_test_confessio()
    for record in confessio:
        title, volume_number, part_title = parse_vd17_vd18.vd17_get_title(record)
        assert title  == "Augustanae Confessionis ... Pars ..."
        assert volume_number == "2"
        assert part_title == "Continens Articulos, In quibus recensentur Abusus"

    # VD18 - only title??
    rance = await create_test_rance()
    for record in rance:
        title, volume_number, part_title = parse_vd17_vd18.vd17_get_title(record)
        break
    assert title  ==\
              "Des Hochwürdigen und Gottseeligen Im Leben und nach dem Todt wunderthätigen "\
                + "Herrn Armandi Joannis De Rancé, Abbtens und Reformators des Closters U. L. "\
                    + "Frauen zu La Trapp Cistercienser Ordens, Welcher den 27. Octobris 1700. "\
                        + "heilig verschiden ist, Vortreffliches Werck von der Heiligkeit "\
                            + "und denen Pflichten des Clösterlichen Lebens"

    # VD18 - title and volume number

    reglemens = await create_test_reglemens()
    for record in reglemens:
        title, volume_number, part_title = parse_vd17_vd18.vd17_get_title(record)
        break
    assert title ==\
              "Réglemens De La Maison-Dieu De Notre-Dame De La Trappe : "\
                + "mis en nouvel ordre & augmentés des Usages particuliers De La Maison-Dieu De "\
                    + "La Val-Sainte De Notre-Dame De La Trappe Au Canton De Fribourg En Suisse, "\
                        + "choisis & tirés Par Les Premiers Religieux De Ce Monastère ..."
    assert volume_number == "2"



@pytest.mark.asyncio
async def test_vd17_get_edition():
    await db_actions.initialise_beanie()
    hueffer = await create_test_hueffer()
    for record in hueffer:
        edition = parse_vd17_vd18.vd17_get_edition(record)
        break
    assert edition == "Neue verbesserte Auflage"


@pytest.mark.asyncio
async def test_vd17_get_series():
    await db_actions.initialise_beanie()
    # VD18 - series title and series number
    baudrand = await create_test_baudrand()
    for record in baudrand:
        series_title, series_number = parse_vd17_vd18.vd17_get_series(record)
        break
    assert series_title == "Baudrand, Barthélemy: Geistliche Schriften"
    assert series_number == "4"


@pytest.mark.asyncio
async def test_vd17_get_date_raw():
    await db_actions.initialise_beanie()
    # VD17 - normal year
    occo = await create_test_occo()
    for record in occo:
        date_raw = parse_vd17_vd18.vd17_get_date_raw(record)
        assert date_raw == "1601"

    # VD18 - normal year
    rance = await create_test_rance()
    for record in rance:
        date_raw = parse_vd17_vd18.vd17_get_date_raw(record)
        break
    assert date_raw == "1750"



@pytest.mark.asyncio
async def test_vd17_get_imprint():
    await db_actions.initialise_beanie()
    #vd17
    occo = await create_test_occo()
    for record in occo:
        imprint = parse_vd17_vd18.vd17_get_imprint(record)
        assert imprint == "Avgvstae Vindelicorvm, ad insigne pinus ... " \
            + "Anno sæculi decimi sexti.primo. - Im Kolophon: Avgvstae Vindelicorvm " \
                + "Anno MDCI. Prid. Kal. April."
    #vd18
    rance = await create_test_rance()
    for record in rance:
        imprint = parse_vd17_vd18.vd17_get_imprint(record)
        break
    assert imprint == "Augspurg, verlegts Matthäus Rieger, Buchhandler, 1750. - "\
        + "Vorlageform des Kolophons: Augspurg, gedruckt bey Bernhard Homodeus Mayer, "\
            + "Cathol. Buch- und Zeitungs Drucker"

    # field missing
    confessio = await create_test_confessio()
    for record in confessio:
        imprint = parse_vd17_vd18.vd17_get_imprint(record)
        assert imprint == ""


@pytest.mark.asyncio
async def test_vd17_get_person():
    await db_actions.initialise_beanie()
    # vd17, 2 persons
    confessio = await create_test_confessio()
    for record in confessio:
        person_list = parse_vd17_vd18.vd17_get_person(record)
        assert person_list[0][0] == "Mamphras, Jeremias"
        assert person_list[0][1] == "printer"
        assert person_list[0][2].name == "GND"
        assert person_list[0][2].external_id == "1037531809"
        assert person_list[1][0] == "Starck, Daniel"
        assert person_list[1][1] == "printer"
        assert person_list[1][2].name == "GND"
        assert person_list[1][2].external_id == "1037512634"

@pytest.mark.asyncio
async def test_vd17_get_printer():
    await db_actions.initialise_beanie()
    rance = await create_test_rance()
    for record in rance:
        person_list = parse_vd17_vd18.vd17_get_printer_name(record)
        assert person_list[0][0] == "Rieger"
        assert person_list[0][1] == "printer"
        assert person_list[1][0] == "Mayer"
        assert person_list[1][1] == "printer"



@pytest.mark.asyncio
async def test_vd17_get_org():
    await db_actions.initialise_beanie()
    # vd17, org as printer
    occo = await create_test_occo()
    for record in occo:
        org_list = parse_vd17_vd18.vd17_get_org(record)
        assert org_list[0][0] == "Druckerei Ad insigne Pinus"
        assert org_list[0][1] == "printer"
        assert org_list[0][2].external_id == "6146135-0"
        assert org_list[0][2].name == "GND"
    # vd18, org as publisher
    biblia =await create_test_biblia()
    for record in biblia:
        org_list = parse_vd17_vd18.vd17_get_org(record)
        break
    assert org_list[0][0] == "Johann Andreas Endter Erben"
    assert org_list[0][1] == "publisher"
    assert org_list[0][2].external_id == "6146131-3"
    assert org_list[0][2].name == "GND"

@pytest.mark.asyncio
async def test_vd17_get_place():
    await db_actions.initialise_beanie()
    #vd17, one place
    occo = await create_test_occo()
    for record in occo:
        place_list = parse_vd17_vd18.vd17_get_place(record)
        assert place_list[0][0] == "Augsburg"
        assert place_list[0][1] == "place of publication"
        assert len(place_list[0]) == 2 #no ID given
    # vd17, two places
    khraysser = await create_test_khraysser()
    for record in khraysser:
        place_list = parse_vd17_vd18.vd17_get_place(record)
        assert place_list[0][0] == "Augsburg"
        assert place_list[0][1] == "place of publication"
        assert len(place_list[0]) == 2 #no ID given
        assert place_list[1][0] == "Ingolstadt"
        assert place_list[1][1] == "place of publication"
        assert len(place_list[1]) == 2 #no ID given
    # vd18, one place, has ID
    biblia = await create_test_biblia()
    for record in biblia:
        place_list = parse_vd17_vd18.vd17_get_place(record)
        break
    assert place_list[0][0] == "Nürnberg"
    assert place_list[0][1] == "place of publication"
    assert place_list[0][2].name == "GND"
    assert place_list[0][2].external_id == "4042742-0"


@pytest.mark.asyncio
async def test_vd17_map_printing_year():
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_year_prefix\
        ("ca. ", "1610", 1610, 1610)
    assert date_string == "about 1610"
    assert date_start == 1608
    assert date_end == 1612
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_year_prefix\
        ("nicht vor ", "1610", 1610, 1610)
    assert date_string == "not before 1610"
    assert date_start == 1610
    assert date_end == 1615
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_year_prefix\
        ("i.e. ", "1610", 1610, 1610)
    assert date_string == "1610 (corrected date)"
    assert date_start == 1610
    assert date_end == 1610


@pytest.mark.asyncio
async def test_vd17_map_printing_year_original_spelling():
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_year_original_spelling(\
        "Anno 1700")
    assert date_string == "1700"
    assert date_start == 1700
    assert date_end == 1700
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_year_original_spelling(\
        "Anno M.D.CC.")
    assert date_string == "1700"
    assert date_start == 1700
    assert date_end == 1700
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_year_original_spelling(\
        "18. Jh.")
    assert date_string == "18th century"
    assert date_start == 1701
    assert date_end == 1800


@pytest.mark.asyncio
async def test_vd17_map_printing_date():
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("1648")
    assert date_string == "1648"
    assert date_start == (1648,1,1)
    assert date_end == (1648,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("[1648]")
    assert date_string == "1648"
    assert date_start == (1648,1,1)
    assert date_end == (1648,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("[ca. 1630]")
    assert date_string == "about 1630"
    assert date_start == (1628,1,1)
    assert date_end == (1632,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("M.DC.LXXXXV.")
    assert date_string == "1695"
    assert date_start == (1695,1,1)
    assert date_end == (1695,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("1683 [?]")
    assert date_string == "1683"
    assert date_start == (1683,1,1)
    assert date_end == (1683,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("Anno 1674")
    assert date_string == "1674"
    assert date_start == (1674,1,1)
    assert date_end == (1674,12,31)
    date_string, date_start, date_end = \
        parse_vd17_vd18.vd17_map_printing_date("Gedruckt im Jahr/ M.D.CXXXII")
    assert date_string == "1632"
    assert date_start == (1632,1,1)
    assert date_end == (1632,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("1071 [i.e. 1701]")
    assert date_string == "1701 (corrected date)"
    assert date_start == (1701,1,1)
    assert date_end == (1701,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("[MDC]LXXXV")
    assert date_string == "1685"
    assert date_start == (1685,1,1)
    assert date_end == (1685,12,31)
    date_string, date_start, date_end = \
    parse_vd17_vd18.vd17_map_printing_date("1683 [erschienen] 1685")
    assert date_string == "1685"
    assert date_start == (1685,1,1)
    assert date_end == (1685,12,31)
    date_string, date_start, date_end = \
        parse_vd17_vd18.vd17_map_printing_date("[nach 1670]")
    assert date_string == "after 1670"
    assert date_start == (1670,1,1)
    assert date_end == (1675,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("[1765?]")
    assert date_string == "1765?"
    assert date_start == (1765,1,1)
    assert date_end == (1765,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("1764-1767")
    assert date_string == "1764-1767"
    assert date_start == (1764,1,1)
    assert date_end == (1767,12,31)
    date_string, date_start, date_end = parse_vd17_vd18.vd17_map_printing_date("[1764-1767]")
    assert date_string == "1764-1767"
    assert date_start == (1764,1,1)
    assert date_end == (1767,12,31)


@pytest.mark.asyncio
async def test_parse_vd17_0():
    # VD17
    # simple title
    # organisation as printer
    await db_actions.initialise_beanie()
    bib_id = "23:230233Z"
    url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + \
        bib_id  + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    results = await parse_vd17_vd18.parse_vd17(url)
    assert results.nodes[0].get_attribute("title") == \
        "Impp. Romanorum Numismata : A Pompeio Magno Ad Heraclium. " + \
        "Editio Altera, Multis nummorum millibus aucta"
    assert results.nodes[0].get_attribute("imprint") == \
        "Avgvstae Vindelicorvm, ad insigne pinus ... Anno sæculi decimi sexti.primo."\
             + " - Im Kolophon: Avgvstae Vindelicorvm Anno MDCI. Prid. Kal. April."
    assert results.nodes[0].external_id[0].name == "vd17"
    assert results.nodes[0].external_id[0].external_id == "23:230233Z"
    assert results.nodes[0].dates[0].date_string == "1601"
    assert results.nodes[0].dates[0].date_start == (1601,1,1)
    assert results.nodes[0].dates[0].date_end == (1601,12,31)
    assert results.nodes[1].name_preferred == "Occo, Adolf"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[1].external_id[0].name == "GND"
    assert results.nodes[1].external_id[0].external_id == "117079510"
    assert results.nodes[2].name_preferred == "Druckerei Ad insigne Pinus"
    assert results.nodes[2].external_id[0].name == "GND"
    assert results.nodes[2].external_id[0].external_id == "6146135-0"
    assert results.nodes[3].name_preferred == "Augsburg"
    assert results.nodes[3].get_attribute("role") == "place of publication"



@pytest.mark.asyncio
async def test_parse_vd17_1():
    # title, volume_number, part_title
    await db_actions.initialise_beanie()
    bib_id = "7:706624Z"
    url = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + \
        bib_id  + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    results = await parse_vd17_vd18.parse_vd17(url)
    assert results.nodes[0].get_attribute("title") == \
        "Augustanae Confessionis ... Pars ..."
    assert results.nodes[0].get_attribute("volume_number") == "2"
    assert results.nodes[0].get_attribute("part_title") == \
        "Continens Articulos, In quibus recensentur Abusus. " \
        + "Editio altera, priori emendati .."
    assert results.nodes[0].external_id[0].name == "vd17"
    assert results.nodes[0].external_id[0].external_id == "7:706624Z"
    assert results.nodes[0].dates[0].date_string == "1653"
    assert results.nodes[0].dates[0].date_start == (1653,1,1)
    assert results.nodes[0].dates[0].date_end == (1653,12,31)
    assert results.nodes[1].name_preferred == "Mylius, Georg"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[2].name_preferred == "Mamphras, Jeremias"
    assert results.nodes[2].get_attribute("role") == "printer"
    assert results.nodes[3].name_preferred == "Starck, Daniel"
    assert results.nodes[3].get_attribute("role") == "printer"



@pytest.mark.asyncio
async def test_parse_vd17_2():
    # vd18
    # series_title, series_volume
    await db_actions.initialise_beanie()
    bib_id = "15354199"
    url = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18' \
        + bib_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    results = await parse_vd17_vd18.parse_vd17(url)
    assert results.nodes[0].get_attribute("title") == \
        "Baudrand, Barthélemy: Geistliche Schriften"
    assert results.nodes[0].get_attribute("volume_number") == "4"
    assert results.nodes[0].get_attribute("part_title") == \
        "Die büßende Seele, oder Betrachtungen über die wichtigsten Glaubenswahrheiten : mit "\
            + "Geschichten und Beyspielen beleuchtet. Sammt einer Erklärung der sieben Bußpsalmen"
    assert results.nodes[0].get_attribute("imprint") == "Augsburg, bey Nicolaus Doll. 1793"
    assert results.nodes[1].name_preferred == "Baudrand, Barthélemy"
    assert results.nodes[1].get_attribute("role") == "author"
    assert results.nodes[1].external_id[0].external_id == "100030076"
    assert results.nodes[2].name_preferred == "Doll, Nikolaus"
    assert results.nodes[2].external_id[0].external_id == "1037499018"
    assert results.nodes[2].get_attribute("role") == "publisher"
    assert results.nodes[3].name_preferred == "Augsburg"
    assert results.nodes[3].get_attribute("role") == "place of publication"
