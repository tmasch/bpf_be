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

import parse_gnd
import db_actions

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


async def create_test_record_thomas_aquinas():
    gnd_id="118622110"
    r=await parse_gnd.get_records(gnd_id)
    return r[0]

async def create_test_record_max_emanuel():
    gnd_id="11857941X"
    r=await parse_gnd.get_records(gnd_id)
    return r[0]

async def create_test_record_saint_scholastica():
    gnd_id="122475127"
    r=await parse_gnd.get_records(gnd_id)
    return r[0]


#@mock.patch('get_external_data.get_web_data_as_json', side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
#@classes.func_logger
async def test_parse_gnd_name_preferred():
    """
    Only subfield a filled
    """
    await db_actions.initialise_beanie()
    rubens=await create_test_record_rubens()
    name_preferred=parse_gnd.gnd_record_get_name_preferred(rubens)
    assert name_preferred[0] == 'Rubens, Peter Paul'
    assert name_preferred[1] == ''
    """
    Also subfield c filled - not a ruler - Saint
    """
    thomas=await create_test_record_thomas_aquinas()
    name_preferred=parse_gnd.gnd_record_get_name_preferred(thomas)
    assert name_preferred[0] == 'Thomas (von Aquin)'
    assert name_preferred[1] == 'Saint'
    """
    Also subfield b filled - 
    subfield c filled with a ruler's
    designation that is to be ignored
    """
    max=await create_test_record_max_emanuel()
    name_preferred=parse_gnd.gnd_record_get_name_preferred(max)
    assert name_preferred[0] == 'Maximilian Emanuel II.'
    assert name_preferred[1] == 'Bayern, Kurfürst'
    """
    Subfield c only indicates a saint
    """
    scholastica=await create_test_record_saint_scholastica()
    name_preferred=parse_gnd.gnd_record_get_name_preferred(scholastica)
    assert name_preferred[0] == 'Scholastika'
    assert name_preferred[1] == 'Saint'
