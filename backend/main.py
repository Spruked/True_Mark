from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import os

app = FastAPI()

# --- CSP Middleware ---
# This middleware sets Content-Security-Policy headers.
# In development, it allows 'unsafe-eval' for Vite HMR to work.
# In production, it enforces a strict CSP (no 'unsafe-eval').
#
# To control the mode, set the environment variable TRUEMARK_ENV:
#   TRUEMARK_ENV=development (default) => relaxed CSP for dev
#   TRUEMARK_ENV=production           => strict CSP for prod
class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Detect dev mode (set TRUEMARK_ENV=development for dev, anything else for prod)
        is_dev = os.environ.get("TRUEMARK_ENV", "development").lower() == "development"
        if is_dev:
            csp = "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        else:
            csp = "default-src 'self'; script-src 'self'; style-src 'self';"
        response.headers["Content-Security-Policy"] = csp
        return response

app.add_middleware(CSPMiddleware)

@app.get("/")
def read_root():
    return {"message": "True Mark Mint Engine FastAPI backend is running."}

# TODO: Add endpoints for minting, payments, certificate generation, and price quoting
