import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("OPENAI_API_KEY")
if not GROQ_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables.")

client = openai.OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI(title="Amenify Support Bot")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG System built with absolutely free TF-IDF (No embedding API cost)
class RAGSystem:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.documents = []
        self.doc_vectors = None
        self.load_knowledge_base()
        
    def load_knowledge_base(self):
        filepath = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.txt")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.documents = [line.strip() for line in f if line.strip()]
            
            if len(self.documents) > 0:
                self.doc_vectors = self.vectorizer.fit_transform(self.documents)
                print(f"Loaded {len(self.documents)} documents into local knowledge base.")
        else:
            print("Knowledge base not found. Please run scraper.py first.")
            
    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        if not self.documents:
            return ""
            
        # Get tf-idf vector for the query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity with all documents
        similarities = cosine_similarity(query_vec, self.doc_vectors).flatten()
        
        # Get indices of top_k most similar docs
        if max(similarities) < 0.1: # Threshold to ensure it's actually relevant
            return ""
            
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Combine the selected text
        context = "\\n\\n".join([self.documents[i] for i in top_indices if similarities[i] > 0.1])
        return context

# Initialize RAG system
rag = RAGSystem()

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not GROQ_API_KEY:
         raise HTTPException(status_code=500, detail="API key not configured.")
         
    # 1. Retrieve context
    context = rag.get_relevant_context(request.message)
    
    # 2. Strict system prompt
    system_prompt = f"""You are the official Amenify Customer Support Bot.
You must ONLY answer incoming questions using the exact information provided in the Context below.
If the answer cannot be found in the Context provided below, you MUST respond with precisely: "I don't know". Do not attempt to guess or provide generic advice.

Context Information:
{context}
"""

    # 3. Build messages with history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history
    for msg in request.history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": request.message})

    try:
        # We can use a fast, cheap model
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0, # Zero hallucinations
            max_tokens=300
        )
        
        reply = response.choices[0].message.content
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
