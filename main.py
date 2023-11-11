from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json 
import iiifparse
from dbactions import *
from classes import *
from imageActions import *
from nanoid import generate
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()
import gndparse
import book_ingest_create_records


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

print(get_database())
#getAllRessourcesFromDb()

app = FastAPI()

origins = [
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
    return {"message": "Hello World port"+os.getenv('MONGODB_PORT', '')+" end port"}
    
@app.get("/getMetadata")
async def getMetadata(iiifUrl, material):
    print("iiifURL: ")
    print(iiifUrl)
    m = iiifparse.iiifparse(iiifUrl)
    m.material = material
#    print(iiifUrl)
#    url = urllib.request.urlopen(iiifUrl)
#    manifest = url.read()
#    print(manifest)
#    m=iiifparse(manifest)
#    m.iiifUrl=iiifUrl
#    m.manifest=manifest
    if m.bibliographic_information:
        for person in m.bibliographic_information[0].persons:
            person = gndparse.person_identification(person)
        #  m.bibliographic_information[0].persons[person_counter] = person
        for organisation in m.bibliographic_information[0].organisations:
            organisation = gndparse.organisation_identification(organisation)
        for place in m.bibliographic_information[0].places:
            place = gndparse.place_identification(place)
    for repository in m.repository:
        repository = gndparse.organisation_identification(repository) # I had to define 'repository' as a list because Pydantic forced me to do so, but it only has one member. 
    m.id=generate()
#    print(m)
    return (m) 

@app.get("/callAdditionalBibliographicInformation")
async def supply_biblio_information(additional_bid):
    bi = iiifparse.supply_bibliographic_information(additional_bid)
    for person in bi.persons:
        person = gndparse.person_identification(person)
    for organisation in bi.organisations:
        organisation = gndparse.organisation_identification(organisation)
    for place in bi.places:
        place = gndparse.place_identification(place)

    print(Bibliographic_id)
    print(bi)
    return (bi)

    
@app.get("/loadNewPersonAuthorityRecord")
async def load_new_person_authority_record(new_authority_id, new_person_role):
    print(new_authority_id)
    print(new_person_role)
#    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id + r'%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100'
#    potential_person = gndparse.gnd_parsing_person(authority_url)
    potential_person = gndparse.additional_person_identification(new_authority_id, new_person_role)
    print(potential_person)
    return(potential_person)

@app.get("/loadNewOrganisationAuthorityRecord")
async def load_new_organisation_authority_record(new_authority_id_org):
#    print(new_authority_id_org)
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id_org + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
    potential_organisation = gndparse.gnd_parsing_organisation(authority_url)
#    print(potential_organisation)
    return(potential_organisation)

@app.get("/loadNewPlaceAuthorityRecord")
async def load_new_place_authority_record(new_authority_id_place):
#    print(new_authority_id_place)
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id_place + r'%20and%20BBG%3DTg*&recordSchema=MARC21-xml&maximumRecords=100'    
    potential_place = gndparse.gnd_parsing_place(authority_url)
    return(potential_place)


@app.get("/loadNewRepositoryAuthorityRecord")
async def load_new_repository_authority_record(new_authority_id_rep):
#    print(new_authority_id_rep)
    authority_url = r'https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=NID%3D' + new_authority_id_rep + r'%20and%20BBG%3DTb*&recordSchema=MARC21-xml&maximumRecords=100'
    potential_organisation = gndparse.gnd_parsing_organisation(authority_url)
#    print(potential_organisation)
    return(potential_organisation)



@app.post("/createNewRessource")
async def createNewRessource(metadata: Metadata):
    print("hello world")
    m = metadata
#    print(m)
    insertMetadata(m)
#    print(m)
    return(m)

@app.post("/saveConnectedRecords")
async def saveConnectedRecords(metadata: Metadata):
    print("hello world")
    m = metadata
    print(m)
    book_ingest_create_records.metadata_dissection(m)
    #print(m)
    return(m)


@app.get("/allRessources", response_model=List[Metadata]) 
async def getAllRessources():
    r=getAllRessourcesFromDb()
    return(r)
    
@app.get("/ressource", response_model=Metadata)
async def getRessource(id: str):
    print(id)
    r=getRessourceFromDb(id)
    return(r)
    
@app.get("/findImages")    
async def findImages(id: str):
    print(id)
    r=findImages(id)
    