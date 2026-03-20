import os
import pandas as pd
from groq import Groq
from config import MODEL_NAME, EXPLAIN_MAX_TOKENS, GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def explain_results(user_question: str, sql: str, df: pd.DataFrame) -> tuple:
    if df is None or df.empty:
        return "The query returned no results for your question.", None

    max_rows = 20
    if len(df) > max_rows:
        data_preview = df.head(max_rows).to_string(index=False)
        row_note = f"(Showing first {max_rows} of {len(df)} rows)"
    else:
        data_preview = df.to_string(index=False)
        row_note = ""

    prompt = f"""You are a helpful data analyst. A user asked a question about a database.
A SQL query was run and returned the results below.
Your job is to explain the results in clear, simple plain English.

USER QUESTION:
{user_question}

SQL QUERY THAT WAS RUN:
{sql}

QUERY RESULTS:
{data_preview}
{row_note}

INSTRUCTIONS:
- Answer the user's question directly in 1-3 sentences
- Mention specific numbers, names, or values from the results
- Keep it conversational and easy to understand
- Do not repeat the SQL query or use technical jargon

PLAIN ENGLISH ANSWER:"""

    try:
        message = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=EXPLAIN_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )

        explanation = message.choices[0].message.content.strip()
        return explanation, None

    except Exception as e:
        return None, f"Error generating explanation: {str(e)}"

