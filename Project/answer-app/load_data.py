import os

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


client = MongoClient(os.getenv("MONGODB_URL"))
collection = client[os.getenv("DATABASE_NAME")][os.getenv("TEXT_BLOB_COLLECTION")]

loader = DirectoryLoader("./sample_files", glob="./*.txt", show_progress=True)
data = loader.load()

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

vectorStore = MongoDBAtlasVectorSearch.from_documents(
    data, embeddings, collection=collection
)
