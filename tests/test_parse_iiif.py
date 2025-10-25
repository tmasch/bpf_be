#pylint: disable=C0116
"""
Test of iiif parsing
"""
#from unittest import mock
import pytest
from dotenv import load_dotenv
from rich import print
#import pytest_asyncio

#import test_get_external_data
#import requests
#import unittest
#import json
#from beanie import Document, Link
#from dotenv import load_dotenv
#import logging


#import get_external_data
#import classes
from bpf import db_actions
from bpf.parsing import parse_iiif
#import test_get_external_data

load_dotenv()

@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_iiif_herbarius():
    await db_actions.initialise_beanie()
    uri_entered="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    r= await parse_iiif.parse_iiif(uri_entered,"b")
    print(r)
