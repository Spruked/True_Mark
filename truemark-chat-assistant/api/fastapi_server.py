# Josephine Chat Assistant FastAPI Server
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
from knowledge_graph import KnowledgeGraph
from inference_engine import InferenceEngine
from improvement_loop import ImprovementLoop

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Add your deployed frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kg = KnowledgeGraph()
ie = InferenceEngine(kg)
il = ImprovementLoop(kg)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    answer = ie.answer(req.message)
    return ChatResponse(response=answer)
