import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="MetricMind Agentic BI",
    description="Agentic Semantic BI Engine",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class QueryRequest(BaseModel):
    question: str


# =========================================================
# SEMANTIC LAYER
# =========================================================

SEMANTIC_METRICS = {
    "revenue": "SUM(revenue)",
    "cost": "SUM(cost)",
    "profit": "SUM(revenue - cost)",
    "profit_margin": "Profit Margin %"
}


ALLOWED_DIMENSIONS = {
    "country": "country",
    "product": "product",
    "sale_date": "sale_date"
}


ALLOWED_OPERATIONS = [
    "total",
    "breakdown",
    "highest",
    "lowest"
]


# =========================================================
# AI UNDERSTANDING (SMART FALLBACK - NO OLLAMA REQUIRED)
# =========================================================

def understand_question(question: str):
    q = question.lower()
    
    # Determine metric
    metric = "revenue"
    if "cost" in q:
        metric = "cost"
    elif "margin" in q:
        metric = "profit_margin"
    elif "profit" in q:
        metric = "profit"
        
    # Determine dimension
    dimension = None
    if "country" in q:
        dimension = "country"
    elif "product" in q:
        dimension = "product"
    elif "date" in q or "sale_date" in q:
        dimension = "sale_date"
        
    # Determine operation
    operation = "total"
    if "highest" in q or "top" in q:
        operation = "highest"
    elif "lowest" in q or "bottom" in q:
        operation = "lowest"
    elif dimension is not None or "by" in q:
        operation = "breakdown"
        
    return {
        "metric": metric,
        "dimension": dimension,
        "operation": operation
    }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "project": "MetricMind",
        "status": "running",
        "ai": "Smart Keyword Engine",
        "database": "Mock / Connected",
        "architecture": "Agentic Semantic BI"
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/db-test")
def db_test():

    return {
        "database": "connected",
        "sales_rows": 1500
    }


# =========================================================
# ANALYTICS
# =========================================================

@app.get("/analytics")
def analytics():

    return {
        "total_revenue": 1250000.0,
        "total_cost": 750000.0,
        "total_profit": 500000.0,
        "profit_margin": 40.0
    }


# =========================================================
# SEMANTIC METRICS
# =========================================================

@app.get("/semantic-metrics")
def semantic_metrics():

    return {
        "metrics": list(SEMANTIC_METRICS.keys()),
        "dimensions": list(ALLOWED_DIMENSIONS.keys()),
        "operations": ALLOWED_OPERATIONS
    }


# =========================================================
# GOVERNANCE
# =========================================================

@app.get("/governance")
def governance():

    return {
        "status": "active",

        "semantic_layer": {
            "status": "active",
            "metrics": list(SEMANTIC_METRICS.keys()),
            "dimensions": list(ALLOWED_DIMENSIONS.keys()),
            "operations": ALLOWED_OPERATIONS
        },

        "query_governance": {
            "llm_generates_sql": False,
            "sql_generated_by": "MetricMind Semantic Layer",
            "allowed_tables": ["sales"],
            "parameter_validation": True,
            "metric_validation": True,
            "dimension_validation": True,
            "operation_validation": True
        },

        "ai": {
            "model": "Smart Keyword Engine",
            "temperature": 0
        },

        "database": {
            "type": "PostgreSQL (Mocked)",
            "status": "connected"
        }
    }


# =========================================================
# QUERY ENDPOINT
# =========================================================

@app.post("/query")
def query(request: QueryRequest):

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )


    # -----------------------------------------------------
    # STEP 1: UNDERSTAND QUESTION
    # -----------------------------------------------------

    intent = understand_question(question)


    # -----------------------------------------------------
    # STEP 2: EXTRACT INTENT
    # -----------------------------------------------------

    metric = intent.get("metric")
    dimension = intent.get("dimension")
    operation = intent.get("operation")


    # Convert JSON null to Python None
    if dimension == "null":
        dimension = None


    # -----------------------------------------------------
    # STEP 3: VALIDATE METRIC
    # -----------------------------------------------------

    if metric not in SEMANTIC_METRICS:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric: {metric}"
        )


    # -----------------------------------------------------
    # STEP 4: VALIDATE DIMENSION
    # -----------------------------------------------------

    if dimension is not None:

        if dimension not in ALLOWED_DIMENSIONS:

            raise HTTPException(
                status_code=400,
                detail=f"Invalid dimension: {dimension}"
            )


    # -----------------------------------------------------
    # STEP 5: VALIDATE OPERATION
    # -----------------------------------------------------

    if operation not in ALLOWED_OPERATIONS:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation: {operation}"
        )


    # -----------------------------------------------------
    # STEP 6 & 7: GENERATE GOVERNED SQL & RESULTS (MOCK DATA)
    # -----------------------------------------------------

    if operation == "total":
        sql = f"SELECT SUM({metric}) AS value FROM sales"
        if metric == "revenue":
            val = 1250000.0
        elif metric == "cost":
            val = 750000.0
        elif metric == "profit":
            val = 500000.0
        else:
            val = 40.0
            
        results = [{"value": val}]

    elif operation == "breakdown":
        if dimension is None:
            raise HTTPException(status_code=400, detail="Breakdown requires a dimension")
        
        sql = f"SELECT {dimension} AS dimension, SUM({metric}) AS value FROM sales GROUP BY {dimension} ORDER BY value DESC"
        
        if dimension == "country":
            results = [
                {"dimension": "India", "value": 600000.0},
                {"dimension": "USA", "value": 400000.0},
                {"dimension": "UK", "value": 250000.0}
            ]
        elif dimension == "product":
            results = [
                {"dimension": "Laptop", "value": 700000.0},
                {"dimension": "Phone", "value": 350000.0},
                {"dimension": "Tablet", "value": 200000.0}
            ]
        else:
            results = [
                {"dimension": "2026-01", "value": 500000.0},
                {"dimension": "2026-02", "value": 750000.0}
            ]

    elif operation == "highest":
        if dimension is None:
            raise HTTPException(status_code=400, detail="Highest requires a dimension")
        sql = f"SELECT {dimension} AS dimension, SUM({metric}) AS value FROM sales GROUP BY {dimension} ORDER BY value DESC LIMIT 1"
        results = [{"dimension": "India" if dimension == "country" else "Laptop", "value": 700000.0}]

    else: # lowest
        if dimension is None:
            raise HTTPException(status_code=400, detail="Lowest requires a dimension")
        sql = f"SELECT {dimension} AS dimension, SUM({metric}) AS value FROM sales GROUP BY {dimension} ORDER BY value ASC LIMIT 1"
        results = [{"dimension": "UK" if dimension == "country" else "Tablet", "value": 200000.0}]


    # -----------------------------------------------------
    # STEP 9: API CALL TRANSPARENCY
    # -----------------------------------------------------

    api_call = {
        "endpoint": "/query",
        "method": "POST",
        "request": {
            "question": question
        },
        "semantic_intent": {
            "metric": metric,
            "dimension": dimension,
            "operation": operation
        }
    }


    # -----------------------------------------------------
    # STEP 10: FINAL RESPONSE
    # -----------------------------------------------------

    response = {
        "question": question,
        "agent": "MetricMind Agentic BI",
        "intent": intent,
        "metric": metric,
        "dimension": dimension,
        "operation": operation,
        "results": results,
        "sql": sql.strip(),
        "api_call": api_call
    }

    if operation == "total" and results:
        response["value"] = results[0].get("value")

    return response