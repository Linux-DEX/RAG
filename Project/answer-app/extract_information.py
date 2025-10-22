import os

import gradio as gr
from dotenv import load_dotenv
from gradio.themes.base import Base
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pymongo import MongoClient

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

try:
    client = MongoClient(os.getenv("MONGODB_URL"))
    collection = client[os.getenv("DATABASE_NAME")][os.getenv("TEXT_BLOB_COLLECTION")]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    collection = None

if collection is not None:
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorStore = MongoDBAtlasVectorSearch(
        collection, embeddings, index_name="vectorSearchRAG"
    )
else:
    vectorStore = None

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an accurate question-answering assistant. Use the following context to answer the user's question concisely and accurately:\n\n{context}",
        ),
        ("human", "{input}"),
    ]
)


def query_data(query):
    """
    Performs similarity search using MongoDB Atlas Vector Search and
    answers the question using Retrieval-Augmented Generation (RAG).
    """
    if not vectorStore:
        return (
            "MongoDB connection failed. Cannot perform vector search.",
            "MongoDB connection failed. Cannot perform RAG.",
        )

    K_VALUE = 3
    retriever = vectorStore.as_retriever(search_kwargs={"k": K_VALUE})

    docs = vectorStore.similarity_search(query, k=1)

    if not docs:
        as_output = "No relevant document found in the vector store."
        retriever_output = "Cannot answer without relevant context."
        return as_output, retriever_output
    else:
        as_output = docs[0].page_content

    try:
        llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)

        rag_chain = (
            {"context": retriever, "input": RunnablePassthrough()} | RAG_PROMPT | llm
        )

        result = rag_chain.invoke(query)
        retriever_output = result.content

    except Exception as e:
        retriever_output = f"Error during RAG execution: {e}"

    return as_output, retriever_output


# this part is for UI
with gr.Blocks(
    theme=Base(), title="Question Answering App using Vector Search + RAG"
) as demo:
    gr.Markdown(
        """
        # Question Answering App
        This app uses **MongoDB Atlas Vector Search** and **Retrieval-Augmented Generation (RAG)** powered by **LangChain** and **OpenAI**.
        """
    )
    textbox = gr.Textbox(label="Enter your question:")
    with gr.Row():
        button = gr.Button("Submit", variant="primary")
    with gr.Column():
        output1 = gr.Textbox(
            lines=5,
            max_lines=10,
            label="Output from Atlas Vector Search (Best Source Document)",
        )
        output2 = gr.Textbox(
            lines=5, max_lines=10, label="Output from RAG (LLM Answer using Context)"
        )

    button.click(query_data, inputs=textbox, outputs=[output1, output2])

demo.launch()
