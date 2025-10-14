"""
Testing of db_actions.py
"""
import pytest
from dotenv import load_dotenv

from . import classes
from . import db_actions

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
    """
    Test find_person, case searching by name
    """
    await db_actions.initialise_beanie()
    p=classes.Node()
    p.name="Test"
    p.type="Person"
    await db_actions.save_person(p)
    r=await db_actions.find_person("Test","name")
    assert len(r) == 1
    assert r[0].name == "Test"
    assert r[0].type == "Person"
    await r[0].delete()
    