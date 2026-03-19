import os
import sys
from groq import Groq

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import MODEL_NAME, SQL_MAX_TOKENS, GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def clean_sql(raw_response: str) -> str:
    sql = raw_response.strip()
    if "```sql" in sql:
        sql = sql.split("```sql")[1].split("```")[0].strip()
    elif "```" in sql:
        sql = sql.split("```")[1].split("```")[0].strip()
    return sql.strip()


def generate_sql(user_question: str, schema: str) -> tuple:
    prompt = f"""You are an expert SQL assistant. Given the database schema below and a user question,
generate a single valid SQL SELECT query that answers the question.

RULES:
- Return ONLY the raw SQL query, nothing else
- No explanations, no markdown, no code blocks
- Only use SELECT statements, never DROP/DELETE/UPDATE/INSERT
- Use table and column names exactly as shown in the schema

DATABASE SCHEMA:
{schema}

USER QUESTION:
{user_question}

SQL QUERY:"""

    try:
        message = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=SQL_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_sql = message.choices[0].message.content
        cleaned_sql = clean_sql(raw_sql)
        return cleaned_sql, None

    except Exception as e:
        return None, f"Error generating SQL: {str(e)}"