#pylint: disable=C0301,C0114,C0116
import asyncio
#from rich import print
from beanie import WriteRules, DeleteRules
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
    entity_name = "Martin Luther"

    print("Beanie initialised")

    r = classes.BridgeAlternative.find(classes.BridgeAlternative.connections.entity.name == entity_name, fetch_links=True)
    result_list = await r.to_list()
    for bridge in result_list:
        for connection in bridge.connections:
            await connection.delete(link_rule=DeleteRules.DO_NOTHING)
        await bridge.delete(link_rule=DeleteRules.DO_NOTHING)
    
    
    r = classes.Entity.find(classes.Entity.name == entity_name) 
    result_list = await r.to_list()
    result = result_list[0] # Normally, one would search for a uniqueID
    await result.delete()



    await search_name("The Bible")
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
