from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import os
import google.generativeai as genai
import getpass

load_dotenv()


if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))


pdf_path= Path(__file__).parent / "nodejs.pdf"
loader= PyPDFLoader(pdf_path)
docs= loader.load()


#chunking

text_splitter= RecursiveCharacterTextSplitter(
    chunk_size= 1000,
    chunk_overlap= 400 
)
split_documents=text_splitter.split_documents(documents= docs)

#vector embeddings

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

#using embedding_model create embeddings of split_document of split_docs and store it in db

vector_store= QdrantVectorStore.from_documents(
    documents=split_documents,
    url="http://vector-db:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)
print("Indexing of documents completed")
