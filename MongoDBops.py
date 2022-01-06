import pymongo
from pymongo import MongoClient


class DBops:

    def __init__(self, username, password):
        try:
            self.username = username
            self.password = password
            self.url = f"mongodb+srv://{self.username}:{self.password}@cluster0.paodh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        except Exception as e:
            raise Exception(f"(__init__): Something went wrong on initiation process\n" + str(e))

    def getMongoDBClientObject(self):
        """
        Connect to mongoDB cluster
        """
        try:
            client = MongoClient(self.url)
            return client
        except Exception as e:
            raise Exception(f"(getMongoDBClientObject): Something went wrong while creating client object \n{e}")

    def insertDoc(self, dic):
        try:
            cluster = self.getMongoDBClientObject()
            db = cluster["Wiki-scraper"]
            collection = db["test"]
            collection.insert_one(dic)
        except Exception as e:
            print(f"Error {e} insert records in database")

    def findDocument(self, name):
        cluster = self.getMongoDBClientObject()
        db = cluster["Wiki-scraper"]
        collection = db["test"]
        result = collection.find_one({"Name": name})
        return result
