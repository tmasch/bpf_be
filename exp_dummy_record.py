"""
Module contains functions for producing dummy records
"""
import asyncio
import exp_classes
import exp_db_actions

async def dummy_record_manuscript():
    """
    Returns a dummy manifest for a manuscript
    """
    manuscript = exp_classes.Node()
    manuscript_plus = exp_classes.NodePlus()

    manuscript.add_attribute("type", "manifest")
    manuscript.add_attribute("type", "manuscript")
    manuscript.add_attribute("number of images", "423")

    manuscript_plus.node = manuscript

    page = exp_classes.Node()
    page.add_attribute("index", "19")
    page.add_attribute("label_raw", "8v (0020)")
    page.add_attribute("label_prefix", "fol. ")
    page.add_attribute("label_page", "8v")
    # perhaps label_volume, or is it never needed?
    page.add_attribute("hight", "6796")
    page.add_attribute("width", "5084")
    page.add_attribute("base_url", r"https://api.digitale-sammlungen.de/iiif/image/v2/bsb00087481_00020")
    # what is the attribute 'format' supposed to do?


    page_connection = exp_classes.Edge()
    page_connection.nodeA = manuscript
    page_connection.nodeB = page
    page_connection.add_attribute("relationA", "page in")
    page_connection.add_attribute("relationb", "has page")

    manuscript_plus.edges.append(page_connection)

    page = exp_classes.Node()
    page.add_attribute("index", "20")
    page.add_attribute("label_raw", "9r (0021)")
    page.add_attribute("labeL_prefix", "fol. ")
    page.add_attribute("label_page", "9r")
    # perhaps label_volume, or is it never needed?
    page.add_attribute("hight", "6533")
    page.add_attribute("width", "5024")
    page.add_attribute("base_url", "https://api.digitale-sammlungen.de/iiif/image/v2/bsb00087481_00021")
    # what is the attribute 'format' supposed to do?


    page_connection = exp_classes.Edge()
    page_connection.nodeA = manuscript
    page_connection.nodeB = page
    page_connection.add_attribute("relationA", "page in")
    page_connection.add_attribute("relationb", "has page")

    manuscript_plus.edges.append(page_connection)


    page = exp_classes.Node()
    page.add_attribute("index", "21")
    page.add_attribute("label_raw", "9v (0022)")
    page.add_attribute("label_prefix", "fol. ")
    page.add_attribute("label_page", "9v")
    # perhaps label_volume, or is it never needed?
    page.add_attribute("hight", "6533")
    page.add_attribute("width", "5024")
    page.add_attribute("base_url", "https://api.digitale-sammlungen.de/iiif/image/v2/bsb00087481_00022")
    # what is the attribute 'format' supposed to do?


    page_connection = exp_classes.Edge()
    page_connection.nodeA = manuscript
    page_connection.nodeB = page
    page_connection.add_attribute("relationA", "page in")
    page_connection.add_attribute("relationb", "has page")
    page_connection.add_attribute("qualifier", "current")

    manuscript_plus.edges.append(page_connection)


    coll = exp_classes.Node()
    coll.add_attribute("type", "Organisation")
    coll.add_attribute("type", "Collection")
    coll.add_attribute("raw", "yes")
    coll.add_attribute('name', "Bayerische Staatsbibliothek")

    coll_connection = exp_classes.Edge()
    coll_connection.nodeA = manuscript
    coll_connection.nodeB = coll
    coll_connection.add_attribute("relationA", "manuscript in")
    coll_connection.add_attribute("relationB", "has manuscript")
    coll_connection.add_attribute("qualifier", "current")
    coll_connection.add_attribute("inventory", "Clm 4452")


    manuscript_plus.edges.append(coll_connection)


    return manuscript_plus


async def dummy_record_collection(search_name):

    collection = exp_classes.Node()
    collection.add_attribute("type", "Organisation")
    collection.add_attribute("type", "Collection")
    collection.add_attribute("name", "Bayerische Staatsbibliothek")
    collection.add_attribute("name_add", "Bibliotheca Regia Monacensis")
    collection.add_attribute("name_add", "Bavarian State Library")

    gnd = exp_classes.ExternalReference()
    gnd.uri=r"http://d-nb.info/gnd/2031351-2"
    gnd.name = "GND"
    gnd.id = "2031351-2"

    collection.external_id.append(gnd)


    date = exp_classes.Date()
    date.date_string = "founded 1919"
    date.date_start = (1919, 0, 0)

    collection.dates.append(date)


    town = exp_classes.Node()
    town.add_attribute("type", "Place")
    town.add_attribute("type", "Town")
    town.add_attribute("name", "München")
    town.add_attribute("raw", "yes")


    town_connection = exp_classes.Edge()
    town_connection.nodeA = collection
    town_connection.nodeB = town
    town_connection.add_attribute("relationA", "has organisation")
    town_connection.add_attribute("relationB", "organisation in")

    collection_plus = exp_classes.NodePlus()
    collection_plus.node = collection
    collection_plus.edges.append(town_connection)

    x = ""
    name = collection_plus.node.get_attribute("name")[0]
    if name == search_name:

        x = collection_plus

    return x
    








async def main():
    await exp_db_actions.initialise_beanie()
    manuscript_plus = await dummy_record_manuscript()
    print(manuscript_plus)
    print("xxx")

    collection_plus = await dummy_record_collection("Bayerische Staatsbibliothek")
    print(collection_plus)


asyncio.run(main())




