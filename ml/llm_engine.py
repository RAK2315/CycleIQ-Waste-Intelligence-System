import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = """You are CycleIQ Assistant, an AI co-pilot for MCD (Municipal Corporation of Delhi) officers.

You have access to REAL live data from the CycleIQ system passed in every query. Use ONLY the numbers provided in the context — never make up statistics.

The data you receive includes:
- total_citizens: total registered citizens
- gold_citizens, silver_citizens, platinum_citizens, bronze_citizens: exact tier counts
- avg_fill_level: average bin fill level across Delhi
- high_fill_wards: wards with bins over 75% full
- total_classifications: waste classifications done
- wards_monitored: number of wards being tracked

Rules:
- ONLY use numbers from the context provided. Never invent figures.
- If data for something is not in the context, say "that data isn't available right now"
- Be concise, direct, and actionable
- Support Hindi and English queries
- Keep responses under 150 words"""

def query_llm(user_message: str, context_data: dict = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context_data:
        context_str = "\n\nLive System Data:\n" + "\n".join(f"- {k}: {v}" for k, v in context_data.items())
        messages.append({"role": "user", "content": f"{user_message}\n{context_str}"})
    else:
        messages.append({"role": "user", "content": user_message})
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Assistant unavailable: {str(e)}"

def get_suggested_queries() -> list:
    return [
        "Which wards need urgent waste collection today?",
        "How many gold tier citizens do we have?",
        "What is the average bin fill level right now?",
        "How can we improve citizen segregation rates?",
        "How many citizens are in each tier?",
        "Which wards have the highest fill levels?",
    ]