
"""
Test of GND parsing
"""
import pytest

from bpf import db_actions
from bpf.parsing import parse_gnd

@pytest.mark.asyncio
async def test_parse_gnd_get_records():
    """
    This test is beyond my pay-greade, I don't know what it does. 
    """
    await db_actions.initialise_beanie()
    gnd_id="11860354X"
    records=await parse_gnd.get_person_records(gnd_id)
    assert type(records).__name__ == "_Element"

## Test records for persons

async def create_test_record_rubens():
    """
    Create a test Person record for Pieter Paul Rubens
    """
    gnd_id="11860354X"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]


async def create_test_record_thomas_aquinas():
    """
    Create a test Person record for Thomas Aquinas
    """
    gnd_id="118622110"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]

async def create_test_record_max_emanuel():
    """
    Create a test Person record for Elector Max Emanuel
    """
    gnd_id="11857941X"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]

async def create_test_record_saint_scholastica():
    """
    Create a test Person record for St Scholastica
    """
    gnd_id="122475127"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]

async def create_test_record_queen_anne():
    """
    Create a test Person record for Queen Anne
    """
    gnd_id="118649450"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]

async def create_test_record_adolf_friedrich():
    """
    Create a test Person record for Adolf Friedrich 
    """
    # One of the relatively few persons with a person-person relation that has a time attached
    gnd_id="100014704"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]

async def create_test_record_caspar_adolay():
    """
    Create a test Person record for Caspar Adolay
    """
    gnd_id = "100004636"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]

async def create_test_record_arenswald():
    """
    Create a test Person record for Arenswald
    """
    gnd_id = "100014747"
    r=await parse_gnd.get_person_records(gnd_id)
    return r[0]



#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_record_get_gnd_internal_id():
    """
    Tests gnd_record_get_gnd_internal_id
    """
    await db_actions.initialise_beanie()
    rubens=await create_test_record_rubens()
    gnd_internal=parse_gnd.gnd_record_get_gnd_internal_id(rubens)[0]
    assert gnd_internal.name=="GND intern"
    assert gnd_internal.external_id=="11860354X"

# I am not sure if this function is needed: it appears to be identical
# to the ID that is in 035 with prefix "(DE-101)"

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_record_get_external_references():
    """
    Test for parsing external references (field 035)
    """
    await db_actions.initialise_beanie()
    # Rubens: Person. old record has Prefix (DE-588a)
    rubens=await create_test_record_rubens()
    external_references=parse_gnd.gnd_record_get_external_references(rubens)
    assert external_references[0].name=="GND internal"
    assert external_references[0].external_id == "11860354X"
    assert external_references[0].uri == ""
    assert external_references[1].name=="GND"
    assert external_references[1].external_id == "11860354X"
    assert external_references[1].uri == "https://d-nb.info/gnd/11860354X"
    assert external_references[2].name== "GND old"
    assert external_references[2].external_id == "187114714"
    assert external_references[2].uri == ""
    assert external_references[3].name== "GND old"
    assert external_references[3].external_id == "127110801"
    assert external_references[3].uri == ""
    # I don't do a separate test for DE-588b and DE-588c
    # since none of the usual guinea-pigs has here
    # anything that is not a repetition of a 035 subfield a.
    # Kathedrale Antwerpen - old record has DE-588c, but it is a repeatition
    kathedrale_antwerpen = await create_test_record_kathedrale_antwerpen()
    external_references = parse_gnd.gnd_record_get_external_references(kathedrale_antwerpen)
    assert len(external_references) == 2 #without the old IDs.
    #assert external_references[2].name == "GND old"
    #assert external_references[2].external_id == "4068763-6"



#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_name_preferred():
    """
    Gets the preferred name from a person (field 100)
    """
    #Only subfield a filled

    await db_actions.initialise_beanie()
    rubens=await create_test_record_rubens()
    name_preferred=parse_gnd.gnd_record_get_person_name_preferred(rubens)
    assert name_preferred[0] == 'Rubens, Peter Paul'
    assert name_preferred[1] == ''

    #Also subfield c filled - not a ruler - Saint

    thomas=await create_test_record_thomas_aquinas()
    name_preferred=parse_gnd.gnd_record_get_person_name_preferred(thomas)
    assert name_preferred[0] == 'Thomas (von Aquin)'
    assert name_preferred[1] == 'Saint'

    #Also subfield b filled -
    #subfield c filled with a ruler's
    #designation that is to be ignored

    maximilian=await create_test_record_max_emanuel()
    name_preferred=parse_gnd.gnd_record_get_person_name_preferred(maximilian)
    assert name_preferred[0] == 'Maximilian Emanuel II.'
    assert name_preferred[1] == 'Bayern, Kurfürst'

    #Subfield c only indicates a saint

    scholastica=await create_test_record_saint_scholastica()
    name_preferred=parse_gnd.gnd_record_get_person_name_preferred(scholastica)
    assert name_preferred[0] == 'Scholastika'
    assert name_preferred[1] == 'Saint'

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_get_sex():
    """
    tests for the sex of a person (field 375)
    """
    await db_actions.initialise_beanie()
    #men
    thomas=await create_test_record_thomas_aquinas()
    sex = parse_gnd.gnd_record_get_sex(thomas)
    assert sex == "male"
    #women
    anne=await create_test_record_queen_anne()
    sex = parse_gnd.gnd_record_get_sex(anne)
    print(sex)
    assert sex == "female"
    #not indicated
    scholastica=await create_test_record_saint_scholastica()
    sex = parse_gnd.gnd_record_get_sex(scholastica)
    assert sex == ""

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_get_person_name_variant():
    """
    Tests gnd_record_get_person_name_variant
    """
    await db_actions.initialise_beanie()
    # Max Emanuel (first additional name has subfields a and b, and c with a comma;
    # 12th additional name has subfields a and b, and c without comma)
    maximilian=await create_test_record_max_emanuel()
    name_variants, comments = parse_gnd.gnd_record_get_person_name_variant(maximilian, "")
    print(name_variants[0])
    print(comments)
    assert name_variants[0] == "Massimiliano Emanuele II."
    assert "Baviera, Duca" in comments
    assert name_variants[11] == "Maximilianus Emmanuel (Palatinae Dux)"

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_get_connected_persons():
    """
    Tests gnd_record_get_connected_persons
    """
    await db_actions.initialise_beanie()
    # Max Emanuel (first connected person has subfields a and c, 4, and 9 with 'v:')
    maximilian=await create_test_record_max_emanuel()
    connected_persons = parse_gnd.gnd_record_get_connected_persons(maximilian)
    connection0 = connected_persons[0]
    person0 = connection0.entityB
    assert person0.name == "Ferdinand Maria (Bayern, Kurfürst)"
    assert person0.external_id[0].name == "GND"
    assert person0.external_id[0].external_id == "119105691"
    assert person0.external_id[0].uri == "https://d-nb.info/gnd/119105691"
    # The following two assertions are true by error (see below)
    assert person0.external_id[1].uri == "https://d-nb.info/gnd/119105691"
    assert person0.external_id[2].external_id == "https://d-nb.info/gnd/119105691"
    assert connection0.relationB == "bezf"
    assert connection0.connection_comment == "Vater"
    # 7th connected person has subfields a, b and c, 4, and 9 with 'v:'
    connection6 = connected_persons[6]
    person6 = connection6.entityB
    assert person6.name == "Karl VII. (Heiliges Römisches Reich, Kaiser)"
    assert connection6.relationB == "bezf"
    assert connection6.connection_comment == "Sohn"
    # Adolf Friedrich von Mecklenburg - has relationship with time attached:
    adolf=await create_test_record_adolf_friedrich()
    connected_persons = parse_gnd.gnd_record_get_connected_persons(adolf)
    connection1 = connected_persons[1]
    assert connection1.relationB == "bezf"
    assert connection1.connection_comment == "Ehefrau, 1. Ehe"
    assert connection1.connection_time == "1622-1634"

    # Some comments:
    # There are several subfields "0" that can contain
        # the GND ID, prefaced by "(DE-588)"
        # the internal ID of the Deutsche Nationalbibliothek, prefaced by "(DE-101)"
            #  (for persons normally identical to the GND ID, for orgs and places not)
        # the URI containing the GND ID
    # I need:
        # The GND ID with the name "GND"
        # Only if it is different, the internal ID with a different name
        # (for searches in VIAF, where the GND ID is not viable because of a bug in VIAF)

    # It may furthermore make sense to provide for the possibilit
    #  that there is no such subfield, but only one with a URI
    # it may make sense to read also 500 subfield d (date) to improve the dummy nodes
    # connection_comment is actually a comment on relationB (and later on, it will become relationB,
    # since the information displayed in relationB is very vague)

#@mock.patch('get_external_data.get_web_data_as_json', }
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_get_connected_orgs():
    """
    Tests gnd_record_get_connected_orgs
    """
    await db_actions.initialise_beanie()
    # Adolf Friedrich von Mecklenburg, connected to one organisationthat has 510 a,
    # as well as 510 9, with "v:" and "Z:"
    adolf=await create_test_record_adolf_friedrich()
    connected_orgs = parse_gnd.gnd_record_get_connected_orgs(adolf)
    connection0 = connected_orgs[0]
    org0 = connection0.entityB
    assert org0.name == "Fruchtbringende Gesellschaft"
    assert org0.external_id[0].external_id=="004706463"
    assert org0.external_id[1].external_id=="2011193-9"
    assert connection0.relationB == "affi"
    assert connection0.connection_comment == "175"
    assert connection0.connection_time == "1629-"
    # Caspar Adolay, connected to one organisation that has 510 a and 510 b
    caspar = await create_test_record_caspar_adolay()
    connected_orgs = parse_gnd.gnd_record_get_connected_orgs(caspar)
    connection0 = connected_orgs[0]
    org0 = connection0.entityB
    assert org0.name == "Bayern (Bayerischer Landtag)"
    assert connection0.relationB == "affi"
    # Some comments:
    # Also here problem with multiple subfields 0, see above

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_get_connected_places():
    """
    Tests gnd_record_get_connected_places
    """
    await db_actions.initialise_beanie()
    # Rubens: first connected places has subfields a and 4, second a, 4 and 9, the latter with "v:"
    rubens = await create_test_record_rubens()
    connected_places = parse_gnd.gnd_record_get_connected_places(rubens)
    connection0 = connected_places[0]
    place0 = connection0.entityB
    assert place0.name == "Siegen"
    assert place0.external_id[0].external_id=="04054883X"
    assert place0.external_id[1].external_id=="4054883-1"
    assert connection0.relationB=="ortg"
    connection1 = connected_places[1]
    assert connection1.relationB=="ortw"
    assert connection1.connection_comment=="dort aufgewachsen"
    # Arenswald: connected to places with subfields a, g, 4 and 9, the latter with "Z:"
    arenswald = await create_test_record_arenswald()
    connected_places = parse_gnd.gnd_record_get_connected_places(arenswald)
    connection0 = connected_places[0]
    place0 = connection0.entityB
    assert place0.name=="Neuenkirchen (Amt Anklam-Land)"
    assert connection0.relationB=="ortw"
    assert connection0.connection_time=="1765-1770"


#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_record_get_comments():
    """
    Tests gnd_record_get_comments
    """
    await db_actions.initialise_beanie()
    # Max Emanuel - has a field 678 but also many other elements beforehand
    # that would be written into the comment field"
    maximilian=await create_test_record_max_emanuel()
    comment = parse_gnd.gnd_record_get_comments(maximilian, "")
    assert comment == "seit 1679 Kurfürst von Bayern; " \
        + "1692-1706 Generalstatthalter der Spanischen Niederlande"


#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_record_get_dates():
    """
    Tests gnd_record_get_dates
    """
    await db_actions.initialise_beanie()
    # elector Maximilian: two dates, the first years only, type "datl",
    # the second days, datetype "datx"
    maximilian=await create_test_record_max_emanuel()
    date=parse_gnd.gnd_record_get_dates(maximilian)
    date0 = date[0]
    assert date0.datestring_raw=="1662-1726"
    assert date0.datetype=="datl"
    date1 = date[1]
    assert date1.datestring_raw=="11.07.1662-26.02.1726"
    assert date1.datetype=="datx"


#@mock.patch('get_external_data.get_web_data_as_json',\
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_profession():
    """
    Tests gnd_record_get_professions
    """
    await db_actions.initialise_beanie()
    # elector Maximilian: has profession
    maximilian = await create_test_record_max_emanuel()
    profession=parse_gnd.gnd_record_get_profession(maximilian, "")
    assert profession=="Kurfürst"

    # some entries also seem to have subfield 9, starting with "v:", I should add that.


# Test records for organisations

async def create_test_record_electrochemical_society():
    """
    Creates a test organisation record for a subgroup of the electrochemical society
    """
    gnd_id="343-8"
    r=await parse_gnd.get_org_records(gnd_id)
    return r[0]

async def create_test_record_academy_religion():
    """
    Creates a test organisation record for the american academy of religion
    """
    gnd_id="364-5"
    r=await parse_gnd.get_org_records(gnd_id)
    return r[0]

async def create_test_record_nato():
    """
    Creates a test organisation record for an institution of the NATO
    """
    gnd_id="378-5"
    r=await parse_gnd.get_org_records(gnd_id)
    return r[0]


async def create_test_record_gesellschaft_kernforschung():
    """
    Creates a test organisation record for a subgroup fo the Gesellschaft für Kernforschung
    """
    gnd_id="2036894-X"
    r=await parse_gnd.get_org_records(gnd_id)
    return r[0]


#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_org_name_preferred():
    """
    Tests gnd_record_get_org_name_preferred
    """
    await db_actions.initialise_beanie()
    # Electrochemical Society has a subfield b
    electrochemical_society=await create_test_record_electrochemical_society()
    name_preferred= parse_gnd.gnd_record_get_org_name_preferred(electrochemical_society)
    assert name_preferred=="Electrochemical Society (Electrothermics and Metallurgy Division)"
    # Academy of Relgion and Mental Health has a subfield g
    academy_of_religion = await create_test_record_academy_religion()
    name_preferred= parse_gnd.gnd_record_get_org_name_preferred(academy_of_religion)
    assert name_preferred=="Academy of Religion and Mental Health (New York, NY)"
    # Gesellschaft für Kernforschung has subfields b and g
    gesellschaft_kernforschung=await create_test_record_gesellschaft_kernforschung()
    name_preferred=parse_gnd.gnd_record_get_org_name_preferred(gesellschaft_kernforschung)
    assert name_preferred == \
        "Gesellschaft für Kernforschung (Abteilung Datenverarbeitung und Instrumentierung) " \
            + "(Karlsruhe)"
    # (this is not pretty, but it will be rare)
    # I have no text for the x since I didn't find an example

    # Currently, the parsing does not support repetible subfields b and g -
    # I have no clue if they exist.

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_org_name_variant():
    """
    Tests gnd_record_get_org_name_variant
    """
    await db_actions.initialise_beanie()
    academy_of_religion = await create_test_record_academy_religion()
    # Academy of Religion and Mental Health has subfield g
    name_variant= parse_gnd.gnd_record_get_org_name_variant(academy_of_religion)
    assert name_variant[0]=="Académie de Religion et de Santé Mentale (New York, NY)"
    # Nato subcommittee has subfield g
    nato= await create_test_record_nato()
    name_variant= parse_gnd.gnd_record_get_org_name_variant(nato)
    assert name_variant[1] == \
        "NATO (Groupe Consultatif pour la Recherche et le Développement Aérospatial)"

    # there may be a repetition of the subfield b, and we should cater for this.


async def create_test_record_kathedrale_antwerpen():
    """
    Creates a test Place record for Antwerp Cathedral
    """
    gnd_id="4068763-6"
    r=await parse_gnd.get_place_records(gnd_id)
    return r[0]

async def create_test_record_ardabil():
    """
    Creates a test Place record for the town of Ardabil
    """
    gnd_id="4068833-1"
    r=await parse_gnd.get_place_records(gnd_id)
    return r[0]

async def create_test_record_regierungsbezirk_merseburg():
    """
    Creates a test Place record for the Regierungsbezhierk Merseburg
    """
    gnd_id="15720-X"
    r=await parse_gnd.get_place_records(gnd_id)
    return r[0]

async def create_test_record_britisch_ostafrika():
    """
    Creates a test Place record for British East Africa
    """
    gnd_id="14267-0"
    r=await parse_gnd.get_place_records(gnd_id)
    return r[0]

#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_entity_type():
    """
    tests gnd_record_get_entity_type
    """
    await db_actions.initialise_beanie()
    kathedrale_antwerpen = await create_test_record_kathedrale_antwerpen()
    entity_type = parse_gnd.gnd_record_get_entity_type(kathedrale_antwerpen)
    assert entity_type[0]=="g"
    assert entity_type[1]=="gib"


#@mock.patch('get_external_data.get_web_data_as_json',\
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_geonames():
    """
    tests gnd_record_get_geonames
    """
    await db_actions.initialise_beanie()
    ardabil = await create_test_record_ardabil()
    geonames = parse_gnd.gnd_record_get_geonames(ardabil)
    assert geonames[0].external_id=="143083"
    assert geonames[0].uri=="https://sws.geonames.org/143083"


#@mock.patch('get_external_data.get_web_data_as_json', \
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_coordinates():
    """
    tests gnd_record_get_coordinates
    """
    await db_actions.initialise_beanie()
    ardabil = await create_test_record_ardabil()
    coordinates = parse_gnd.gnd_record_get_coordinates(ardabil)
    assert coordinates[0].west=="E 048 17 35"
    assert coordinates[0].east=="E 048 17 35"
    assert coordinates[0].north=="N 038 14 59"
    assert coordinates[0].south=="N 038 14 59"
    assert coordinates[1].west=="E048.293300"
    assert coordinates[1].east=="E048.293300"
    assert coordinates[1].north=="N038.249800"
    assert coordinates[1].south=="N038.249800"



#@mock.patch('get_external_data.get_web_data_as_json',\
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_place_name_preferred():
    """
    Tests gnd_record_get_place_name_preferred
    """
    await db_actions.initialise_beanie()
    # Ardabil, has only subfield a
    ardabil = await create_test_record_ardabil()
    name_preferred = parse_gnd.gnd_record_get_place_name_preferred(ardabil)
    assert name_preferred=="Ardabil"
    # Kathedrale Antwerpen has subfields a and g
    kathedrale_antwerpen = await create_test_record_kathedrale_antwerpen()
    name_preferred = parse_gnd.gnd_record_get_place_name_preferred(kathedrale_antwerpen)
    assert name_preferred=="Kathedrale Antwerpen (Antwerpen)"

    # I dop not test the subfields x and z because I haven't found
    # any examples for their use


#@mock.patch('get_external_data.get_web_data_as_json',\
# side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_gnd_record_get_place_name_variant():
    """
    Tests gnd_record_get_place_name_variant
    """
    await db_actions.initialise_beanie()
    # Ardabil, has only subfield a
    ardabil = await create_test_record_ardabil()
    name_variant = parse_gnd.gnd_record_get_place_name_variant(ardabil)
    assert name_variant[0]=="Ardebil"
    # Kathedrale Antwerpen has subfields a and g
    kathedrale_antwerpen = await create_test_record_kathedrale_antwerpen()
    name_variant = parse_gnd.gnd_record_get_place_name_variant(kathedrale_antwerpen)
    assert name_variant[0]=="Liebfrauenkathedrale Antwerpen (Antwerpen)"
    # Regierungsbezirk Merseburg has two synonyms that, however,
    # have the relation "spio", they should be supressed
    regierungsbezirk_merseburg = await create_test_record_regierungsbezirk_merseburg()
    name_variant = parse_gnd.gnd_record_get_place_name_variant(regierungsbezirk_merseburg)
    assert not name_variant
    # Britisch Ostafrika has in one synym a field "x" without having in "4" the spio
    # > this should not be excluded
    britisch_ostafrika=await create_test_record_britisch_ostafrika()
    name_variant = parse_gnd.gnd_record_get_place_name_variant(britisch_ostafrika)
    assert name_variant[5]=="Großbritannien (Kolonie)"

    # Subfield x can be repeated, this should be included here.
    # I did not check subfield z because I didn't find an example
