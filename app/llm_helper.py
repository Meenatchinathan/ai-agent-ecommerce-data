from llama_cpp import Llama
import sqlite3
import os
import re
from typing import Dict, List, Union, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "ecommerce.db")
MODEL_PATH = os.path.join(BASE_DIR, "models", "mistral-7b-openorca.Q4_K_M.gguf")

# Schema mapping for column name corrections
COLUMN_ALIASES = {
    "product_name": "product_id",
    "cpc": "cost_per_click",
    "roas": "return_on_ad_spend"
}

# Initialize LLM only once
LLM_INSTANCE = None

def initialize_llm() -> Llama:
    """Initialize and cache the LLM instance with error handling"""
    global LLM_INSTANCE
    if LLM_INSTANCE is None:
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file missing at {MODEL_PATH}")
            
            logger.info("Initializing LLM...")
            LLM_INSTANCE = Llama(
                model_path=MODEL_PATH,
                n_ctx=2048,
                n_threads=8,
                n_gpu_layers=1 if os.uname().sysname == "Darwin" else 0,
                verbose=False
            )
            
            # Verify LLM is working
            test_response = LLM_INSTANCE("Test", max_tokens=1)
            if not test_response:
                raise RuntimeError("LLM failed to respond to test prompt")
                
            logger.info("LLM initialized successfully")
        except Exception as e:
            LLM_INSTANCE = None
            logger.error(f"LLM initialization failed: {str(e)}")
            raise
    
    return LLM_INSTANCE

def get_db_schema() -> str:
    """Retrieve database schema with actual column names"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    schema = []
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cursor.fetchall():
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]  # Get only column names
            schema.append(f"{table_name}({', '.join(columns)})")
    finally:
        conn.close()
    
    return "\n".join(schema)

def normalize_column_names(sql: str) -> str:
    """Replace common column name variations with actual names"""
    for alias, actual in COLUMN_ALIASES.items():
        sql = re.sub(rf'\b{alias}\b', actual, sql, flags=re.IGNORECASE)
    return sql

def clean_sql(sql: str) -> str:
    """Validate and clean generated SQL"""
    if not sql or sql.strip() == ";":
        raise ValueError("Empty SQL query")
    
    # Remove markdown code blocks
    sql = re.sub(r'^```sql|```$', '', sql, flags=re.IGNORECASE).strip()
    
    # Ensure semicolon termination
    sql = sql.split(";")[0] + ";"
    
    # Normalize column names
    sql = normalize_column_names(sql)
    
    # Basic validation
    sql_lower = sql.lower()
    if not sql_lower.startswith(("select", "with")):
        raise ValueError("Only SELECT/WITH queries allowed")
    if any(word in sql_lower for word in ["insert", "update", "delete", "drop"]):
        raise ValueError("Data modification queries not allowed")
    
    return sql

def get_fallback_query(question: str) -> str:
    """Schema-aware fallback queries"""
    question = question.lower()
    
    if any(word in question for word in ["total", "sum", "sales"]):
        return "SELECT SUM(total_sales) FROM total_sales_metrics;"
    elif "highest cpc" in question:
        return "SELECT product_id, MAX(cost_per_click) FROM ad_sales_metrics GROUP BY product_id ORDER BY MAX(cost_per_click) DESC LIMIT 1;"
    elif "roas" in question:
        return "SELECT SUM(ad_sales)/SUM(ad_spend) AS return_on_ad_spend FROM ad_sales_metrics;"
    elif "count" in question:
        return "SELECT COUNT(*) FROM products;"
    else:
        return "SELECT * FROM total_sales_metrics LIMIT 5;"

def generate_sql_query(question: str) -> str:
    """Generate SQL from natural language with robust error handling"""
    try:
        llm = initialize_llm()
        schema = get_db_schema()
        
        prompt = f"""
        ### Database Schema (Use EXACTLY these column names):
        {schema}
        
        ### Examples:
        Good: SELECT SUM(total_sales) FROM total_sales_metrics;
        Bad: SELECT ProductName FROM... (never use approximate column names)
        
        ### Question:
        {question}
        
        ### Rules:
        1. Use ONLY the tables/columns shown above
        2. Return JUST the SQL query ending with ;
        3. Never explain or add comments
        4. For aggregates, use explicit column names (e.g., SUM(total_sales))
        
        ### SQL Query:
        """
        
        response = llm(
            prompt,
            max_tokens=256,
            stop=["\n", ";"],
            temperature=0.1
        )
        
        raw_sql = response['choices'][0]['text'].strip()
        return clean_sql(raw_sql)
        
    except Exception as e:
        logger.warning(f"LLM generation failed for '{question}': {str(e)}")
        return get_fallback_query(question)

def execute_query(sql: str) -> Dict[str, Union[List[str], List[Dict]]]:
    """Execute SQL with proper error handling"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []
        
        return {
            "columns": columns,
            "rows": [dict(row) for row in rows]
        }
    except sqlite3.Error as e:
        return {
            "error": str(e),
            "sql": sql
        }
    finally:
        conn.close()

# Initialize on import (will show errors immediately)
try:
    initialize_llm()
except Exception as e:
    logger.error(f"Startup initialization failed: {str(e)}")