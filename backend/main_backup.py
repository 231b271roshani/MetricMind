from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2


# ============================================================
# APP
# ============================================================

app = FastAPI(title="MetricMind API")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="metricmind",
        user="postgres",
        password="Roshanirs@2502"
    )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "MetricMind API is running!"
    }


# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/db-test")
def db_test():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sales;")

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "sales_rows": count
    }


# ============================================================
# ANALYTICS
# ============================================================

@app.get("/analytics")
def analytics():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(revenue),
            SUM(cost),
            SUM(revenue - cost),
            ROUND(
                (SUM(revenue - cost) /
                NULLIF(SUM(revenue), 0)) * 100,
                2
            )
        FROM sales;
    """)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "total_revenue": float(result[0]),
        "total_cost": float(result[1]),
        "total_profit": float(result[2]),
        "profit_margin": float(result[3])
    }


# ============================================================
# SEMANTIC METRICS
# ============================================================

SEMANTIC_METRICS = {

    "revenue": "SUM(revenue)",

    "cost": "SUM(cost)",

    "profit": "SUM(revenue - cost)",

    "profit_margin": """
        ROUND(
            (SUM(revenue - cost) /
            NULLIF(SUM(revenue), 0)) * 100,
            2
        )
    """
}


# ============================================================
# SEMANTIC LAYER
# ============================================================

@app.get("/semantic-metrics")
def semantic_metrics():

    return {

        "metrics": {

            "revenue": {
                "label": "Total Revenue",
                "definition": "SUM(revenue)"
            },

            "cost": {
                "label": "Total Cost",
                "definition": "SUM(cost)"
            },

            "profit": {
                "label": "Total Profit",
                "definition": "SUM(revenue - cost)"
            },

            "profit_margin": {
                "label": "Profit Margin",
                "definition": "(Total Profit / Total Revenue) × 100"
            }
        },

        "dimensions": [
            "country",
            "product",
            "sale_date"
        ]
    }


# ============================================================
# QUERY REQUEST
# ============================================================

class QueryRequest(BaseModel):
    question: str


# ============================================================
# NATURAL LANGUAGE QUERY ENGINE
# ============================================================

@app.post("/query")
def query_metric(request: QueryRequest):

    question = request.question.lower().strip()

    # --------------------------------------------------------
    # Detect Metric
    # --------------------------------------------------------

    if "profit margin" in question or "margin" in question:

        metric = "profit_margin"

    elif "revenue" in question or "sales" in question:

        metric = "revenue"

    elif "cost" in question:

        metric = "cost"

    elif "profit" in question:

        metric = "profit"

    else:

        return {
            "answer": "I could not identify a supported metric.",

            "supported_metrics": [
                "revenue",
                "cost",
                "profit",
                "profit margin"
            ]
        }

    # --------------------------------------------------------
    # Detect Dimension
    # --------------------------------------------------------

    if "country" in question or "countries" in question:

        dimension = "country"

    elif "product" in question or "products" in question:

        dimension = "product"

    elif "date" in question or "time" in question:

        dimension = "sale_date"

    else:

        dimension = None

    # --------------------------------------------------------
    # Detect Ranking
    # --------------------------------------------------------

    highest = (
        "highest" in question
        or "maximum" in question
        or "max" in question
        or "top" in question
        or "best" in question
    )

    lowest = (
        "lowest" in question
        or "minimum" in question
        or "min" in question
        or "worst" in question
    )

    # ========================================================
    # TOTAL METRIC
    # ========================================================

    if dimension is None:

        conn = get_connection()
        cursor = conn.cursor()

        query = f"""
            SELECT {SEMANTIC_METRICS[metric]}
            FROM sales;
        """

        cursor.execute(query)

        result = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        if result is None:
            result = 0

        return {

            "question": request.question,

            "metric": metric,

            "dimension": None,

            "value": float(result)
        }

    # ========================================================
    # GROUP BY QUERY
    # ========================================================

    query = f"""
        SELECT
            {dimension},
            {SEMANTIC_METRICS[metric]} AS metric_value
        FROM sales
        GROUP BY {dimension}
    """

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    if highest:

        query += " ORDER BY metric_value DESC"

    elif lowest:

        query += " ORDER BY metric_value ASC"

    else:

        query += f" ORDER BY {dimension}"

    # --------------------------------------------------------
    # Limit for ranking
    # --------------------------------------------------------

    if highest or lowest:

        query += " LIMIT 1"

    query += ";"

    # ========================================================
    # Execute Query
    # ========================================================

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # ========================================================
    # Format Results
    # ========================================================

    results = []

    for row in rows:

        value = row[1]

        if value is None:
            value = 0

        results.append({
            "dimension": str(row[0]),
            "value": float(value)
        })

    # ========================================================
    # Return
    # ========================================================

    return {

        "question": request.question,

        "metric": metric,

        "dimension": dimension,

        "results": results
    }