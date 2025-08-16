#pylint: disable=C0116
"""
Test of GND parsing
"""
#from unittest import mock
import pytest
#import pytest_asyncio
#import test_get_external_data
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

@pytest.mark.asyncio
async def test_parse_gnd_get_records():
    await db_actions.initialise_beanie()
    gnd_id="11860354X"
    records=await parse_gnd.get_records(gnd_id)
    assert type(records).__name__ == "_Element"

async def create_test_record_rubens():
    gnd_id="11860354X"
    r=await parse_gnd.get_records(gnd_id)
    return r[0]

#@mock.patch('get_external_data.get_web_data_as_json', side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_name_preferred():
    await db_actions.initialise_beanie()
    record=await create_test_record_rubens()
    name_preferred=parse_gnd.gnd_record_get_name_preferred(record)
    assert name_preferred[0] == 'Rubens, Peter Paul'
    assert name_preferred[1] == ''