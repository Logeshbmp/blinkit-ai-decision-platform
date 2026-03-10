from dotenv import load_dotenv
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_PATH = os.path.join(BASE_DIR, "data", "faiss_index")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    FAISS_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.2
)

def ask_business_question(question: str):

    docs = vectorstore.similarity_search(question, k=8)

    context = "\n".join([
        f"[Area: {doc.metadata.get('area')}] {doc.page_content}"
        for doc in docs
    ])

    prompt = f"""
You are a senior business analyst at Blinkit.

Customer feedback excerpts:
{context}

Question:
{question}

Answer in ONE sentence explaining the root cause.
"""

    return llm.invoke(prompt).content