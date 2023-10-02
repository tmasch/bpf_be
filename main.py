from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json 
from iiifparse import *
from dbactions import *
from classes import *
from nanoid import generate
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
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
async def getMetadata(iiifUrl):
    m = iiifparse(iiifUrl)
#    print(iiifUrl)
#    url = urllib.request.urlopen(iiifUrl)
#    manifest = url.read()
#    print(manifest)
#    m=iiifparse(manifest)
#    m.iiifUrl=iiifUrl
#    m.manifest=manifest
    m.id=generate()
    print(m)

    return (m) 

@app.post("/createNewRessource")
async def createNewRessource(metadata: Metadata):
    print("hello world")
    m = metadata
    print(m)
    insertMetadata(m)
    print(m)
    return("Hello World")
    
@app.get("/allRessources", response_model=List[Metadata]) 
async def getAllRessources():
    r=getAllRessourcesFromDb()
    return(r)
    
@app.get("/ressource", response_model=Metadata)
async def getRessource(id: str):
    print(id)
    r=getRessourceFromDb(id)
    return(r)