#pylint: disable=C0116
"""
Test of iiif parsing
"""
from unittest import mock
import pytest

import test_get_external_data
#import requests
#import unittest
#import json
import pytest_asyncio
#from beanie import Document, Link
#from dotenv import load_dotenv
#import logging


import get_external_data
import parse_iiif
#import classes
import db_actions
#import test_get_external_data

@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_iiif_herbarius():
#    logging.basicConfig(level=logging.DEBUG)
#    logging.getLogger().addHandler(logging.StreamHandler())

    await db_actions.initialise_beanie()

    uri_entered="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    r= await parse_iiif.parse_iiif(uri_entered,"b")
    print(r)
