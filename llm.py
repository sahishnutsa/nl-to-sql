import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from database import SCHEMA_DESCRIPTION

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_sql(user_question):
    prompt = f"""You are a SQL generation engine for a SQLite database.

DATABASE SCHEMA:
{SCHEMA_DESCRIPTION}

RULES (follow exactly):
- Generate ONLY a single SQLite-compatible SELECT query.
- NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements.
- Return ONLY the raw SQL query. No markdown, no code fences, no explanations, no comments.
- Use proper JOINs when the question requires data from multiple tables.
- Use SQLite date functions (date('now'), date('now', '-30 days')) for relative date filters.
- If the question cannot be answered with the given schema, return: SELECT 'Query not supported' AS message;

User question: "{user_question}"

SQL query:"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # strip markdown fences if present despite instructions
    raw = raw.replace("```sql", "").replace("```", "").strip()

    # keep only up to the first semicolon-terminated statement (defensive)
    match = re.search(r"(SELECT[\s\S]*?;)", raw, re.IGNORECASE)
    if match:
        raw = match.group(1)

    return raw.strip()