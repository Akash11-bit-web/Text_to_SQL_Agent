import streamlit as st
import sqlalchemy as sa
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_SUBTITLE, MAX_HISTORY_DISPLAY, SUPPORTED_DBS
from llm.sql_generator import generate_sql
from llm.explainer import explain_results
from utils.query_runner import run_query
from utils.schema_extractor import get_schema_from_engine, get_table_preview
from history.query_history import save_to_history, get_history


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🗄️",
    layout="wide"
)


def create_engine_from_inputs(db_type, **kwargs):
    try:
        if db_type == "SQLite":
            path = kwargs.get("path", "")
            if not path:
                return None, "Please provide a SQLite file path."
            if not os.path.exists(path):
                return None, f"File not found: {path}"
            engine = sa.create_engine(f"sqlite:///{path}")

        elif db_type == "PostgreSQL":
            host     = kwargs.get("host", "localhost")
            port     = kwargs.get("port", 5432)
            database = kwargs.get("database", "")
            username = kwargs.get("username", "")
            password = kwargs.get("password", "")
            engine = sa.create_engine(
                f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
            )

        elif db_type == "MySQL":
            host     = kwargs.get("host", "localhost")
            port     = kwargs.get("port", 3306)
            database = kwargs.get("database", "")
            username = kwargs.get("username", "")
            password = kwargs.get("password", "")
            engine = sa.create_engine(
                f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            )

        else:
            return None, "Unsupported database type."

        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))

        return engine, None

    except Exception as e:
        return None, f"Connection failed: {str(e)}"


# ── Header ───────────────────────────────────────────────
st.title("🗄️ " + APP_TITLE)
st.caption(APP_SUBTITLE)
st.divider()


# ── Sidebar — Database Connection ────────────────────────
with st.sidebar:
    st.subheader("Connect Your Database")

    db_type = st.selectbox("Database type", SUPPORTED_DBS)

    if db_type == "SQLite":
        sqlite_path = st.text_input(
            "SQLite file path",
            placeholder="e.g. C:/projects/mydb.db"
        )
        connect_clicked = st.button("Connect", type="primary", use_container_width=True)

        if connect_clicked:
            with st.spinner("Connecting..."):
                engine, error = create_engine_from_inputs("SQLite", path=sqlite_path)
                if error:
                    st.error(error)
                else:
                    st.session_state.engine = engine
                    st.session_state.db_type = "SQLite"
                    st.session_state.db_name = os.path.basename(sqlite_path)
                    st.session_state.schema = get_schema_from_engine(engine)
                    st.success("Connected!")

    elif db_type == "PostgreSQL":
        pg_host = st.text_input("Host", value="localhost")
        pg_port = st.number_input("Port", value=5432)
        pg_db   = st.text_input("Database name")
        pg_user = st.text_input("Username")
        pg_pass = st.text_input("Password", type="password")
        connect_clicked = st.button("Connect", type="primary", use_container_width=True)

        if connect_clicked:
            with st.spinner("Connecting..."):
                engine, error = create_engine_from_inputs(
                    "PostgreSQL",
                    host=pg_host, port=pg_port,
                    database=pg_db, username=pg_user, password=pg_pass
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.engine = engine
                    st.session_state.db_type = "PostgreSQL"
                    st.session_state.db_name = pg_db
                    st.session_state.schema = get_schema_from_engine(engine)
                    st.success("Connected!")

    elif db_type == "MySQL":
        my_host = st.text_input("Host", value="localhost")
        my_port = st.number_input("Port", value=3306)
        my_db   = st.text_input("Database name")
        my_user = st.text_input("Username")
        my_pass = st.text_input("Password", type="password")
        connect_clicked = st.button("Connect", type="primary", use_container_width=True)

        if connect_clicked:
            with st.spinner("Connecting..."):
                engine, error = create_engine_from_inputs(
                    "MySQL",
                    host=my_host, port=my_port,
                    database=my_db, username=my_user, password=my_pass
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.engine = engine
                    st.session_state.db_type = "MySQL"
                    st.session_state.db_name = my_db
                    st.session_state.schema = get_schema_from_engine(engine)
                    st.success("Connected!")

    st.divider()

    if "schema" in st.session_state:
        st.subheader("Database Schema")
        with st.expander("View schema", expanded=False):
            st.code(st.session_state.schema, language="sql")
        st.caption("Only SELECT queries are allowed for safety.")


# ── Main Area ─────────────────────────────────────────────
if "engine" not in st.session_state:
    st.info("Connect a database from the sidebar to get started.")

    st.markdown("### Supported databases")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**SQLite**\nLocal `.db` file on your computer")
    with col2:
        st.markdown("**PostgreSQL**\nLocal or cloud hosted")
    with col3:
        st.markdown("**MySQL**\nLocal or cloud hosted")

else:
    st.success(f"Connected to: **{st.session_state.db_name}** ({st.session_state.db_type})")

    # ── Table Explorer ────────────────────────────────────
    st.subheader("Table Explorer")
    inspector = sa.inspect(st.session_state.engine)
    tables = inspector.get_table_names()

    selected_table = st.selectbox("Pick a table to preview", tables)

    if selected_table:
        preview_df = get_table_preview(st.session_state.engine, selected_table)
        st.caption(f"Showing first 5 rows of `{selected_table}`")
        st.dataframe(preview_df, use_container_width=True)

    st.divider()

    # ── Q&A Section ───────────────────────────────────────
    col_main, col_history = st.columns([2, 1])

    with col_main:
        st.subheader("Ask a Question")

        user_question = st.text_input(
            label="Your question",
            placeholder="e.g. Which product generated the most revenue?",
            label_visibility="collapsed"
        )

        submit = st.button("Submit", type="primary", use_container_width=True)

        if submit and user_question.strip():
            with st.spinner("Thinking..."):

                sql, sql_error = generate_sql(
                    user_question,
                    st.session_state.schema
                )

                if sql_error:
                    st.error(f"SQL Generation Failed: {sql_error}")
                    st.stop()

                df, db_error = run_query(sql, st.session_state.engine)

                if db_error:
                    st.error(f"Query Execution Failed: {db_error}")
                    with st.expander("See generated SQL"):
                        st.code(sql, language="sql")
                    st.stop()

                explanation, explain_error = explain_results(
                    user_question, sql, df
                )

                if explain_error:
                    st.error(f"Explanation Failed: {explain_error}")
                    st.stop()

            st.success("Done!")
            st.markdown("### Answer")
            st.info(explanation)

            with st.expander("View generated SQL"):
                st.code(sql, language="sql")

            with st.expander("View raw query results"):
                st.dataframe(df, use_container_width=True)

            save_to_history(user_question, sql, explanation)

        elif submit and not user_question.strip():
            st.warning("Please enter a question before submitting.")

    with col_history:
        st.subheader("Query History")
        history = get_history(limit=MAX_HISTORY_DISPLAY)

        if not history:
            st.caption("No queries yet. Ask something!")
        else:
            for entry in history:
                with st.expander(f"Q: {entry['question'][:45]}..."):
                    st.markdown(f"**Answer:** {entry['answer']}")
                    st.code(entry['sql'], language="sql")
                    st.caption(f"{entry['timestamp']}")
