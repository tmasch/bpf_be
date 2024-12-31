#import requests
#import unittest
import json
#from unittest import mock
import urllib.request
import pytest
import pytest_asyncio

#from beanie import Document, Link
from dotenv import load_dotenv

import get_external_data
#import parse_iiif
import logging
import classes
#import db_actions   

#logger = logging.getLogger(__name__)
load_dotenv()

@pytest.mark.asyncio
#@classes.func_logger
async def mock_get_web_data_as_json(*args, **kwargs):
    print("mocking web call")
    print(args[0])
    if args[0] == "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest":
        print("URL: https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest")
        f = open("herbarius_manifest.json","r")
        print("Getting data from herbarius_manifest.json")
        mock_json=json.load(f)
        f.close()
        return mock_json
    else:
        print("Getting data from the interweb")
        url=args[0]
        url = url.replace(" ", "%20")
        url_opened = urllib.request.urlopen(url)
        contents = json.load(url_opened)
        return contents
    return (None, 404)

#    print(r)


def test_get_web_data_as_json():
    return 1


#@classes.func_logger
@pytest.mark.asyncio
async def test_get_external_data():
    authority_id = "11860354X"
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D'\
              + authority_id\
                  + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
    content=await get_external_data.get_web_data(authority_url)