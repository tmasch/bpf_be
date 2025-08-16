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


    e1=classes.Node()
    a1=classes.Attribute()
    a1.key="test"
    a1.value="test_value luther"
    e1.name="Martin Luther"
    e1.attributes.append(a1)

    e2=classes.Node()
    a2=classes.Attribute()
    a2.key="test"
    a2.value="test_value bible"
    e2.name="The Bible"
    e2.attributes.append(a2)

    ec1=classes.Edge()
    ec1.entityA=e1
    ec1.entityB=e2
    ec1.relationA="Translator of"
    ec1.relationB="translated by"
    await ec1.save(link_rule=WriteRules.WRITE)

    e3=classes.Node()
    e3.name="Albrecht Dürer"

    ec2=classes.Edge()
    ec2.entityA=e2
    ec2.entityB=e3
    ec2.relationA="Illustrator of"
    ec2.relationB="illustrated by by"
    await ec2.save(link_rule=WriteRules.WRITE)

    eac1 = classes.EntityAndConnections()
    eac1.entity=e1
    eac1.connected_entities=[ec1]
    eac1.name = "Martin Luther Connections"
    await eac1.save(link_rule=WriteRules.WRITE)

    eac2 = classes.EntityAndConnections()
    eac2.entity=e2
    eac2.connected_entities=[ec1, ec2]
    eac2.name = "The Bible Connections"
    await eac2.save(link_rule=WriteRules.WRITE)

    eac3 = classes.EntityAndConnections()
    eac3.entity = e3
    eac3.connected_entities=[ec2]
    eac3.name = "Albrecht Dürer Connection"
    await eac3.save(link_rule=WriteRules.WRITE)


    print("Search Luther")
    r = classes.Edge.find(classes.Edge.entityA.name == "Martin Luther", fetch_links=True)
    print(await r.to_list())


    print("Search Bible")
    r = classes.Edge.find(classes.Edge.entityA.name == "The Bible", fetch_links=True)
    print(await r.to_list())
    r = classes.Edge.find(classes.Edge.entityB.name == "The Bible", fetch_links=True)
    print(await r.to_list())

    print("Search Luther as Entity")
    r = classes.Node.find(classes.Node.name=="Martin Luther", fetch_links = True)
    print(await r.to_list())


    print("search Bible as EntityAndConnections")
    r = classes.EntityAndConnections.find(classes.EntityAndConnections.entity.name=="The Bible", fetch_links=True)
    result_list = await r.to_list()
    connected_entities_list = []
    for result in result_list:
        id = result.entity.id
        print("id of core record")
        print(id)
        for connection in result.connected_entities:
            if connection.entityA.id != id:
                connected_entities_list.append(connection.entityA)
            if connection.entityB.id != id:
                connected_entities_list.append(connection.entityB)
    print("connected entities:")
    print(connected_entities_list)

asyncio.run(main())
