from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
from typing import Optional
from pydantic import BaseModel
from app.llm_helper import generate_sql_query, execute_query

from app.visualization import generate_plot


app = FastAPI(
    title="E-commerce AI Agent API",
    description="Natural language interface for e-commerce data analysis",
    version="1.0"
)

class QueryRequest(BaseModel):
    question: str
    stream: bool = False
    visualize: bool = False

@app.get("/")
def read_root():
    """Root endpoint with API documentation"""
    return {
        "message": "E-commerce AI Agent API", 
        "endpoints": {
            "/query": {
                "method": "POST",
                "description": "Ask natural language questions about e-commerce data",
                "request_format": {
                    "question": "string",
                    "stream": "boolean (optional)",
                    "visualize": "boolean (optional)"
                }
            },
            "/health": {
                "method": "GET",
                "description": "Check service status"
            },
            "/docs": "Interactive API documentation"
        }
    }

@app.post("/query")
async def answer_question(request: QueryRequest):
    """
    Main endpoint for answering data questions
    
    Example request:
    {
        "question": "What is total sales?",
        "stream": false,
        "visualize": true
    }
    """
    try:
        # Generate SQL from natural language question
        sql_query = generate_sql_query(request.question)
        
        # Execute query against database
        result = execute_query(sql_query)
        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={
                    "error": result["error"],
                    "sql": sql_query,
                    "message": "SQL execution failed"
                }
            )
        
        # Stream response if requested
        if request.stream:
            return StreamingResponse(
                stream_response(request.question, sql_query, result, request.visualize),
                media_type="text/event-stream"
            )
        
        # Standard JSON response
        response = {
            "question": request.question,
            "sql": sql_query,
            "result": result
        }
        
        # Add visualization if requested
        if request.visualize:
            plot = generate_plot(result, request.question)
            if plot:
                response["plot"] = plot
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Service health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": "mistral-7b-openorca",
        "database": "connected",
        "version": "1.0"
    }

async def stream_response(question: str, sql: str, result: dict, visualize: bool):
    """Generate streaming response with typing effect"""
    # Stream SQL query
    yield f"🔍 Generated SQL:\n\n{sql}\n\n"
    await asyncio.sleep(0.5)
    
    # Stream results
    if "error" in result:
        yield f"❌ Error: {result['error']}"
        return
    
    yield "📊 Results:\n\n"
    
    if not result["rows"]:
        yield "No results found"
        return
    
    # Stream headers
    headers = " | ".join(result["columns"])
    yield f"{headers}\n"
    yield "-" * len(headers) + "\n"
    await asyncio.sleep(0.1)
    
    # Stream rows
    for row in result["rows"]:
        values = [str(row[col]) for col in result["columns"]]
        yield " | ".join(values) + "\n"
        await asyncio.sleep(0.05)
    
    # Stream visualization if requested
    if visualize:
        plot = generate_plot(result, question)
        if plot:
            yield "\n📈 Visualization:\n\n"
            yield f"![Plot]({plot})"

# For running directly during development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)