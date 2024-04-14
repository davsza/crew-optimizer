from dotenv import load_dotenv, find_dotenv
import os
import pprint
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://davidszabolcs115:{password}@cluster0.ao8jbfi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(connection_string)

dbs = client.list_database_names()
test_db = client.testdb
collections = test_db.list_collection_names()  # table
print(collections)


def insert_test_document():
    collection = test_db.testcollection
    test_user = {
        "name": "Test",
        "email": "test@mail.com",
        "password": "test123"
    }
    inserted_id = collection.insert_one(test_user).inserted_id
    print(inserted_id)


insert_test_document()

production = client.production
person_collection = client.person_collection
