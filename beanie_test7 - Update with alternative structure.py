#pylint: disable=C0301,C0114,C0116
import asyncio
#from rich import print
from beanie import WriteRules
#from beanie.odm.operators.find.element import BaseFindElementOperator
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
    entity_name = "The Bible"

    print("Beanie initialised")


    e1=classes.Entity()
    a1=classes.Attribute()
    a1.key="test"
    a1.value="test_value Genesis"
    e1.name="Genesis"
    e1.attributes.append(a1)
    await e1.save()

    r = classes.Entity.find(classes.Entity.name == "The Bible") # normally, one would have this entity alreaday waiting somewhere
    result_list = await r.to_list()
    far_entity = result_list[0]



    c1a=classes.Connection()
    c1a.entity=far_entity
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="part of"
    c1a.attributes.append(a1)
    #await c1a.save()

    c1b=classes.Connection()
    c1b.entity=e1
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="has part"
    c1b.attributes.append(a1)
    #await c1b.save()

    b1=classes.BridgeAlternative()
    b1.connections.append(c1a)
    b1.connections.append(c1b)
    await b1.save(link_rule=WriteRules.WRITE)


    r = classes.Entity.find(classes.Entity.name == "Martin Luther") # normally, one would have this entity alreaday waiting somewhere
    result_list = await r.to_list()
    far_entity = result_list[0]



    c1a=classes.Connection()
    c1a.entity=far_entity
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="wrote a commentary"
    c1a.attributes.append(a1)
    #await c1a.save()

    c1b=classes.Connection()
    c1b.entity=e1
    a1=classes.Attribute()
    a1.key="relation"
    a1.value="commentator of"
    c1b.attributes.append(a1)
    #await c1b.save()

    b1=classes.BridgeAlternative()
    b1.connections.append(c1a)
    b1.connections.append(c1b)
    await b1.save(link_rule=WriteRules.WRITE)



    await search_name("The Bible")
    await search_name("Martin Luther")
    await search_name("Genesis")



    return

async def search_name(entity_name):
    display_record = classes.EntityPlus()
    r = classes.BridgeAlternative.find(classes.BridgeAlternative.connections.entity.name == entity_name, fetch_links=True)
    result_list = await r.to_list()
    for bridge in result_list:
        for connection in bridge.connections:
            if connection.entity.name != entity_name:
                display_record.connections.append(connection)
            elif display_record.entity is None: # The entity has only to be added once
                display_record.entity = connection.entity
    print(display_record)






asyncio.run(main())
