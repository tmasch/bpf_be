"""
This module contains all functions that contain database actions, like
creating new records, reading from the DB etc.

There should be no business logic here.
"""

import json
import os
from nanoid import generate
from pymongo import MongoClient
from beanie import init_beanie
import motor.motor_asyncio

import exp_classes
import person_relations



MONGO_CLIENT=None

@exp_classes.async_func_logger
async def initialise_beanie():
    mongo_db_database_name = "bpf"
    mongo_host = os.getenv('MONGODB_HOST', '')
    endpoint = f"mongodb://{mongo_host}"
    motor_client = motor.motor_asyncio.AsyncIOMotorClient(endpoint)
    database = motor_client[mongo_db_database_name]
    await init_beanie(database=database, document_models=[exp_classes.Union, exp_classes.Node, exp_classes.Edge, exp_classes.NodePlus])

@exp_classes.func_logger
def get_database():
    """
    Method to get the database connection
    """
    global MONGO_CLIENT
    if bool(MONGO_CLIENT):
        return MONGO_CLIENT['bpf']
    mongo_host = os.getenv('MONGODB_HOST', '')
    print("host",mongo_host)
    print(os.getenv('MONGODB_PORT', ''))
    mongo_port = int(os.getenv('MONGODB_PORT', ''))
    print("port",mongo_port)
    endpoint = f"mongodb://{mongo_host}"
    print("endpoint",endpoint)
    MONGO_CLIENT = MongoClient(host=endpoint,port=mongo_port,connectTimeoutMS=1000,timeoutMS=1200)
    print(MONGO_CLIENT)
    print("databases",MONGO_CLIENT.list_database_names())
#    await init_beanie(database=mongo_client.bpf, document_models=[classes.Metadata,classes.Person,classes.OrganisationDb,classes.BookDb])
    return MONGO_CLIENT['bpf']
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    # client = MongoClient('localhost', 27017)
    # Create the database for our example (we will use the same database throughout the tutorial
#   return client['bpf']


