import streamlit as st
import pandas as pd
from database import seed_database, get_connection
from llm import generate_sql

st.set_page_config(page_title="Natural Language SQL Query Tool", layout="centered")
st.title("E-Commerce Natural Language SQL Query Tool")

seed_database()

# ---------------- SESSION STATE ----------------
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "history" not in st.session_state:
    st.session_state.history = []  # list of {question, sql, dataframe}

BLOCKED_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE"]

# ================= TASK 1: NATURAL LANGUAGE INPUT =================
st.header("1. Ask a Question")

user_question = st.text_area(
    "Enter your question about the e-commerce data",
    value=st.session_state.current_query,
    height=100,
    placeholder="e.g. Find the top 5 customers by total spend"
)

if st.button("Generate SQL"):
    if not user_question.strip():
        st.error("Please enter a meaningful question.")
    else:
        with st.spinner("Generating SQL..."):
            try:
                sql = generate_sql(user_question)
                st.session_state.generated_sql = sql
                st.session_state.current_query = user_question
            except Exception as e:
                st.error(f"Failed to generate SQL: {e}")

# ================= TASK 2: DISPLAY GENERATED SQL =================
if st.session_state.generated_sql:
    st.header("2. Generated SQL")
    st.code(st.session_state.generated_sql, language="sql")

    # ================= TASK 4: EXECUTE QUERY =================
    if st.button("Execute Query"):
        sql = st.session_state.generated_sql
        sql_upper = sql.upper()

        # ---- TASK 3: SAFETY VALIDATION ----
        blocked = [kw for kw in BLOCKED_KEYWORDS if kw in sql_upper]
        if blocked:
            st.error(f"Unsafe query detected ({', '.join(blocked)}). Only SELECT queries are allowed.")
        elif not sql_upper.strip().startswith("SELECT"):
            st.error("Only SELECT queries are allowed.")
        else:
            try:
                conn = get_connection()
                df = pd.read_sql_query(sql, conn)
                conn.close()

                st.header("3. Results")
                if df.empty:
                    st.info("No matching records found.")
                else:
                    st.write(f"Showing {len(df)} results")
                    st.dataframe(df, use_container_width=True, height=350)

                # Save to history
                st.session_state.history.append({
                    "question": st.session_state.current_query,
                    "sql": sql,
                    "dataframe": df
                })

            except Exception as e:
                err = str(e)
                if "no such table" in err.lower():
                    st.error("That table doesn't exist in the database.")
                elif "no such column" in err.lower():
                    st.error("That column doesn't exist in the database.")
                else:
                    st.error(f"Query failed: {err}")

# ================= TASK 6: QUERY HISTORY =================
st.header("4. Query History")

if not st.session_state.history:
    st.info("No queries executed yet.")
else:
    for i, item in enumerate(reversed(st.session_state.history)):
        idx = len(st.session_state.history) - i
        with st.expander(f"{idx}. {item['question']}"):
            st.code(item["sql"], language="sql")
            if item["dataframe"].empty:
                st.info("No matching records found.")
            else:
                st.write(f"Showing {len(item['dataframe'])} results")
                st.dataframe(item["dataframe"], use_container_width=True, height=250)

            if st.button("Reload this query", key=f"reload_{idx}"):
                st.session_state.current_query = item["question"]
                st.session_state.generated_sql = item["sql"]
                st.rerun()