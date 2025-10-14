#pylint: disable=C0301, C0303, C0116, C0325, C0103, C0114, C0304
"""
This module collects functions that obtain data from external webpages
"""

import json
import urllib.request
import xml.etree.ElementTree
#import logging
import asyncio
import aiohttp
import requests

from . import classes
from . import parse_artist_record
from . import parsing_helpers


#logger = logging.getLogger(__name__)


@classes.async_func_logger
async def get_web_data_as_json(url):
    """
    Do a web call and returns a json object
    """
    url = url.replace(" ", "%20")
    content = await get_web_data(url)
    result = json.loads(content)
    return result


@classes.async_func_logger
async def get_web_data(url_in):
    """
    Do a web call and return byte object
    """
    print("searching for")
    print(url_in)
    r = await classes.WebCall.find(classes.WebCall.url == url_in).to_list()
    if len(r) > 0:
        print("found content in database")
        content=r[0].content
    else:
        print("making web call")
        response = requests.get(url_in)
        content = response.content
        print(type(content))
        wc = classes.WebCall(url=url_in,content=content)
        await wc.save()
    return content


@classes.async_func_logger
async def get_viaf_header(session, url):
    # This is a short programme I received from Gregor Dick. Together with a gather funciton i
#    async with session.head(url, allow_redirects=False) as response:
    print(url)
    async with session.head(url) as response:
        # Wait for the start of the response.
        await response.read()
#        print("result: ")
#        print(response)
#        print
#        print(response.read())
        f = open("requests.txt","a")
        f.write("------------------------\n")
        f.write("WEB CALL get_viaf_header\n")
        f.write("REQUEST\n")
        f.write("url: "+url)
        f.write("\nRESPONSE HEADER\n")
#        data = await response.json()
#        type(data)
#        f.write(data)
#        f.write(response.read())
        f.write("\n------------------------\n")
        f.close()

        if "Location" in response.headers:
            return response.headers["Location"]
        else:
            return ""


@classes.async_func_logger
async def get_viaf_from_authority(url_list):
    # This function the URL of an authority file (currently GND and ULAN) and returns an External_id object
    # It will be used numerous times for 'stitching' records together
    #    print("URL as it arrives in get_viaf_from_authorty")
    #    print(url)
    url_search_list = []
    identifier = ""
    url_list = list(dict.fromkeys(url_list))  # this shoudl remove duplicates
    for url in url_list:
        print("URL to be sent for transformation into VIAF ID")
        #        print("List: ")
        #        print(url_list)
        #        print("single url")
        #        print(url)
        if r"/gnd/" in url:
            identifier = "DNB%7C" + url[22:]
        #            print("URI comes from GND")
        #            print(identifier)
        elif (
            r"vocab.getty.edu/page/ulan/" in url
        ):  # I am not sure if this exists, but I leave it just in case
            identifier = "JPG%7C" + url[33:]
        elif r"vocab.getty.edu/ulan/" in url:
            identifier = "JPG%7C" + url[28:]
        elif (
            r"GND_intern" in url
        ):  # This is an intern ID of the GND that cannot be used to create proper URLs - it is necessary as log as VIAF cannot read the external ID
            identifier = "DNB%7C" + url[10:]
        if identifier != "":
            url_search = r"https://viaf.org/viaf/sourceID/" + identifier
            #            print("url sent off: ")
            #            print(url_search)
            url_search_list.append(url_search)

    #    print(url_list)
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(get_viaf_header(session, url) for url in url_search_list))
    viaf_urls_dict = dict(zip(url_list, results))

    return viaf_urls_dict


@classes.func_logger
def transform_gnd_id_with_hyphen(id_with_hyphen):
    # This module is temporarily needed to replace those GND IDs of organisations and places that contain a hyphen with the internal ID of the GND that can be searched in VIAF
    # (there is a bug in VIAF preventing searches for hyphens, hence there is need for this module unless it is fixed)
    # input is merely the ID number, output is an object of the class External_id that is then added to the record.
    authority_url = (
        r"https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D"
        + id_with_hyphen
        + r"&recordSchema=MARC21-xml&maximumRecords=100"
    )
    classes.logger.info("Calling " + authority_url)
    url = urllib.request.urlopen(authority_url)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    for record in root[2]:
        print("Getting internal id")
        for step1 in record[2][0]:
            match step1.get("tag"):
                case "001":
                    record_id = classes.ExternalReference()
                    record_id.name = "GND_intern"
                    record_id.id = step1.text
                    record_id.uri = "GND_intern" + step1.text
                    print("ID as produced by transform_gnd_id_with_hyphen")
                    print(record_id)
    return record_id


@classes.async_func_logger
async def search_ulan(person):
    """
    \todo
    """
    person_name_search = person.name
    for old, new in parsing_helpers.url_replacement.items():
        person_name_search = person_name_search.replace(old, new)
    authority_url = (
        r"https://vocab.getty.edu/sparql.json?query=select%20distinct%20%3Fartist_id%20%7B%0A%20%7B%3FSubject%20luc%3Aterm%20%22"
        + person.name
        + r"%22%3B%20skos%3AinScheme%20ulan%3A%20%3B%20a%20%3Ftyp%3B%20gvp%3AprefLabelGVP%20%5Bxl%3AliteralForm%20%3FTerm%5D%7D"
        + r"%20union%20%7B%3FSubject%20luc%3Aterm%20%22"
        + person.name
        + r"%22%3B%20skos%3AinScheme%20ulan%3A%20%3B%20a%20%3Ftyp%3B%20xl%3AaltLabel"
        + r"%20%5Bxl%3AliteralForm%20%3FTerm%5D%7D%0A%20%20%3Ftyp%20rdfs%3AsubClassOf%20gvp%3ASubject%3B%20rdfs%3Alabel%20%3FType.%0A%20filter"
        + r"%20(%3Ftyp%20!%3D%20gvp%3ASubject)%20%0A%20optional%20%7B%3FSubject%20gvp%3AparentString%20%3FType2%7D%0A%20filter%20(%3FType2%20!%3D%20"
        + r"%22Unidentified%20Named%20People%20and%20Firms%22)%20%0A%20optional%20%7B%3FSubject%20dc%3Aidentifier%20%3Fartist_id%7D%7D%0AORDER%20BY%20"
        + r"(fn%3Alower-case(str(%3FTerm)))%0A&toc=Finding_Subjects&implicit=true&equivalent=false&_form=/queriesF"
    )
    ulan_list_raw = requests.get(authority_url, timeout=10)
    ulan_list = ulan_list_raw.json()
    ulan_url_list = []
    if "results" in ulan_list:
        list_results = ulan_list["results"]
        if "bindings" in list_results:
            bindings = list_results["bindings"]
            for artist in bindings:
                artist_id = artist["artist_id"]["value"]
                artist_authority_url = (
                    r"https://vocab.getty.edu/ulan/" + artist_id + r".json"
                )
                ulan_url_list.append(artist_authority_url)
            print(ulan_url_list)
            async with aiohttp.ClientSession() as session:
                results = await asyncio.gather(
                    *(get_viaf_header(session, url) for url in ulan_url_list)
                )
            #                print("results")
            #                print(results)
            #                print(len(results))
            for result in results:
                candidate = parse_artist_record.parse_artist_record(result)
                #                print("candidate identified: ")
                #                print(candidate)
                # authority_url_list.append(artist_authority_url)
                person.potential_candidates.append(candidate)
                # print("candidate appended, now" + str(len(person.potential_candidates)) + "candidates")

    return person
