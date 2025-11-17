import os
import asyncio
import aiohttp
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from dotenv import load_dotenv
from models import Response, SessionLocal
from llm_clients import query_groq, query_gpt, query_qwen  # add more models if you have them

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (index.html, app.js) at /static/...
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------- FRONTEND ROOT (single link) ----------

@app.get("/")
def root():
    """Serve the main reviewer UI."""
    index_path = STATIC_DIR / "index.html"
    return FileResponse(index_path)


# ---------- API: RUN BATCH ----------

@app.post("/run-batch")
async def run_batch():
    prompts_path = BASE_DIR / "prompts.txt"
    with prompts_path.open() as f:
        prompts = [line.strip() for line in f if line.strip()]

    total_responses = 0

    async with aiohttp.ClientSession() as session:
        for prompt in prompts:
            tasks = [
                query_groq(session, prompt),
                query_gpt(session, prompt),
                query_qwen(session, prompt),
            ]
            results = await asyncio.gather(*tasks)

            db = SessionLocal()
            try:
                for res in results:
                    entry = Response(
                        prompt=prompt,
                        model=res["model"],
                        response=res["response"],
                    )
                    db.add(entry)
                    total_responses += 1
                db.commit()
            finally:
                db.close()

    return {
        "status": "completed",
        "num_prompts": len(prompts),
        "num_responses": total_responses,
    }


# ---------- API: GET RESPONSES ----------

@app.get("/responses")
def get_responses():
    db = SessionLocal()
    data = db.query(Response).all()
    db.close()
    return [
        {
            "id": r.id,
            "prompt": r.prompt,
            "model": r.model,
            "response": r.response,
            "rating": r.rating,
        }
        for r in data
    ]


# ---------- API: RATE RESPONSE ----------

@app.post("/rate/{response_id}/{rating}")
def rate_response(response_id: int, rating: int):
    db = SessionLocal()
    r = db.query(Response).get(response_id)
    if r is None:
        db.close()
        return {"status": "error", "message": f"id {response_id} not found"}

    r.rating = rating
    db.commit()
    db.close()
    return {"status": "rated", "id": response_id, "rating": rating}
