# Josephine — True Mark Chat Assistant

A self-contained, branded chat bubble assistant for the True Mark Mint Engine.

## Features
- Branded as "Josephine" — always available in the lower right corner
- Answers user/admin questions about privacy, minting, compliance, and onboarding
- Self-improving, persistent knowledge graph (demo)
- No external AI dependencies

## Structure
- `core/` — Knowledge graph, inference engine, improvement loop
- `api/` — FastAPI backend
- `frontend/` — React chat bubble UI

## Running Locally
1. `cd truemark-chat-assistant`
2. `pip install -r requirements.txt`
3. `uvicorn api.fastapi_server:app --reload --port 8001`
4. In another terminal: `cd frontend && npm install && npm run dev`

## Integration
- Import and render `ChatBubble.jsx` in your main React app (e.g., in `App.jsx`)
- Set `REACT_APP_JOSEPHINE_API` to your backend URL if not using default

---
