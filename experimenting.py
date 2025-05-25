# pylint: disable-all
import asyncio
import urllib.request
from typing import Optional
from nanoid import generate
from bson import DBRef

#import requests
import json
import os
import orjson
import pprint 
import pickle
from rich import print
from lxml import etree
import marcalyx
#import logging
import aiohttp
import pytest
import pytest_asyncio
from beanie import Document, Link, WriteRules
import re
from dotenv import load_dotenv
from pydantic_core import from_json
from unittest import mock

import book_ingest_create_records
import get_external_data
import parse_iiif
import db_actions
#import main as app
import classes
#import ingest_person
#import parse_manifests
#import test_get_external_data
#import parse_date_1
#import parse_date
#import main as app_main
#import book_ingest_create_records

#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

load_dotenv()

#@classes.func_logger
#@mock.patch('get_external_data.get_web_data_as_json', side_effect=test_get_external_data.mock_get_web_data_as_json)
#@pytest.mark.asyncio
async def main():
    
    classes.logger.debug(" DEBUG   Hello world")
#    os.environ["MONGODB_HOST"] = "localhost"
#    os.environ["MONGODB_PORT"] = "27017"
    
    await db_actions.initialise_beanie()
    e=classes.Entity()
    a=classes.Attribute()
    a.key="test"
    a.value="test_value"
    e.attributes.append(a)
    print(e)

    print(e.get_attribute("test"))

    eac=classes.EntityAndConnections(name="eac")
    r=classes.EntityAndConnections(name="r")

    eac.connections.append(r)
    print(eac)
    await r.save()
    await eac.save()
#     p=classes.Entity(type="Person",name="person")
# #    await p.save()
#     b=classes.Entity(type="Book",name="book")
#  #   await b.save()

#     ec=classes.EntityConnection()
#     ec.entityA=b
#     ec.entityB=p
#  #   await ec.save()

#     r = await db_actions.get_all_resources_from_db()
# #    print(r)
    
#     r = classes.Entity.find(classes.Entity.type=="Book",fetch_links=True)
#     print(await r.to_list())

#     e1=classes.Entity(type="Person",name="a")
# #    await e1.save()
#     e2=classes.Entity(type="Person",name="b")
#     e2.linkedEntity=e1
# #    await e2.save()


# #    r = classes.EntityConnection.find(class
# # es.EntityConnection.entity.gnd_id == "118795295", fetch_links=True)
# #    classes.E
# #    print(await r.to_list())
# #    print(marc)
# #    iiif_url="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
# #    url = iiif_url
# #    r = await get_external_data.get_web_data_as_json(iiif_url)


# #    print(type(r))
#     #print(r)
#    r = await classes.webCall.find(classes.webCall.url == url).to_list()
#    print(r)
#    if r[0]:
#        content=r[0].content
#    await run_parse_iiif()
#    id="6707748eb64a43e946737251"
#    m = await classes.Person.get(id,fetch_links=True)
#    print(m)
#    await book_ingest_create_records.metadata_dissection(m)
#    if (1==2):



async def run_parse_iiif():
    iiif_url="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    material="book"
    r = await parse_iiif.parse_iiif(iiif_url,material)
    response = await r.save(link_rule=WriteRules.WRITE)
    return response

asyncio.run(main())