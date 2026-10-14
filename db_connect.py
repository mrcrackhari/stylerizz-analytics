"""
db_connect.py — MySQL connection helper for Stylerizz Analytics.
Uses Streamlit secrets for credentials.
"""
import pandas as pd
import mysql.connector
from mysql.connector import Error
import streamlit as st


def get_connection():
    """Create and return a MySQL connection using st.secrets."""
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=st.secrets.get("DB_PORT", 3306),
        )
        return conn
    except Error as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


def run_query(sql: str, params: tuple = None) -> pd.DataFrame:
    """Execute a SELECT and return a pandas DataFrame."""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        return pd.read_sql(sql, conn, params=params)
    except Error as e:
        st.error(f"❌ Query failed: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def run_ddl(sql: str) -> bool:
    """Execute DDL/DML (INSERT/UPDATE/etc.). Returns True on success."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return True
    except Error as e:
        st.error(f"❌ DDL failed: {e}")
        return False
    finally:
        conn.close()