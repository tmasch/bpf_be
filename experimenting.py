#pylint: disable=C0301, C0303, C0116, C0325, C0103, C0114, C0304
import asyncio
import urllib.request
from typing import Optional

from beanie import Document, Link
#import requests
import json
import orjson
import os
import pickle
import pprint 
import logging
import aiohttp
import re
from dotenv import load_dotenv
from pydantic_core import from_json
from unittest import mock

import get_external_data
import parse_iiif
import db_actions   
#import main as app
import classes
#import ingest_person
import parse_manifests
import test_get_external_data
import parse_date_1
import parse_date

logger = logging.getLogger(__name__)

load_dotenv()


@classes.func_logger
#@mock.patch('get_external_data.get_web_data_as_json', side_effect=test_get_external_data.mock_get_web_data_as_json)
async def main():
    logging.basicConfig(level=logging.INFO)
#    os.environ["MONGODB_HOST"] = "localhost"
#    os.environ["MONGODB_PORT"] = "27017"
    
#    await db_actions.initialise_beanie()
#    external_id = classes.ExternalId()
#    external_id.name = "viaf"
#    external_id.id = "128386719"
#        person_selected = person.potential_candidates[person.chosen_candidate]


#        for connected_person in person_selected.connected_persons:
    #for external_id in connected_person.external_id:
#                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
#    person_found = db_actions.find_person(external_id,"external_id")
#        person_found = collection.find_one({"external_id": {"$elemMatch": {"name": person.id_name, "id": person.id}}}, {"id": 1, "person_type1": 1, "name_preferred": 1})
#    person_found = db_actions.find_person(person,"external_id")
#    print(person_found)
#    r = await classes.PersonDb.find_one(classes.PersonDb.external_id.id == external_id.id 
#                              and classes.PersonDb.external_id.name == external_id.name)
#    r=r.project(classes.PersonDb)
#    rr=classes.PersonDb()
# #   rr=r
#    print(r)
#    schoeffer_json='{"id":"","id_name":"","internal_id":"","internal_id_person_type1":[],"internal_id_person_type1_needed":"Printer","internal_id_person_type1_comment":"","internal_id_preview":"","name":"Peter Schoeffer","role":"prt","chosen_candidate":0,"potential_candidates":[{"external_id":[{"uri":"https://d-nb.info/gnd/118609947","name":"GND","id":"118609947"}],"internal_id":"","internal_id_person_type1":[],"internal_id_person_type1_comment":"","name_preferred":"Schöffer, Peter","name_variant":["Schöffer, Peter (der Ältere)","Peter (Schöffer)","Schoeffer, Peter","Schöffer, Petrus","Scheffer, Peter","Scheffer, Petrus","Schoffer, Petrus","Schoiffer, Petrus","Schoyffer, Petrus","Schoiffer de Gernheym, Petrus","Gernheym, Petrus Schoiffer de","Schoyffer de Gernheym, Petrus","Gernheym, Petrus, Schoyffer de","Gernssheym, Petrus","Schoiffer de Gernßhem, Petrus","Gernßhem, Petrus Schoiffer de"],"sex":"male","dates_from_source":[{"datestring_raw":"1420-1502","date_comments":"","datetype":"datl","datestring":"","date_start":[],"date_end":[],"date_aspect":""}],"datestring":"","date_start":[],"date_end":[],"date_aspect":"","connected_persons":[{"id":"","external_id":[{"uri":"https://d-nb.info/gnd/118795295","name":"GND","id":"118795295"}],"name":"Schöffer, Peter","connection_type":"bezf","connection_comment":"Sohn","connection_time":""}],"connected_organisations":[],"connected_locations":[{"id":"","external_id":[{"uri":"https://d-nb.info/gnd/4020399-2","name":"GND","id":"4020399-2"}],"name":"Gernsheim","connection_type":"ortg","connection_comment":"","connection_time":""},{"id":"","external_id":[{"uri":"https://d-nb.info/gnd/4037124-4","name":"GND","id":"4037124-4"}],"name":"Mainz","connection_type":"ortw","connection_comment":"","connection_time":"1457-1502"}],"comments":"Dt. Druckerverleger, Mitarbeiter und fähigster Schüler Gutenbergs. - Aus Germsheim, studierte an der Universität Paris und kam 1452 nach Mainz. Stand im Streit zwischen Fust und Gutenberg auf Seiten Fusts; mit seiner Hilfe konnte Fust den Betrieb weiterführen. Während Schöffer die Druckerei leitete, besorgte Fust den Buchhandel. Nach Fusts Tod 1466 heiratete Schöffer Fusts Tochter Christine und wurde dadurch neben anderen Erben Fusts Mitbesitzer des Unternehmens.; Drucker; Buchdrucker; Verleger","preview":"Schöffer, Peter (1420-1502), born in Gernsheim, active in Mainz, also called: Schöffer, Peter (der Ältere); Peter (Schöffer); Schoeffer, Peter; Schöffer, Petrus; Scheffer, Peter; Scheffer, Petrus; Schoffer, Petrus; Schoiffer, Petrus; Schoyffer, Petrus; Schoiffer de Gernheym, Petrus; Gernheym, Petrus Schoiffer de; Schoyffer de Gernheym, Petrus; Gernheym, Petrus, Schoyffer de; Gernssheym, Petrus; Schoiffer de Gernßhem, Petrus; Gernßhem, Petrus Schoiffer de (Dt. Druckerverleger, Mitarbeiter und fähigster Schüler Gutenbergs. - Aus Germsheim, studierte an der Universität Paris und kam 1452 nach Mainz. Stand im Streit zwischen Fust und Gutenberg auf Seiten Fusts; mit seiner Hilfe konnte Fust den Betrieb weiterführen. Während Schöffer die Druckerei leitete, besorgte Fust den Buchhandel. Nach Fusts Tod 1466 heiratete Schöffer Fusts Tochter Christine und wurde dadurch neben anderen Erben Fusts Mitbesitzer des Unternehmens.; Drucker; Buchdrucker; Verleger)"}],"new_authority_id":""}'
#    print(schoeffer_json)
#    print("importing json")
#    p=classes.Person()
#    p.model_validate_json(schoeffer_json)
#    print(p)
#    print("string")

#user_dict = json.loads(json_raw)
#user = User(**user_dict)
#    d = json.loads(schoeffer_json)
#    p = classes.Person(**d)
#    print(p)
#    pp = await ingest_person.ingest_person(p)



#    uri_entered="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
#    m= await get_external_data.get_web_data_as_json(uri_entered)
#    await parse_iiif.parse_iiif(uri_entered,"b")
#    m=classes.Metadata()
#§    m=await app.get_metadata(uri_entered,"b")
#    m="asdf"    
#    m.model_dump_json()
#    print(m.model_dump_json())
#    json.dumps(m)
#    f = open("herbarius_metadata.json","w")
#    json.dump(m,f)
#    f.close()
#    print(type(m))

#    f = open("herbarius_metadata.json","r")
#    m = f.read()
#    print(m)
#    m=json.load(f)
#    m=json.load(f)
#    print(m)
#    manifest = classes.Metadata(**m)
#    manifest=m
#    print("PRINTING MANIFEST")
#    print(manifest)
#    parse_manifests.parse_manifests_bsb(manifest)

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
#    url_search_list=["https://viaf.org/viaf/sourceID/DNB%7C040203999"]
#    async with aiohttp.ClientSession() as session:
#        results = await asyncio.gather(*(get_viaf_header(session, url) for url in url_search_list))
#    viaf_urls_dict = dict(zip(url_list, results))
#    t=classes.PagesDb()
#    manifest= await get_external_data.get_web_data_as_json(uri_entered)

#    uri_entered="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
#    r= await parse_iiif.parse_iiif(uri_entered,"b")
#    print(r)
#    f = open("datetest.txt","r")
#    m = f.read()
#     d="29.02.1456-zwischen 10.09. und Oktober 1527"
#     d=d.lower()
#     dd=parse_date_1.get_date_aspect(d)
#     dd=re.sub("\d","",dd)
# #            dd=parse_date_1.remove_tags(dd)
# #            r=parse_date.parse_date_range(d)
#     print(dd,end="\n")
# #           
    if 1==1:

        f = open("date_results.txt","w")

        l=0
        succ=0
        succ_indiv=0
        filename="datestest.txt"
        with open(filename) as file:
            for line in file:
                l=l+1
    #            print(line)
                d=line.rstrip()
#                print(line.rstrip(),end=" ")
 #               d=d.lower()
#                dd=parse_date_1.get_date_aspect(d)
    #            dd=re.sub("\d","",dd)
                #dd=parse_date_1.remove_tags(dd)
                if not re.match("oder",d):
                    ddd=parse_date.parse_date_overall(d,"","")

                r=parse_date_1.parse_date_range(d)
#                print(dd,end=" ")
                if(r.state=="FAIL"):
                    print("Line ",end=" ")
                    print(l,end=" ")
                    print(d)
                    print(ddd)
                    print(r)
                
                f.write(d)
                f.write(" ")
                f.write("\n")
                f.write(r.model_dump_json())
                f.write("\n")
                if r.state == "SUCCESS":
                    if r.start.state == "SUCCESS":
                        succ_indiv=succ_indiv+1
                    if r.end.state == "SUCCESS":
                        succ_indiv
    #                print("SUCCESS")
    #                print(d)
    #                print(r.start)
    #                print(r.end)
                    succ=succ+1
        print("Successes:")
        print(succ,succ/l)
        print("Individual Successes:")
        print(succ_indiv,succ_indiv/l/2)

    d="-18.04.1605"
    d="09.07.1867-XX.XX.19XX"
    d="29.02.1456-zwischen 10.09. und Oktober 1527"
 #   d="0X.02.1825-05.08.1895"
 #   d="1. Drittel 20. Jh."
 #   d="ca. 20. - 21. Jh."
    d="2. h. 17. Jh."
#    print(d)
    #d="1234-1234"
#    print(d)
    r=parse_date_1.parse_date_range(d)
#    print(r)

#    r=parse_date.parse_date_overall(d,"","")
#    print(r)


async def url_test(uri_entered):
    d=await get_external_data.get_web_data_as_json(uri_entered)
    print("type of return from external_data")
    print(type(d))
    url = urllib.request.urlopen(uri_entered)
    ds=url.read()
    print("type of urllib result")
    print(type(ds))





asyncio.run(main())