# flake8: noqa
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import os
import getpass

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass(
        "Enter API key for Google Gemini: ")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_db = QdrantVectorStore.from_existing_collection(
    collection_name="learning_vectors",
    url="http://vector-db:6333",
    embedding=embedding_model
)


query = input("> ")

# vector similarity search [query] in db

search_results = vector_db.similarity_search(
    query=query
)

print(search_results)

context = "\n\n\n".join(
    [f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])


SYSTEM_PROMPT = f"""You are a helpful AI assistant who answers user query based on the available context
retrieved from a PDF  file along with page_contents and page number.
You should only ans the user based on the following context and navigate the user to open the right page number to know more.

Context: {context}

"""
model = genai.GenerativeModel(
    "gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

# print(SYSTEM_PROMPT)


response = model.generate_content(
    contents=[
        {"parts": [{"text": query}], "role": "user"}
    ]
)
print(f"🤖: {response.text}")
# print(f"🤖: {query}", response.text, "\n\n\n")
# return response.text
