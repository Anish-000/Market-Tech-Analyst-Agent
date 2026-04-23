from dotenv import load_dotenv
import os

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print("Groq key loaded:", "YES" if groq_key else "NO")
print("Tavily key loaded:", "YES" if tavily_key else "NO")

from langchain_groq import ChatGroq
from tavily import TavilyClient
import chromadb
from sentence_transformers import SentenceTransformer

print("All imports successful")