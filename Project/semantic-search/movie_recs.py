"""
- here we are generating embedding locally with generate_embedding() func and saving in mongodb collection plot_embedding_hf field, & creating index for that field on mongodb atlas.
- use aggregate function to query on the embedding.
"""

import os

import pymongo
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
database = os.getenv("DATABASE_NAME")
movie_collection = os.getenv("MOVIE_COLLECTION")

client = pymongo.MongoClient(mongodb_url)
db = client[database]
collection = db[movie_collection]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# generate embedding with model object
# NOTE we can also use requests and hf url and key to generate
def generate_embedding(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()


# testing generate_embedding() function
# print(generate_embedding("Arch Linux is awesome"))

# create vector embedding for 50 document
# for doc in collection.find({"plot": {"$exists": True}}).limit(50):
#     doc["plot_embedding_hf"] = generate_embedding(doc["plot"])
#     collection.replace_one({"_id": doc["_id"]}, doc)


query = "imaginary characters from outer space at war"

results = collection.aggregate(
    [
        {
            "$vectorSearch": {
                "queryVector": generate_embedding(query),
                "path": "plot_embedding_hf",
                "numCandidates": 100,
                "limit": 4,
                "index": "PlotSemanticSearch",
            }
        }
    ]
)

for document in results:
    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')
