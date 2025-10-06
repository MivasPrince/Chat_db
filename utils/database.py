"""Database connection and query utilities"""
import os
import psycopg2
import pandas as pd
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Database configuration
db_config = {
    "host": os.getenv('DB_HOST', '16.170.143.253'),
    "port": int(os.getenv('DB_PORT', 5432)),
    "user": os.getenv('DB_USER', 'admin'),
    "password": os.getenv('DB_PASSWORD', 'password123'),
    "database": os.getenv('DB_NAME', 'miva_ai_db'),
}

SCHEMA = os.getenv('DB_SCHEMA', 'public')

@st.cache_resource
def get_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def test_connection() -> bool:
    """Test database connection"""
    try:
        conn = psycopg2.connect(**db_config)
        conn.close()
        return True
    except:
        return False

@st.cache_data(ttl=300)  # Cache for 5 minutes
def list_tables(schema: str = SCHEMA) -> List[str]:
    """Get list of tables in schema"""
    sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name;
    """
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (schema,))
                return [r[0] for r in cur.fetchall()]
    except Exception as e:
        st.error(f"Error listing tables: {e}")
        return []

@st.cache_data(ttl=300)
def list_columns(table: str, schema: str = SCHEMA) -> pd.DataFrame:
    """Get columns information for a table"""
    sql = """
    SELECT
        c.ordinal_position,
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        CASE
            WHEN tc.constraint_type = 'PRIMARY KEY' THEN true
            ELSE false
        END AS is_primary_key
    FROM information_schema.columns c
    LEFT JOIN information_schema.key_column_usage k
        ON  c.table_schema = k.table_schema
        AND c.table_name  = k.table_name
        AND c.column_name = k.column_name
    LEFT JOIN information_schema.table_constraints tc
        ON  tc.table_schema = k.table_schema
        AND tc.table_name   = k.table_name
        AND tc.constraint_name = k.constraint_name
        AND tc.constraint_type = 'PRIMARY KEY'
    WHERE c.table_schema = %s
      AND c.table_name   = %s
    ORDER BY c.ordinal_position;
    """
    try:
        with psycopg2.connect(**db_config) as conn:
            return pd.read_sql(sql, conn, params=(schema, table))
    except Exception as e:
        st.error(f"Error getting columns for {table}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_table_data(table: str, limit: int = 1000, schema: str = SCHEMA) -> pd.DataFrame:
    """Get data from a table"""
    sql = f'SELECT * FROM "{schema}"."{table}" LIMIT %s'
    try:
        with psycopg2.connect(**db_config) as conn:
            return pd.read_sql(sql, conn, params=(limit,))
    except Exception as e:
        st.error(f"Error getting data from {table}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_table_count(table: str, schema: str = SCHEMA) -> int:
    """Get row count for a table"""
    sql = f'SELECT COUNT(*) FROM "{schema}"."{table}"'
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchone()[0]
    except Exception as e:
        st.error(f"Error getting count for {table}: {e}")
        return 0

def execute_query(query: str) -> Tuple[pd.DataFrame, str]:
    """Execute custom SQL query"""
    try:
        with psycopg2.connect(**db_config) as conn:
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                df = pd.read_sql(query, conn)
                return df, "success"
            else:
                # For non-SELECT queries
                with conn.cursor() as cur:
                    cur.execute(query)
                    conn.commit()
                    return pd.DataFrame(), f"Query executed successfully. Rows affected: {cur.rowcount}"
    except Exception as e:
        return pd.DataFrame(), f"Error: {str(e)}"

@st.cache_data(ttl=300)
def get_table_stats() -> Dict[str, Any]:
    """Get overall database statistics"""
    stats = {}
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                # Table count
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (SCHEMA,))
                stats['table_count'] = cur.fetchone()[0]
                
                # Total columns
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_schema = %s
                """, (SCHEMA,))
                stats['total_columns'] = cur.fetchone()[0]
                
                # Database size
                cur.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                stats['db_size'] = cur.fetchone()[0]
                
                # Approximate total records (sum of all tables)
                total_records = 0
                tables = list_tables()
                for table in tables:
                    try:
                        cur.execute(f'SELECT COUNT(*) FROM "{SCHEMA}"."{table}"')
                        total_records += cur.fetchone()[0]
                    except:
                        continue
                stats['total_records'] = total_records
                
    except Exception as e:
        st.error(f"Error getting stats: {e}")
    
    return stats

@st.cache_data(ttl=300)
def get_table_metadata(table: str, schema: str = SCHEMA) -> Dict[str, Any]:
    """Get detailed metadata for a table"""
    metadata = {}
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                # Table size
                cur.execute(f"""
                    SELECT pg_size_pretty(pg_relation_size('"{schema}"."{table}"'))
                """)
                metadata['size'] = cur.fetchone()[0]
                
                # Row count
                metadata['row_count'] = get_table_count(table, schema)
                
                # Column info
                metadata['columns'] = list_columns(table, schema)
                
                # Indexes
                cur.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE schemaname = %s AND tablename = %s
                """, (schema, table))
                metadata['indexes'] = cur.fetchall()
                
    except Exception as e:
        st.error(f"Error getting metadata for {table}: {e}")
    
    return metadata
