#pylint: disable=C0114,C0116,W0622,
import pytest
#import pytest_asyncio
from dotenv import load_dotenv
from rich import print
#from beanie import WriteRules

#import classes
#import db_actions
import parse_istc
#import get_external_data

load_dotenv()


@pytest.mark.asyncio
async def parse_bibliographic_id():
    pass
