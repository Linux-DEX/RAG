import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    exit()

client = OpenAI(api_key=api_key)


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embedding.create(input=[text], model=model).data[0].embedding


df = pd.read_csv("output/embedding_1k_review.csv")
df["ada_embedding"] = df.ada_embedding.apply(eval).apply(np.array)

df["ada_embedding"] = df.combined.apply(
    lambda x: get_embedding(x, model="text-embedding-3-small")
)
df.to_csv("output/embedded_1k_reviews.csv", index=False)
