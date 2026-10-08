import json

import psycopg2

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


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
# DATABASE
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "metricmind",
    "user": "postgres",
    "password": "Roshanirs@2502"
}


def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
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
    "profit_margin": """
        CASE
            WHEN SUM(revenue) = 0 THEN 0
            ELSE ROUND(
                (SUM(revenue - cost) / SUM(revenue)) * 100,
                2
            )
        END
    """
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
# LLAMA 3.2
# =========================================================

llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


# =========================================================
# AI PROMPT
# =========================================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are MetricMind, an Agentic BI intent classifier.

Your job is ONLY to understand the user's analytics question.

You must NOT generate SQL.

Return ONLY valid JSON.
Do not write explanations.
Do not use markdown.
Do not use code fences.

Allowed metrics:
- revenue
- cost
- profit
- profit_margin

Allowed dimensions:
- country
- product
- sale_date

Allowed operations:
- total
- breakdown
- highest
- lowest

Rules:

1. Total revenue/cost/profit/margin:
   dimension = null
   operation = total

2. Metric by country/product/date:
   operation = breakdown

3. Highest metric by country/product/date:
   operation = highest

4. Lowest metric by country/product/date:
   operation = lowest

Example:
{{"metric":"revenue","dimension":"country","operation":"breakdown"}}

Return ONLY:
{{"metric":"revenue","dimension":"country","operation":"breakdown"}}
"""
    ),
    (
        "human",
        "{question}"
    )
])


# =========================================================
# AI UNDERSTANDING
# =========================================================

def understand_question(question: str):

    try:

        chain = prompt | llm

        response = chain.invoke({
            "question": question
        })

        print("========== AI RAW RESPONSE ==========")
        print(response.content)
        print("=====================================")

        content = response.content.strip()

        # Remove markdown code fences if Llama adds them
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        # Extract JSON object
        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:

            raise HTTPException(
                status_code=400,
                detail="AI returned invalid JSON"
            )

        content = content[start:end + 1]

        return json.loads(content)

    except json.JSONDecodeError as e:

        raise HTTPException(
            status_code=400,
            detail=f"AI returned invalid JSON: {str(e)}"
        )

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}"
        )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "project": "MetricMind",
        "status": "running",
        "ai": "Llama 3.2",
        "database": "PostgreSQL",
        "architecture": "Agentic Semantic BI"
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/db-test")
def db_test():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM sales")

        count = cursor.fetchone()[0]

        cursor.close()

        return {
            "database": "connected",
            "sales_rows": count
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database test failed: {str(e)}"
        )

    finally:

        connection.close()


# =========================================================
# ANALYTICS
# =========================================================

@app.get("/analytics")
def analytics():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        query = """
            SELECT
                COALESCE(SUM(revenue), 0),
                COALESCE(SUM(cost), 0),
                COALESCE(SUM(revenue - cost), 0),
                CASE
                    WHEN SUM(revenue) = 0 THEN 0
                    ELSE ROUND(
                        (SUM(revenue - cost) / SUM(revenue)) * 100,
                        2
                    )
                END
            FROM sales
        """

        cursor.execute(query)

        row = cursor.fetchone()

        cursor.close()

        return {
            "total_revenue": float(row[0]),
            "total_cost": float(row[1]),
            "total_profit": float(row[2]),
            "profit_margin": float(row[3])
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Analytics query failed: {str(e)}"
        )

    finally:

        connection.close()


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
            "model": "llama3.2",
            "temperature": 0
        },

        "database": {
            "type": "PostgreSQL",
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
    # STEP 1: AI UNDERSTANDS QUESTION
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
    # STEP 6: SEMANTIC METRIC
    # -----------------------------------------------------

    metric_expression = SEMANTIC_METRICS[metric]


    # -----------------------------------------------------
    # STEP 7: GENERATE GOVERNED SQL
    # -----------------------------------------------------

    if operation == "total":

        sql = f"""
            SELECT
                {metric_expression} AS value
            FROM sales
        """


    elif operation == "breakdown":

        if dimension is None:

            raise HTTPException(
                status_code=400,
                detail="Breakdown requires a dimension"
            )

        dimension_column = ALLOWED_DIMENSIONS[dimension]

        sql = f"""
            SELECT
                {dimension_column} AS dimension,
                {metric_expression} AS value
            FROM sales
            GROUP BY {dimension_column}
            ORDER BY value DESC
        """


    elif operation == "highest":

        if dimension is None:

            raise HTTPException(
                status_code=400,
                detail="Highest requires a dimension"
            )

        dimension_column = ALLOWED_DIMENSIONS[dimension]

        sql = f"""
            SELECT
                {dimension_column} AS dimension,
                {metric_expression} AS value
            FROM sales
            GROUP BY {dimension_column}
            ORDER BY value DESC
            LIMIT 1
        """


    elif operation == "lowest":

        if dimension is None:

            raise HTTPException(
                status_code=400,
                detail="Lowest requires a dimension"
            )

        dimension_column = ALLOWED_DIMENSIONS[dimension]

        sql = f"""
            SELECT
                {dimension_column} AS dimension,
                {metric_expression} AS value
            FROM sales
            GROUP BY {dimension_column}
            ORDER BY value ASC
            LIMIT 1
        """


    # -----------------------------------------------------
    # STEP 8: EXECUTE SQL
    # -----------------------------------------------------

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        results = []

        for row in rows:

            item = {}

            for index, column in enumerate(columns):

                value = row[index]

                if hasattr(value, "isoformat"):

                    value = value.isoformat()

                elif hasattr(value, "__float__"):

                    value = float(value)

                item[column] = value

            results.append(item)

        cursor.close()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )

    finally:

        connection.close()


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


    # Add direct value for total queries

    if operation == "total" and results:

        response["value"] = results[0].get("value")


    return response