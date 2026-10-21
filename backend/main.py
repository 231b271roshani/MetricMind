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
    version="1.1.0"
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
    allow_headers=["*"]
)


# =========================================================
# DATABASE
# =========================================================

DB_CONFIG = {
    "host": "127.0.0.1",
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
You are MetricMind, an analytics intent classifier.

Do not generate SQL.
Return only valid JSON without markdown.

Allowed metrics:
revenue, cost, profit, profit_margin

Allowed dimensions:
country, product, sale_date

Allowed operations:
total, breakdown, highest, lowest

Rules:
- Total metric questions use dimension null and operation total.
- Metric grouped by a dimension uses breakdown.
- Highest metric by a dimension uses highest.
- Lowest metric by a dimension uses lowest.

Example:
{{"metric":"revenue","dimension":"country","operation":"breakdown"}}
"""
    ),
    ("human", "{question}")
])


# =========================================================
# AI UNDERSTANDING
# =========================================================

def understand_question(question: str):
    try:
        chain = prompt | llm
        response = chain.invoke({"question": question})

        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "").strip()

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise HTTPException(
                status_code=400,
                detail="AI returned invalid JSON"
            )

        return json.loads(content[start:end + 1])

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
# MULTI-STEP REASONING — WEEK 3
# =========================================================

def handle_multi_step_question(question: str):
    normalized = question.lower()

    is_multi_step = (
        "highest revenue" in normalized
        and "profit" in normalized
        and (
            "country" in normalized
            or "countries" in normalized
        )
    )

    if not is_multi_step:
        return None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # STEP 1: Find the country with highest revenue.
            sql_step_1 = """
                SELECT
                    country,
                    SUM(revenue) AS revenue
                FROM sales
                GROUP BY country
                ORDER BY revenue DESC, country ASC
                LIMIT 1
            """

            cursor.execute(sql_step_1)
            top_country = cursor.fetchone()

            if not top_country:
                return {
                    "steps": [],
                    "results": [],
                    "answer": "No sales data was found."
                }

            country, revenue = top_country

            # STEP 2: Calculate profit for that country.
            sql_step_2 = """
                SELECT
                    COALESCE(SUM(revenue - cost), 0) AS profit
                FROM sales
                WHERE country = %s
            """

            cursor.execute(sql_step_2, (country,))
            profit_row = cursor.fetchone()
            profit = profit_row[0]

            result = {
                "country": country,
                "revenue": float(revenue),
                "profit": float(profit)
            }

            answer = (
                f"{country} has the highest revenue of "
                f"{float(revenue):,.2f}, with a profit of "
                f"{float(profit):,.2f}."
            )

            return {
                "steps": [
                    {
                        "step": 1,
                        "description": (
                            "Find the country with the highest revenue"
                        ),
                        "sql": sql_step_1.strip()
                    },
                    {
                        "step": 2,
                        "description": (
                            "Calculate profit for the selected country"
                        ),
                        "sql": sql_step_2.strip(),
                        "parameters": {"country": country}
                    }
                ],
                "results": [result],
                "answer": answer
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multi-step reasoning failed: {str(e)}"
        )

    finally:
        connection.close()


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
        "architecture": "Agentic Semantic BI",
        "week": 3
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/db-test")
def db_test():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sales")
            count = cursor.fetchone()[0]

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
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(revenue), 0),
                    COALESCE(SUM(cost), 0),
                    COALESCE(SUM(revenue - cost), 0),
                    CASE
                        WHEN COALESCE(SUM(revenue), 0) = 0
                        THEN 0
                        ELSE ROUND(
                            (
                                SUM(revenue - cost)
                                / SUM(revenue)
                            ) * 100,
                            2
                        )
                    END
                FROM sales
            """)

            row = cursor.fetchone()

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
            "status": "configured"
        }
    }


# =========================================================
# QUERY ENDPOINT
# =========================================================

def save_query_history(
    question: str,
    metric=None,
    dimension=None,
    operation=None,
    status="success",
    answer=None
):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO query_history
                    (question, metric, dimension, operation, status, answer)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    question,
                    metric,
                    dimension,
                    operation,
                    status,
                    answer
                )
            )
        connection.commit()
    finally:
        connection.close()


@app.get("/query-history")
def get_query_history(limit: int = 20):
    limit = max(1, min(limit, 100))
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, question, metric, dimension, operation,
                       status, answer, created_at
                FROM query_history
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (limit,)
            )
            rows = cursor.fetchall()

        return {
            "count": len(rows),
            "history": [
                {
                    "id": row[0],
                    "question": row[1],
                    "metric": row[2],
                    "dimension": row[3],
                    "operation": row[4],
                    "status": row[5],
                    "answer": row[6],
                    "created_at": row[7].isoformat()
                }
                for row in rows
            ]
        }
    finally:
        connection.close()

@app.post("/query")
def query(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

   
    # WEEK 3: MULTI-STEP REASONING
    multi_step_result = handle_multi_step_question(question)

   
    if multi_step_result is not None:
        save_query_history(
            question=question,
            metric="revenue_and_profit",
            dimension=None,
            operation="multi_step",
            status="success",
            answer=multi_step_result["answer"]
        )

        return {

            "question": question,
            "agent": "MetricMind Agentic BI",
            "intent": {
                "type": "multi_step_reasoning",
                "steps": multi_step_result["steps"]
            },
            "metric": "revenue_and_profit",
            "dimension": None,
            "operation": "multi_step",
            "multi_step": True,
            "steps": multi_step_result["steps"],
            "results": multi_step_result["results"],
            "answer": multi_step_result["answer"],
            "sql": "\n\n".join(
                step["sql"] for step in multi_step_result["steps"]
            ),
            "api_call": {
                "endpoint": "/query",
                "method": "POST",
                "request": {"question": question},
                "semantic_intent": {
                    "type": "multi_step_reasoning"
                }
            }
        }

          


    # EXISTING SINGLE-STEP AI WORKFLOW
    intent = understand_question(question)

    metric = intent.get("metric")
    dimension = intent.get("dimension")
    operation = intent.get("operation")

    if dimension == "null":
        dimension = None

    if not metric or metric not in SEMANTIC_METRICS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to identify a valid metric. "
                "Please ask about revenue, cost, profit, or profit_margin."
            )
        )

    if dimension is not None:
        if dimension not in ALLOWED_DIMENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid dimension: {dimension}"
            )

    if operation not in ALLOWED_OPERATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation: {operation}"
        )

    metric_expression = SEMANTIC_METRICS[metric]

    if operation == "total":
        sql = f"""
            SELECT {metric_expression} AS value
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

    else:  # lowest
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

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )

    finally:
        connection.close()

    response = {
        "question": question,
        "agent": "MetricMind Agentic BI",
        "intent": intent,
        "metric": metric,
        "dimension": dimension,
        "operation": operation,
        "results": results,
        "sql": sql.strip(),
        "api_call": {
            "endpoint": "/query",
            "method": "POST",
            "request": {"question": question},
            "semantic_intent": {
                "metric": metric,
                "dimension": dimension,
                "operation": operation
            }
        }
    }

    if operation == "total" and results:
        response["value"] = results[0].get("value")

    return response