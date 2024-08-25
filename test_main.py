#pylint: disable=C0301,C0116
"""
Testing of main
"""
#import os
from unittest import mock
import pytest

import main

import db_actions
import get_external_data
import test_get_external_data

#os.environ["MONGODB_HOST"] = "localhost"
#os.environ["MONGODB_PORT"] = "27017"

@mock.patch('get_external_data.get_web_data_as_json', side_effect=test_get_external_data.mock_get_web_data_as_json)
@pytest.mark.asyncio
async def test_get_metadata(self):
    await db_actions.initialise_beanie()
    # Herbarius as standard test case
    iiif_url="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    material="book"
    r = await main.get_metadata(iiif_url,material)
