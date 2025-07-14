#pylint: disable=C0301,C0114,C0116
import asyncio
from rich import print
from beanie import WriteRules
from dotenv import load_dotenv

import db_actions
import classes

load_dotenv()

#@classes.func_logger
#@pytest.mark.asyncio
async def main():
    await db_actions.initialise_beanie()
    print("adding entity 'Genesis' and connecting it with entity 'Bible'")

    e1=classes.Entity()
    e1.name = "Genesis"

    eac2 = classes.EntityAndConnections()
    eac2.entity = e1
    eac2.name = "Genesis and connections"



    r= classes.EntityAndConnections.find(classes.EntityAndConnections.entity.name == "The Bible", fetch_links=True)
    result_list = await r.to_list()
    eac1 = result_list[0]

    ec1=classes.EntityConnection()
    ec1.entityA=e1
    ec1.entityB=eac1.entity
    ec1.relationA="part of"
    ec1.relationB="has part"

    eac1.connected_entities.append(ec1)
    eac2.connected_entities.append(ec1)


    await eac1.save(link_rule=WriteRules.WRITE)
    await eac2.save(link_rule=WriteRules.WRITE)




    r= classes.EntityAndConnections.find(classes.EntityAndConnections.entity.name == "The Bible", fetch_links=True)
    result_list = await r.to_list()
    print("result of addition of Genesis in record 'The Bible'")
    print(result_list[0])

    r= classes.EntityAndConnections.find(classes.EntityAndConnections.entity.name == "Genesis", fetch_links=True)
    print("result of addition of Genesis in record 'Genesis'")
    result_list = await r.to_list()
    print(result_list[0])

    


asyncio.run(main())
