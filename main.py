from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json 
from iiifparse import *
from dbactions import *
from classes import *
from nanoid import generate
   
   


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
    return {"message": "Hello World"}
    
@app.get("/getMetadata")
async def getMetadata(iiifUrl):
    print(iiifUrl)
    url = urllib.request.urlopen(iiifUrl)
    manifest = url.read()
    print(manifest)
    m=iiifparse(manifest)
    m.iiifUrl=iiifUrl
    m.manifest=manifest
    m.id=generate()
    print(m)
    return (m) 

@app.post("/createNewRessource")
async def createNewRessource(metadata: Metadata):
    m = metadata
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