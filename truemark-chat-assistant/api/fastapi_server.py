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
    "http://localhost:3300",
    "http://127.0.0.1:3300",
    "https://true-mark.spruked.com",
    "https://www.true-mark.spruked.com",
    "https://truemark.spruked.com",
    "https://www.truemark.spruked.com",
    "https://true_mark.spruked.com",
    "https://www.true_mark.spruked.com",
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
