#pylint: disable=C0301
"""
\todo refactor to follow naming conventions!

"""
#import urllib.request
#import json
import os
from typing import List
#from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from nanoid import generate

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import iiif_parse
import db_actions
import classes
import image_actions
import gndparse
import book_ingest_create_records
import displayRecords

load_dotenv()

#class Settings(BaseSettings):
#    class Config:
#        env_file = '.env'
#        env_file_encoding = 'utf-8'


#settings = Settings()
#for name, value in os.environ.items():
#    print("{0}: {1}".format(name, value))
#print("MONGODB")
#print( os.getenv('MONGODB_HOST', ''))
#print( os.getenv('MONGODB_PORT', ''))
#print("Settings")
#print(settings.dict())
#print(settings.MONGODB_PORT)

print(db_actions.get_database())
#getAllRessourcesFromDb()

app = FastAPI()

origins = [
    "*",
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    """
    Main method doing nothing
    """
    return {"message": "Hello World port"+os.getenv('MONGODB_PORT', '')+" end port"}

@app.get("/getMetadata")
async def get_metadata(iiif_url, material):
    """
    Method returning metadata for a given iiif url
    """
    print("iiif URL: "+iiif_url)
    print("material: "+material)
    m = iiif_parse.iiif_parse(iiif_url, material)
    #m.material = material
#    print(iiifUrl)
#    url = urllib.request.urlopen(iiifUrl)
#    manifest = url.read()
#    print(manifest)
#    m=iiifparse(manifest)
#    m.iiifUrl=iiifUrl
#    m.manifest=manifest
    if m.bibliographic_information:
        if m.bibliographic_information[0]:
            #print("m.bibliographic_information: ")
            #print(m.bibliographic_information)
            for person in m.bibliographic_information[0].persons:
                person = await gndparse.person_identification(person)
            #  m.bibliographic_information[0].persons[person_counter] = person
            for organisation in m.bibliographic_information[0].organisations:
                organisation = gndparse.organisation_identification(organisation)
            for place in m.bibliographic_information[0].places:
                place = gndparse.place_identification(place)
    for repository in m.repository:
        repository = gndparse.organisation_identification(repository)
        # I had to define 'repository' as a list because Pydantic forced me to do so,
        #  but it only has one member.
        repository.role = "col"
        # Normally, this role depends on the bibliographical data -
        # in this case, it has to be set here.

    m.id=generate()
#    print("List of places to be sent to FE")
#    print(m.bibliographic_information[0].places)
    return m

@app.get("/callAdditionalBibliographicInformation")
async def supply_biblio_information(additional_bid):
    """
    Method returning additional bibliographic information
    """
    bi = iiif_parse.supply_bibliographic_information(additional_bid)
    for person in bi.persons:
        person = await gndparse.person_identification(person)
    for organisation in bi.organisations:
        organisation = gndparse.organisation_identification(organisation)
    for place in bi.places:
        place = gndparse.place_identification(place)

#    print(BibliographicId)
    print(bi)
    return bi

@app.get("/loadNewPersonAuthorityRecord")
async def load_new_person_authority_record(new_authority_id, new_person_role):
    """"
    Method to find???
    """
    print(new_authority_id)
    print(new_person_role)
#    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&
# operation=searchRetrieve&query=NID%3D'
# + new_authority_id + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
#    potential_person = gndparse.gnd_parsing_person(authority_url)
    potential_person = gndparse.additional_person_identification(new_authority_id, new_person_role)
    print(potential_person)
    return potential_person

@app.get("/loadNewOrganisationAuthorityRecord")
async def load_new_organisation_authority_record(new_authority_id_org, new_organisation_role):
    """
    Endpoint
    """
#    print(new_authority_id_org)
#    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&
# operation=searchRetrieve&query=NID%3D'
#  + new_authority_id_org + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml
# &maximumRecords=100'
#    potential_organisation = gndparse.gnd_parsing_organisation(authority_url)
    potential_organisation = \
        gndparse.additional_organisation_identification(new_authority_id_org, new_organisation_role)
#    print(potential_organisation)
    return potential_organisation

@app.get("/loadNewPlaceAuthorityRecord")
async def load_new_place_authority_record(new_authority_id_place, new_place_role):
    """
    Endpoint
    """
#    print(new_authority_id_place)
#    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&
# operation=searchRetrieve&query=NID%3D' + new_authority_id_place +
#  r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'
#    potential_place = gndparse.gnd_parsing_place(authority_url)
    potential_place = \
        gndparse.additional_place_identification(new_authority_id_place, new_place_role)
    print("potential place to be sent to FE")
    print(potential_place)
    return potential_place


@app.get("/loadNewRepositoryAuthorityRecord")
async def load_new_repository_authority_record(new_authority_id_rep):
    """
    Endpoint
    """
#    print(new_authority_id_rep)
    new_authority_id_rep = new_authority_id_rep.strip()
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id_rep + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
    potential_organisation = gndparse.gnd_parsing_organisation(authority_url)
#    print(potential_organisation)
    return potential_organisation

@app.post("/submitAdditionalInformation")
async def submit_additional_information(making_processes: list[classes.MakingProcess]):
    """
    Endpoint 
    """
    print(making_processes)
    making_processes = await gndparse.making_process_identification(making_processes)
    print("The following is sent back: ")
    print(making_processes)
    return making_processes

@app.post("/createNewResource")
async def create_new_resource(metadata: classes.Metadata):
    """
    Endpoint to create a new resource in the database
    """
    m = metadata
    db_actions.insert_metadata(m)
    return m


@app.post("/createImageRecord")
async def create_image_record_endpoint(coords: classes.Frame):
    """
    Endpoint for creating a new image record in the database given the coordinates
    """
    print("index",coords.index)
    print("x position",coords.x_abs)
    print("y position",coords.y_abs)
    print("width",coords.w_abs)
    print("height",coords.h_abs)
    print("Saving image as file")
    image_actions.save_image_file(coords)
    db_actions.create_image_record()
    return

@app.post("/saveConnectedRecords")
async def save_connected_records(metadata: classes.Metadata):
    """
    \todo not quite clear what connected records should be
    """
    print("hello world")
    m = metadata
    print("Repository in main.py: ")
    print(m.repository)
    ingest_result = await book_ingest_create_records.metadata_dissection(m)
    #print(m)
    return ingest_result

@app.get("/allResources", response_model=List[classes.PreviewListDb])
async def get_all_resources():
    """
    Endpoint to get all resources from the database
    """
    r=db_actions.get_all_resources_from_db()
    print(r)
    return r

@app.get("/resource", response_model=classes.Metadata)
async def get_resource(identifier: str):
    """
    Endpoint to get a specific ressource from the database
    \todo use this endpoint together with a qualifier to get any record!
    """
    print("Getting resource")
    print(identifier)
    r=db_actions.get_resource_from_db(identifier)
    return r

@app.get("/findImages")
async def find_all_images(identifier: str):
    """
    Endpoint to start the image finding/extraction process for a ressource
    """
    print(identifier)
    print("starting")
    r=image_actions.find_images(identifier)
    print(r)
    return

@app.get("/getBookRecord", response_model = classes.BookDbDisplay)
async def get_book_record(identifier: str):
    """
    \todo move to get_resource
    """
    print("arrived in get book record")
    book_record = displayRecords.getBookRecord(identifier)
    print("bookrecord before returning from main.py: ")
    print(book_record)
    return book_record

@app.get("/getManuscriptRecord", response_model = classes.ManuscriptDbDisplay)
async def get_manuscript_record(identifier: str):
    """
    \todo move to get_resource    
    """
    manuscript_record = displayRecords.getManuscriptRecord(identifier)
    print("manuscriptkrecord before returning from main.py: ")
    print(manuscript_record)
    return manuscript_record


@app.get("/getPersonRecord", response_model = classes.PersonDbDisplay)
async def get_person_record(identifier: str):
    """
    \todo move to get_resource    
    """
    print("Person record request arrived in BFF")
    person_record = displayRecords.getRecord(identifier)
    print("Person record sent off from BFF")
    return person_record

@app.get("/getOrgRecord", response_model = classes.OrgDbDisplay)
async def get_org_record(identifier: str):
    """
    \todo move to get_resource    
    """
    print("Person record request arrived in BFF")
    org_record = displayRecords.getRecord(identifier)
    print("Person record sent off from BFF")
    return org_record

@app.get("/getPlaceRecord", response_model = classes.PlaceDbDisplay)
async def get_place_record(identifier: str):
    """
    \todo move to get_resource  
    """
    print("Person record request arrived in BFF")
    place_record = displayRecords.getRecord(identifier)
    print("Person record sent off from BFF")
    return place_record
