import pandas as pd
import sqlalchemy as sa

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "CREATE"]


def is_safe_query(sql: str) -> bool:
    sql_upper = sql.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql_upper:
            return False
    return True


def run_query(sql: str, engine) -> tuple:
    sql = sql.strip()

    if not is_safe_query(sql):
        return None, "Unsafe query blocked. Only SELECT statements are allowed."

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(sa.text(sql), conn)

        if df.empty:
            return None, "Query ran successfully but returned no results."

        return df, None

    except sa.exc.OperationalError as e:
        return None, f"SQL error: {str(e)}"

    except Exception as e:
        return None, f"Unexpected error: {str(e)}"