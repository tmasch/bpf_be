
import pytest
from dotenv import load_dotenv


import classes
import db_actions

load_dotenv()


@pytest.mark.asyncio
async def test_create_person():
    await db_actions.initialise_beanie()
    p=classes.Entity()
    p.name="Test"
    r = await db_actions.save_person(p)

@pytest.mark.asyncio
async def test_create_person_with_linked_person():
    await db_actions.initialise_beanie()

    pass
