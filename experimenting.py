#pylint: disable=C0301, C0303, C0116, C0325, C0103, C0114, C0304
import asyncio
import urllib.request
#import requests
import json
import orjson
import os
import pickle
import pprint 
import logging

import classes
import get_external_data
import parse_iiif
import db_actions
import main as app
logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    os.environ["MONGODB_HOST"] = "localhost"
    
    await db_actions.initialise_beanie()

    uri_entered="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    await parse_iiif.parse_iiif(uri_entered,"b")
#    m=classes.Metadata()
#    m=await app.get_metadata(uri_entered,"b")
#    m="asdf"    
#    m.model_dump_json()
#    print(m.model_dump_json())
#    json.dumps(m)
#    f = open("herbarius_metadata.json","w")
#    f.write(m.model_dump_json())
#    print(type(m))

#    f = open("herbarius_metadata.json",)


#    with open('herbarius_metadata.pkl', 'wb') as f: 
#        pickle.dump([m], f)

#    with open('herbarius_metadata.pkl', 'rb') as f:
#        m = pickle.load(f)
    
#    print("pretty printing")
#    print(m)
#    print(type(m))
#    mm=classes.Metadata(m)
#    pprint.pp(m)
#    m.bibliographic_information[0]



async def url_test(uri_entered):
    d=await get_external_data.get_web_data_as_json(uri_entered)
    print("type of return from external_data")
    print(type(d))
    url = urllib.request.urlopen(uri_entered)
    ds=url.read()
    print("type of urllib result")
    print(type(ds))





asyncio.run(main())