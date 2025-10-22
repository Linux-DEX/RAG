import os

import pymongo
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Set your OpenAI API key
client_openai = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

mongodb_url = os.getenv("MONGODB_URL")
database = os.getenv("DATABASE_NAME")
collection_name = os.getenv("EMBEDDED_MOVIE_COLLECTION")

client = pymongo.MongoClient(mongodb_url)
db = client[database]
collection = db[collection_name]


def generate_embedding(text: str) -> list[float]:
    response = client_openai.embeddings.create(
        model="text-embedding-ada-002", input=[text]
    )
    return response.data[0].embedding


query = "imaginary characters from outer space at war"

results = collection.aggregate(
    [
        {
            "$vectorSearch": {
                "queryVector": generate_embedding(query),
                "path": "plot_embedding",
                "numCandidates": 100,
                "limit": 4,
                "index": "PlotSemanticSearch",
            }
        }
    ]
)

for document in results:
    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')
