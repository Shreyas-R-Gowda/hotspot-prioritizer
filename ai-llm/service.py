from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI LLM Service")

# Initialize OpenAI Client
# Expects OPENAI_API_KEY in env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SummarizeRequest(BaseModel):
    reports: List[str]

class SummarizeResponse(BaseModel):
    summary: str

class SQLRequest(BaseModel):
    query: str

class SQLResponse(BaseModel):
    sql_query: str

@app.get("/")
def root():
    return {"message": "ai-llm service is running"}

@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    if not request.reports:
        return {"summary": "No reports to summarize."}
    
    # Combine reports into a single text block
    text_block = "\n".join([f"- {r}" for r in request.reports])
    
    prompt = f"""
    You are an assistant for a city management system. 
    Summarize the following citizen reports into a concise 3-sentence overview highlighting the main issues and locations.
    
    Reports:
    {text_block}
    
    Summary:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        summary = response.choices[0].message.content.strip()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_sql", response_model=SQLResponse)
def generate_sql(request: SQLRequest):
    # Schema context for the LLM
    schema_context = """
    Table: reports
    Columns: id (int), title (text), description (text), category (text), status (text), upvotes (int), created_at (timestamp).
    Note: The table has a PostGIS geometry column 'location'. 
    To filter by distance, use ST_DWithin(location, ST_MakePoint(lon, lat)::geography, radius_meters).
    To get lat/lon, use ST_X(location::geometry) as lon, ST_Y(location::geometry) as lat.
    """
    
    prompt = f"""
    You are a SQL expert for a PostgreSQL + PostGIS database.
    Convert the following natural language query into a SQL query.
    
    Schema:
    {schema_context}
    
    Rules:
    1. Return ONLY the SQL query. No markdown, no explanation.
    2. The query must be read-only (SELECT).
    3. Do not use markdown formatting like ```sql.
    
    Query: "{request.query}"
    
    SQL:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        sql = response.choices[0].message.content.strip()
        # Basic safety check
        if not sql.lower().startswith("select"):
            raise HTTPException(status_code=400, detail="Generated query was not a SELECT statement.")
        
        # Remove markdown if present
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        return {"sql_query": sql}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
