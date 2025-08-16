#pylint: disable=C0116
"""
Test of GND parsing
"""
from unittest import mock
import pytest
import pytest_asyncio
import test_get_external_data
#import requests
#import unittest
#import json

#from beanie import Document, Link
#from dotenv import load_dotenv
#import logging

from lxml import etree
import get_external_data
import parse_gnd
#import classes
import db_actions

#import test_get_external_data

#@mock.patch('get_external_data.get_web_data_as_json', side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_name_preferred():
    await db_actions.initialise_beanie()
    authority_id = "11860354X"
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D'\
              + authority_id\
                  + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
    result = []
    content=await get_external_data.get_web_data(authority_url)
    root = etree.XML(content)
    records=root.find("records", namespaces=root.nsmap)
#    print(records)
#    print(records.tag)
#    tag_id='400'
#    subfield_code="a"
    for record in records:
        print("found record")
    pass
