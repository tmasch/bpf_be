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


    e1=classes.Entity()
    a1=classes.Attribute()
    a1.key="test"
    a1.value="test_value luther"
    e1.name="Martin Luther"
    e1.attributes.append(a1)

    e2=classes.Entity()
    a2=classes.Attribute()
    a2.key="test"
    a2.value="test_value bible"
    e2.name="The Bible"
    e2.attributes.append(a2)

    ec1=classes.EntityConnection()
    ec1.entityA=e1
    ec1.entityB=e2
    ec1.relationA="Translator of"
    ec1.relationB="translated by"
    await ec1.save(link_rule=WriteRules.WRITE)

    e3=classes.Entity()
    e3.name="Albrecht Dürer"

    ec2=classes.EntityConnection()
    ec2.entityA=e2
    ec2.entityB=e3
    ec2.relationA="Illustrator of"
    ec2.relationB="illustrated by by"
    await ec2.save(link_rule=WriteRules.WRITE)


    print("Search Luther")
    r = classes.EntityConnection.find(classes.EntityConnection.entityA.name == "Martin Luther", fetch_links=True)
    print(await r.to_list())


    print("Search Bible")
    r = classes.EntityConnection.find(classes.EntityConnection.entityA.name == "The Bible", fetch_links=True)
    print(await r.to_list())
    r = classes.EntityConnection.find(classes.EntityConnection.entityB.name == "The Bible", fetch_links=True)
    print(await r.to_list())


asyncio.run(main())
