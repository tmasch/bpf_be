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
async def insert_data():
    luther=classes.Entity()
    luther.name="Martin Luther"

    bible=classes.Entity()
    bible.name="The Bible"

    luther_bible=classes.EntityConnection()
    luther_bible.entityA=luther
    luther_bible.nameA=luther.name
    luther_bible.entityB=bible
    luther_bible.nameB=bible.name
    luther_bible.relationA="Translator of"
    luther_bible.relationB="translated by"
#    await luther_bible.save(link_rule=WriteRules.WRITE)

    melanchton=classes.Entity()
    melanchton.name="Melanchton"

    luther_melanchton=classes.EntityConnection()
    luther_melanchton.entityA=melanchton
    luther_melanchton.nameA=melanchton.name
    luther_melanchton.entityB=luther
    luther_melanchton.nameB=luther.name
    luther_melanchton.relationA="candidate"
    luther_melanchton.relationB="candidate"

#    await luther_melanchton.save(link_rule=WriteRules.WRITE)


    duerer=classes.Entity()
    duerer.name="Albrecht Dürer"

    duerer_bible=classes.EntityConnection()
    duerer_bible.entityB=duerer
    duerer_bible.entityA=bible
    duerer_bible.relationA="Illustrator of"
    duerer_bible.relationB="illustrated by by"
#    await duerer_bible.save(link_rule=WriteRules.WRITE)

    l=[]
    l.append(luther_melanchton)
    l.append(duerer_bible)
    l.append(luther_bible)

    for e in l:
        print(e)
        await e.save(link_rule=WriteRules.WRITE)

async def main():
    await db_actions.initialise_beanie()

    await insert_data()


    print("Search Luther")
    r = await classes.EntityConnection.find(classes.EntityConnection.entityA.name == "Martin Luther", fetch_links=True).to_list()
#    print(r)


    print("Search Bible")
    r = classes.EntityConnection.find(classes.EntityConnection.entityA.name == "The Bible", fetch_links=True)
    print(await r.to_list())
    r = classes.EntityConnection.find(classes.EntityConnection.entityB.name == "The Bible", fetch_links=True)
    print(await r.to_list())

    print("Search Luther as Entity")
    r = classes.Entity.find(classes.Entity.name=="Martin Luther", fetch_links = True)
    print(await r.to_list())

asyncio.run(main())
