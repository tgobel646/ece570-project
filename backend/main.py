# backend/main.py

from pathlib import Path
from contextlib import asynccontextmanager
import aiohttp
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import Response, Rating, SessionLocal   
from .llm_clients import query_groq, query_gpt, query_kimi     

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# -------------------- CORE BATCH LOGIC --------------------

async def run_batch_core():
    prompts_path = BASE_DIR / "prompts.txt"
    answers_path = BASE_DIR / "answers.txt"   # comment this out if you don't use it

    with prompts_path.open() as f:
        prompts = [line.strip() for line in f if line.strip()]

    # if you don't use correct answers, you can remove everything about answers_path
    with answers_path.open() as f:
        answers = [line.strip() for line in f if line.strip()]

    if len(prompts) != len(answers):
        raise HTTPException(
            status_code=400,
            detail=f"prompts ({len(prompts)}) and answers ({len(answers)}) mismatch"
        )

    total_responses = 0

    async with aiohttp.ClientSession() as session:
        for prompt, correct_answer in zip(prompts, answers):
            tasks = [
                query_groq(session, prompt),
                query_gpt(session, prompt),
                query_kimi(session, prompt),
            ]
            results = await asyncio.gather(*tasks)

            db = SessionLocal()
            try:
                for res in results:
                    entry = Response(
                        prompt=prompt,
                        model=res["model"],
                        response=res["response"],
                        correct_answer=correct_answer,
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

# -------------------- LIFESPAN (RUN BATCH ONCE IF EMPTY) --------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs BEFORE the app starts serving
    db = SessionLocal()
    try:
        count = db.query(Response).count()
    finally:
        db.close()

    if count == 0:
        print("No responses found; running initial batch...")
        await run_batch_core()
    else:
        print(f"Found {count} responses; skipping initial batch.")

    # hand control to FastAPI
    yield

    # runs AFTER shutdown (optional cleanup)
    print("Server shutting down.")

# -------------------- CREATE APP (THIS IS THE ONE UVICORN USES) --------------------

app = FastAPI(lifespan=lifespan)

# Static files + index.html
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")

# -------------------- API ENDPOINTS --------------------

@app.post("/run-batch")
async def run_batch():
    return await run_batch_core()

@app.get("/responses")
def get_responses():
    db = SessionLocal()
    try:
        rows = db.query(Response).all()
        out = []
        for r in rows:
            scores = [rt.score for rt in r.ratings] if hasattr(r, "ratings") else []
            num_pos = sum(1 for s in scores if s > 0)
            num_neg = sum(1 for s in scores if s < 0)
            cumulative = sum(scores) if scores else 0

            out.append({
                "id": r.id,
                "prompt": r.prompt,
                "model": r.model,
                "response": r.response,
                "correct_answer": getattr(r, "correct_answer", None),
                "num_ratings": len(scores),
                "positive_ratings": num_pos,
                "negative_ratings": num_neg,
                "cumulative_score": cumulative,
            })
        return out
    finally:
        db.close()

@app.post("/rate/{response_id}/{rating}")
def rate_response(response_id: int, rating: int):
    db = SessionLocal()
    try:
        resp = db.query(Response).get(response_id)
        if resp is None:
            raise HTTPException(status_code=404, detail=f"id {response_id} not found")

        new_rating = Rating(response_id=response_id, score=rating)
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)

        return {"status": "rated", "id": response_id, "score": rating}
    finally:
        db.close()
