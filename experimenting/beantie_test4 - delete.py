#pylint: disable=C0301,C0114,C0116
import asyncio
from rich import print
from beanie import WriteRules, DeleteRules
from dotenv import load_dotenv

import db_actions
import classes

load_dotenv()

#@classes.func_logger
#@pytest.mark.asyncio
async def main():
    await db_actions.initialise_beanie()
    print("deleting entity 'Genesis' and its connection with the entity 'Bible'")
    list_of_connected_entities = []
    r= classes.EntityAndConnections.find(classes.EntityAndConnections.entity.name == "Genesis", fetch_links=True)
    result_list = await r.to_list()
    eac1 = result_list[0]
    e_id = eac1.entity.id

    for connection in eac1.connected_entities:
        if connection.entityA.id != e_id:
            list_of_connected_entities.append(connection.entityA.id)
        if connection.entityB.id != e_id:
            list_of_connected_entities.append(connection.entityB.id)
    print("connected entities that have to be changed")
    print(list_of_connected_entities)

    for connected_entity in list_of_connected_entities:
        print("connected_entity")
        print(connected_entity)
        r= classes.EntityAndConnections.find(classes.EntityAndConnections.entity.id == connected_entity, fetch_links=True)
        result_list = await r.to_list()
        eac2 = result_list[0]
        print("record that has to be updated")
        print(eac2)
        for connection in eac2.connected_entities:
            print("entityA")
            print(connection.entityA)
            print("entityB")
            print(connection.entityB)
            if connection.entityA.id == e_id or connection.entityB.id == e_id:
                print("removing one connection")
                eac2.connected_entities.remove(connection)
                break
        await eac2.replace(link_rule=WriteRules.DO_NOTHING)

    for connection in eac1.connected_entities:
        await connection.delete(link_rule=DeleteRules.DO_NOTHING)
    await eac1.entity.delete(link_rule=DeleteRules.DO_NOTHING)
    await eac1.delete(link_rule=DeleteRules.DO_NOTHING)
    print("record 'Bible' after deletion")
    r= classes.EntityAndConnections.find(classes.EntityAndConnections.entity.name == "The Bible", fetch_links=True)
    result_list = await r.to_list()
    print(result_list[0])




asyncio.run(main())
