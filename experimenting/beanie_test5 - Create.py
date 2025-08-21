#pylint: disable=C0301,C0114,C0116
import asyncio
from rich import print
from beanie import WriteRules
from beanie.odm.operators.find.element import BaseFindElementOperator
from dotenv import load_dotenv

import db_actions
import classes

load_dotenv()

"""
New Test of Beanie
Using no EntityAndConnections
Using Bridge/Connections instead of the single EntityConnections

"""


#@classes.func_logger
#@pytest.mark.asyncio
async def main():
    await db_actions.initialise_beanie()
    print("Beanie initialised")


    e1=classes.Node()
    a1=classes.Attribute()
    a1.key="test"
    a1.value="test_value luther"
    e1.name="Martin Luther"
    e1.attributes.append(a1)
    await e1.save()

    e2=classes.Node()
    a2=classes.Attribute()
    a2.key="test"
    a2.value="test_value bible"
    e2.name="The Bible"
    e2.attributes.append(a2)
    await e2.save()

    c1a=classes.Connection()
    c1a.entity=e1
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="translated by"
    c1a.attributes.append(a1)

    c1b=classes.Connection()
    c1b.entity=e2
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="translator of"
    c1b.attributes.append(a1)

    b1=classes.Bridge()
    b1.connection.append(c1a)
    b1.connection.append(c1b)
    await b1.save(link_rule=WriteRules.WRITE)


    e3=classes.Node()
    e3.name="Albrecht Dürer"
    await e3.save()


    c2a=classes.Connection()
    c2a.entity=e3
    a2=classes.Attribute()
    a1.key="relation"
    a1.value="iillustrated by"
    c1a.attributes.append(a1)

    c2b=classes.Connection()
    c2b.entity=e2
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="illustrator of"
    c2b.attributes.append(a1)

    b2=classes.Bridge()
    b2.connection.append(c2a)
    b2.connection.append(c2b)
    await b2.save(link_rule=WriteRules.WRITE)

    result= await search_name("The Bible")

    return

async def search_name(entity_name):


    # the following is from the mouth of the Pythia:
    pipeline = [
        {
            "$unwind": "$connection"
        },
        {
            "$lookup": {
                "from": "all_collections",  # the collection name in MongoDB (not the class name)
                "localField": "connection.entity.$id",
                "foreignField": "_id",
                "as": "entity_link"
            }
        },
        {
            "$unwind": "$entity_link"
        },
        {
            "$match": {
                "entity_link.name": entity_name
            }
        }
    ]
    results = await classes.Bridge.aggregate(pipeline).to_list()

    for bridge in results:
        for connection in bridge:
            pass


    print(results)


    #result_list = await r.to_list()
    


    


asyncio.run(main())
