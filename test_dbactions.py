
import pytest
from dotenv import load_dotenv


import classes
import db_actions

load_dotenv()


@pytest.mark.asyncio
async def test_create_person():
    """
    \todo validation needs full testing
    \todo missing adding attributes etc.
    """
    await db_actions.initialise_beanie()
    p=classes.Node()
    p.name="Test"
    r = await db_actions.save_person(p)
    assert r == "ERROR"
    p.type="Person"
    r = await db_actions.save_person(p)
    assert r.name == "Test"
    await p.delete()


@pytest.mark.asyncio
async def test_find_person_name():
    await db_actions.initialise_beanie()
#    classes.Entity.find()
    p=classes.Node()
    p.name="Test"
    p.type="Person"
    t = await db_actions.save_person(p)
    r=await db_actions.find_person("Test","name")
    assert r.__len__() == 1
    assert r[0].name == "Test"
    assert r[0].type == "Person"
    await r[0].delete()




