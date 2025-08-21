#pylint: disable=C0301,C0114,C0116,W0622
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
    luther=classes.Node()
    luther.name="Martin Luther"

    bible=classes.Node()
    bible.name="The Bible"

    luther_bible=classes.Edge()
    luther_bible.entityA=luther
    luther_bible.nameA=luther.name
    luther_bible.entityB=bible
    luther_bible.nameB=bible.name
    luther_bible.relationA="Translator of"
    luther_bible.relationB="translated by"
#    await luther_bible.save(link_rule=WriteRules.WRITE)

    melanchton=classes.Node()
    melanchton.name="Melanchton"

    luther_melanchton=classes.Edge()
    luther_melanchton.entityA=melanchton
    luther_melanchton.nameA=melanchton.name
    luther_melanchton.entityB=luther
    luther_melanchton.nameB=luther.name
    luther_melanchton.relationA="candidate"
    luther_melanchton.relationB="candidate"

#    await luther_melanchton.save(link_rule=WriteRules.WRITE)


    duerer=classes.Node()
    duerer.name="Albrecht Dürer"

    duerer_bible=classes.Edge()
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

#    await insert_data()


    print("Search Luther")
    r = await classes.Edge.find(classes.Edge.entityA.name == "Martin Luther", fetch_links=True).to_list()
#    print(r)


    print("Search Bible")
    r = classes.Edge.find(classes.Edge.entityA.name == "The Bible", fetch_links=True)
    print(await r.to_list())
    r = classes.Edge.find(classes.Edge.entityB.name == "The Bible", fetch_links=True)
    print(await r.to_list())

    print("Search Luther as Entity")
    r = classes.Node.find(classes.Node.name=="Martin Luther", fetch_links = True)
    print(await r.to_list())

asyncio.run(main())
