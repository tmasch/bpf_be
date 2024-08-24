import requests
import unittest
import json
from unittest import mock
import pytest
import pytest_asyncio
import urllib.request

from beanie import Document, Link
from dotenv import load_dotenv

import get_external_data
import parse_iiif
import logging
import classes
import db_actions   

#logger = logging.getLogger(__name__)
load_dotenv()

@pytest.mark.asyncio
#@classes.func_logger
async def mock_get_web_data_as_json(*args, **kwargs):
    print("mocking web call")
    print(args[0])
    if args[0] == "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest":
        print("URL: https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest")
        f = open("herbarius_metadata.json","r")
        print("Getting data from herbarius_metadata.json")
        mock_json=json.load(f)
        f.close()
        return mock_json
    else:
        url=args[0]
        url = url.replace(" ", "%20")
        url_opened = urllib.request.urlopen(url)
        contents = json.load(url_opened)
        return contents

    return (None, 404)

#    print(r)


def test_get_web_data_as_json():
    return 1


