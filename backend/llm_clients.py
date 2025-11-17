import aiohttp, os
from dotenv import load_dotenv

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")

async def query_groq(session, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with session.post(url, headers=headers, json=data) as r:
        try:
            res = await r.json()
        except Exception as e:
            return {"model": "Groq LLaMA3", "response": f"JSON decode error: {e}"}

        # Handle error responses gracefully
        if "choices" not in res:
            # Log or print the full response so you can debug
            print("Groq API error:", res)
            return {
                "model": "Groq LLaMA3",
                "response": f"Groq API returned error: {res.get('error', res)}",
            }

        return {
            "model": "Groq LLaMA3",
            "response": res["choices"][0]["message"]["content"],
        }

async def query_gpt(session, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
    data = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with session.post(url, headers=headers, json=data) as r:
        try:
            res = await r.json()
        except Exception as e:
            return {"model": "OpenAI GPT OSS 120b", "response": f"JSON decode error: {e}"}

        # Handle error responses gracefully
        if "choices" not in res:
            # Log or print the full response so you can debug
            print("OpenAI GPT OSS 120b", res)
            return {
                "model": "OpenAI GPT OSS 120b",
                "response": f"OpenAI GPT OSS 120b returned error: {res.get('error', res)}",
            }

        return {
            "model": "OpenAI GPT OSS 120b",
            "response": res["choices"][0]["message"]["content"],
        }
    
async def query_qwen(session, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
    data = {
        "model": "qwen/qwen3-32b",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with session.post(url, headers=headers, json=data) as r:
        try:
            res = await r.json()
        except Exception as e:
            return {"model": "Qwen 3", "response": f"JSON decode error: {e}"}

        # Handle error responses gracefully
        if "choices" not in res:
            # Log or print the full response so you can debug
            print("Qwen 3", res)
            return {
                "model": "Qwen 3",
                "response": f"Qwen 3 returned error: {res.get('error', res)}",
            }

        return {
            "model": "Qwen 3",
            "response": res["choices"][0]["message"]["content"],
        }
    
    

# Add similar functions for OpenAI and Gemini if desired.
