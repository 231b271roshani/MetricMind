"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/* ============================================================
   TYPES
============================================================ */

type AnalyticsData = {
  total_revenue: number;
  total_cost: number;
  total_profit: number;
  profit_margin: number;
};

type QueryResult = {
  question?: string;

  agent?: string;

  intent?: {
    metric: string;
    dimension: string | null;
    operation: string;
  };

  metric?: string;

  dimension?: string | null;

  operation?: string;

  value?: number;

  results?: {
    dimension: string;
    value: number;
  }[];

  answer?: string;

  sql?: string;

  supported_metrics?: string[];
};


/* ============================================================
   MAIN PAGE
============================================================ */

export default function Home() {

  const [data, setData] =
    useState<AnalyticsData | null>(null);

  const [question, setQuestion] =
    useState("");

  const [queryResult, setQueryResult] =
    useState<QueryResult | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [asking, setAsking] =
    useState(false);

  const [error, setError] =
    useState("");


  /* ==========================================================
     LOAD DASHBOARD ANALYTICS
  ========================================================== */

  useEffect(() => {

    fetch("http://127.0.0.1:8001/analytics")

      .then((response) => {

        if (!response.ok) {
          throw new Error("API error");
        }

        return response.json();
      })

      .then((result) => {

        setData(result);

        setLoading(false);

        setError("");
      })

      .catch(() => {

        setError(
          "Unable to connect to MetricMind API"
        );

        setLoading(false);
      });

  }, []);


  /* ==========================================================
     ASK METRICMIND
  ========================================================== */

  const askMetricMind = async () => {

    if (!question.trim()) {
      return;
    }

    setAsking(true);

    setQueryResult(null);

    setError("");

    try {

      const response = await fetch(
        "http://127.0.0.1:8001/query",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question: question,
          }),
        }
      );


      const result =
        await response.json();


      if (!response.ok) {

        throw new Error(
          result.detail || "Query failed"
        );
      }


      setQueryResult(result);

    }

    catch (err) {

      setQueryResult({
        answer:
          err instanceof Error
            ? err.message
            : "Unable to connect to MetricMind API.",
      });

    }

    finally {

      setAsking(false);
    }
  };


  /* ==========================================================
     FORMAT VALUE
  ========================================================== */

  const formatValue = (
    value: number,
    metric?: string
  ) => {

    if (metric === "profit_margin") {

      return `${value.toFixed(2)}%`;
    }

    return `₹${value.toLocaleString("en-IN")}`;
  };


  /* ==========================================================
     FORMAT TEXT
  ========================================================== */

  const formatText = (value?: string | null) => {

    if (!value) {
      return "None";
    }

    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) =>
        char.toUpperCase()
      );
  };


  /* ==========================================================
     CHART TOOLTIP
  ========================================================== */

  const CustomTooltip = ({
    active,
    payload,
    label,
  }: any) => {

    if (
      !active ||
      !payload ||
      !payload.length
    ) {
      return null;
    }


    const value =
      payload[0].value;


    return (

      <div
        style={{
          background: "#111827",
          color: "white",

          padding: "12px 16px",

          borderRadius: "10px",

          boxShadow:
            "0 5px 20px rgba(0,0,0,0.2)",
        }}
      >

        <div
          style={{
            fontWeight: "bold",
            marginBottom: "5px",
          }}
        >
          {label}
        </div>

        <div>
          {formatValue(
            Number(value),
            queryResult?.metric
          )}
        </div>

      </div>
    );
  };


  /* ==========================================================
     PAGE UI
  ========================================================== */

  return (

    <main
      style={{
        minHeight: "100vh",

        background: "#f5f7fb",

        padding: "40px",

        fontFamily:
          "Arial, Helvetica, sans-serif",

        color: "#111827",
      }}
    >

      <div
        style={{
          maxWidth: "1200px",

          margin: "0 auto",
        }}
      >


        {/* ==================================================
           HEADER
        ================================================== */}

        <header
          style={{
            background: "#111827",

            color: "white",

            padding: "32px",

            borderRadius: "18px",

            marginBottom: "28px",

            boxShadow:
              "0 5px 20px rgba(0,0,0,0.12)",
          }}
        >

          <h1
            style={{
              margin: 0,

              fontSize: "38px",

              color: "white",
            }}
          >
            MetricMind
          </h1>


          <p
            style={{
              marginTop: "8px",

              color: "#cbd5e1",

              fontSize: "18px",
            }}
          >
            Agentic Semantic BI Engine
          </p>


          <span
            style={{
              display: "inline-block",

              marginTop: "12px",

              padding:
                "7px 14px",

              background: "#16a34a",

              color: "white",

              borderRadius: "20px",

              fontSize: "13px",

              fontWeight: "bold",
            }}
          >
            ● Live
          </span>

        </header>


        {/* ==================================================
           ERROR
        ================================================== */}

        {error && (

          <div
            style={{
              background: "#fee2e2",

              color: "#991b1b",

              padding: "15px",

              borderRadius: "10px",

              marginBottom: "20px",
            }}
          >
            {error}
          </div>

        )}


        {/* ==================================================
           KPI CARDS
        ================================================== */}

        <div
          style={{
            display: "grid",

            gridTemplateColumns:
              "repeat(4, 1fr)",

            gap: "20px",

            marginBottom: "30px",
          }}
        >

          <MetricCard
            title="Total Revenue"

            value={
              loading
                ? "Loading..."
                : `₹${data?.total_revenue?.toLocaleString(
                    "en-IN"
                  )}`
            }
          />


          <MetricCard
            title="Total Cost"

            value={
              loading
                ? "Loading..."
                : `₹${data?.total_cost?.toLocaleString(
                    "en-IN"
                  )}`
            }
          />


          <MetricCard
            title="Total Profit"

            value={
              loading
                ? "Loading..."
                : `₹${data?.total_profit?.toLocaleString(
                    "en-IN"
                  )}`
            }
          />


          <MetricCard
            title="Profit Margin"

            value={
              loading
                ? "Loading..."
                : `${data?.profit_margin}%`
            }
          />

        </div>


        {/* ==================================================
           ASK METRICMIND
        ================================================== */}

        <section
          style={{
            background: "white",

            padding: "30px",

            borderRadius: "18px",

            marginBottom: "30px",

            boxShadow:
              "0 4px 20px rgba(0,0,0,0.06)",
          }}
        >

          <h2
            style={{
              marginTop: 0,

              color: "#111827",
            }}
          >
            Ask MetricMind 🤖
          </h2>


          <p
            style={{
              color: "#64748b",

              marginBottom: "18px",
            }}
          >
            Ask a business question in
            natural language.
          </p>


          {/* INPUT */}

          <div
            style={{
              display: "flex",

              gap: "12px",
            }}
          >

            <input

              value={question}

              onChange={(e) =>
                setQuestion(
                  e.target.value
                )
              }

              onKeyDown={(e) => {

                if (e.key === "Enter") {

                  askMetricMind();
                }

              }}

              placeholder=
                "What is the revenue by country?"

              style={{
                flex: 1,

                padding: "16px",

                border:
                  "1px solid #cbd5e1",

                borderRadius: "10px",

                fontSize: "16px",

                color: "#111827",

                background: "white",

                outline: "none",
              }}
            />


            <button

              onClick={askMetricMind}

              disabled={asking}

              style={{
                padding:
                  "14px 28px",

                background: "#111827",

                color: "white",

                border: "none",

                borderRadius: "10px",

                cursor:
                  asking
                    ? "not-allowed"
                    : "pointer",

                fontWeight: "bold",

                fontSize: "15px",
              }}
            >

              {asking
                ? "Thinking..."
                : "Ask"}

            </button>

          </div>


          {/* EXAMPLE QUESTIONS */}

          <div
            style={{
              display: "flex",

              flexWrap: "wrap",

              gap: "10px",

              marginTop: "16px",
            }}
          >

            {[
              "What is the total revenue?",
              "Show me revenue by country",
              "Show me profit by country",
              "Which product has the highest profit?",
            ].map((example) => (

              <button
                key={example}

                onClick={() =>
                  setQuestion(example)
                }

                style={{
                  padding:
                    "8px 12px",

                  border:
                    "1px solid #cbd5e1",

                  background: "white",

                  color: "#475569",

                  borderRadius: "8px",

                  cursor: "pointer",

                  fontSize: "13px",
                }}
              >
                {example}
              </button>

            ))}

          </div>


          {/* =================================================
             QUERY RESULT
          ================================================= */}

          {queryResult && (

            <div
              style={{
                marginTop: "24px",

                padding: "22px",

                background:
                  "#f8fafc",

                border:
                  "1px solid #e2e8f0",

                borderRadius: "12px",
              }}
            >


              {/* =================================================
                 AI RESULT HEADER
              ================================================= */}

              {queryResult.question && (

                <div
                  style={{
                    marginBottom: "20px",
                  }}
                >

                  <h3
                    style={{
                      marginTop: 0,

                      color: "#111827",

                      fontSize: "22px",
                    }}
                  >
                    MetricMind Result
                  </h3>

                  <p
                    style={{
                      color: "#64748b",
                    }}
                  >
                    Question:{" "}
                    <strong
                      style={{
                        color: "#111827",
                      }}
                    >
                      {queryResult.question}
                    </strong>
                  </p>

                </div>

              )}


              {/* =================================================
                 AGENT INTENT
              ================================================= */}

              {queryResult.metric && (

                <div
                  style={{
                    display: "grid",

                    gridTemplateColumns:
                      "repeat(3, 1fr)",

                    gap: "12px",

                    marginBottom: "20px",
                  }}
                >

                  <InfoCard
                    title="Metric"
                    value={formatText(
                      queryResult.metric
                    )}
                  />

                  <InfoCard
                    title="Dimension"
                    value={formatText(
                      queryResult.dimension
                    )}
                  />

                  <InfoCard
                    title="Operation"
                    value={formatText(
                      queryResult.operation
                    )}
                  />

                </div>

              )}


              {/* =================================================
                 GROUPED RESULT
              ================================================= */}{queryResult.results &&
queryResult.results.length > 0 &&
queryResult.dimension ? (

                <>

                  {/* =================================================
                     BAR CHART
                  ================================================= */}

                  <div
                    style={{
                      width: "100%",

                      height: "380px",

                      background: "white",

                      borderRadius: "12px",

                      padding:
                        "20px",

                      boxSizing:
                        "border-box",

                      marginBottom:
                        "20px",
                    }}
                  >

                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >

                      <BarChart

                        data={
                          queryResult.results
                        }

                        margin={{
                          top: 10,

                          right: 20,

                          left: 10,

                          bottom: 10,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray=
                            "3 3"
                        />

                        <XAxis
                          dataKey=
                            "dimension"

                          tick={{
                            fill:
                              "#475569",
                          }}
                        />

                        <YAxis

                          tick={{
                            fill:
                              "#475569",
                          }}

                          tickFormatter={(
                            value
                          ) =>
                            `₹${Number(
                              value
                            ).toLocaleString(
                              "en-IN"
                            )}`
                          }
                        />


                        <Tooltip
                          content={
                            <CustomTooltip />
                          }
                        />


                        <Bar

                          dataKey="value"

                          name={
                            queryResult.metric
                          }

                          fill="#111827"

                          radius={[
                            8,
                            8,
                            0,
                            0,
                          ]}
                        />

                      </BarChart>

                    </ResponsiveContainer>

                  </div>


                  {/* =================================================
                     RESULT LIST
                  ================================================= */}

                  <div
                    style={{
                      display: "grid",

                      gap: "10px",

                      marginTop: "20px",
                    }}
                  >

                    {queryResult.results.map(
                      (
                        item,
                        index
                      ) => (

                        <div

                          key={index}

                          style={{
                            display:
                              "flex",

                            justifyContent:
                              "space-between",

                            alignItems:
                              "center",

                            padding:
                              "14px 16px",

                            background:
                              "white",

                            borderRadius:
                              "8px",

                            border:
                              "1px solid #e5e7eb",
                          }}
                        >

                          <strong
                            style={{
                              color:
                                "#111827",
                            }}
                          >
                            {item.dimension}
                          </strong>


                          <strong
                            style={{
                              color:
                                "#111827",
                            }}
                          >
                            {formatValue(
                              item.value,

                              queryResult.metric
                            )}
                          </strong>

                        </div>

                      )
                    )}

                  </div>

                </>

              ) : queryResult.value !==
                undefined ? (

                /* =================================================
                   TOTAL RESULT
                ================================================= */

                <>

                  <p
                    style={{
                      margin: 0,

                      color: "#64748b",
                    }}
                  >
                    Metric:{" "}

                    <strong
                      style={{
                        color: "#111827",
                      }}
                    >
                      {formatText(
                        queryResult.metric
                      )}
                    </strong>
                  </p>


                  <h2
                    style={{
                      margin:
                        "10px 0 0",

                      color:
                        "#111827",
                    }}
                  >
                    {formatValue(
                      queryResult.value,

                      queryResult.metric
                    )}
                  </h2>

                </>

              ) : (

             
                /* =================================================
                   ERROR RESULT
                ================================================= */
                <p style={{ color: "#991b1b" }}>
                  {queryResult.answer}
                </p>
              )}


              {/* =================================================
                 VIEW SQL
              ================================================= */}

              {queryResult.sql && (

                <details
                  style={{
                    marginTop: "20px",

                    background: "#111827",

                    borderRadius: "10px",

                    overflow: "hidden",
                  }}
                >

                  <summary
                    style={{
                      cursor: "pointer",

                      padding: "14px 16px",

                      color: "white",

                      fontWeight: "bold",
                    }}
                  >
                    View Generated SQL
                  </summary>

                  <pre
                    style={{
                      margin: 0,

                      padding: "18px",

                      color: "#67e8f9",

                      background:
                        "#020617",

                      overflowX:
                        "auto",

                      fontSize: "13px",

                      lineHeight: 1.6,
                    }}
                  >
                    {queryResult.sql}
                  </pre>

                </details>

              )}


              {/* =================================================
                 VIEW AI INTENT
              ================================================= */}

              {queryResult.intent && (

                <details
                  style={{
                    marginTop: "12px",

                    background: "#111827",

                    borderRadius: "10px",

                    overflow: "hidden",
                  }}
                >

                  <summary
                    style={{
                      cursor: "pointer",

                      padding: "14px 16px",

                      color: "white",

                      fontWeight: "bold",
                    }}
                  >
                    View AI Intent
                  </summary>

                  <pre
                    style={{
                      margin: 0,

                      padding: "18px",

                      color: "#86efac",

                      background:
                        "#020617",

                      overflowX:
                        "auto",

                      fontSize: "13px",

                      lineHeight: 1.6,
                    }}
                  >
                    {JSON.stringify(
                      queryResult.intent,
                      null,
                      2
                    )}
                  </pre>

                </details>

              )}

            </div>

          )}

        </section>


        {/* ==================================================
           ARCHITECTURE
        ================================================== */}

        <h2
          style={{
            color: "#111827",

            marginBottom: "18px",
          }}
        >
          MetricMind Architecture
        </h2>


        <div
          style={{
            display: "grid",

            gridTemplateColumns:
              "repeat(4, 1fr)",

            gap: "20px",
          }}
        >

          <ArchitectureCard
            title="Natural Language"

            description=
              "User asks questions in plain English."
          />


          <ArchitectureCard
            title="AI Agent"

            description=
              "Llama 3.2 understands the user's analytical intent."
          />


          <ArchitectureCard
            title="Semantic Layer"

            description=
              "Uses governed business metrics and dimensions."
          />


          <ArchitectureCard
            title="PostgreSQL"

            description=
              "Executes analytics on the sales data."
          />

        </div>


        {/* ==================================================
           FOOTER
        ================================================== */}

        <footer
          style={{
            marginTop: "40px",

            padding:
              "20px 0",

            borderTop:
              "1px solid #e2e8f0",

            color: "#64748b",

            fontSize: "14px",
          }}
        >
          MetricMind • Agentic Semantic BI Engine
        </footer>

      </div>

    </main>
  );
}


/* ============================================================
   METRIC CARD
============================================================ */

function MetricCard({
  title,
  value,
}: {
  title: string;

  value: string;
}) {

  return (

    <div
      style={{
        background: "white",

        padding: "25px",

        borderRadius: "14px",

        boxShadow:
          "0 3px 15px rgba(0,0,0,0.05)",
      }}
    >

      <p
        style={{
          margin: 0,

          color: "#64748b",

          fontSize: "15px",
        }}
      >
        {title}
      </p>


      <h2
        style={{
          margin:
            "10px 0 0",

          color: "#111827",

          fontSize: "27px",
        }}
      >
        {value}
      </h2>

    </div>

  );
}


/* ============================================================
   INFO CARD
============================================================ */

function InfoCard({
  title,
  value,
}: {
  title: string;

  value: string;
}) {

  return (

    <div
      style={{
        background: "white",

        padding: "15px",

        borderRadius: "10px",

        border:
          "1px solid #e2e8f0",
      }}
    >

      <p
        style={{
          margin: 0,

          color: "#64748b",

          fontSize: "12px",
        }}
      >
        {title}
      </p>

      <strong
        style={{
          display: "block",

          marginTop: "5px",

          color: "#111827",
        }}
      >
        {value}
      </strong>

    </div>

  );
}


/* ============================================================
   ARCHITECTURE CARD
============================================================ */

function ArchitectureCard({
  title,
  description,
}: {
  title: string;

  description: string;
}) {

  return (

    <div
      style={{
        background: "white",

        padding: "24px",

        borderRadius: "14px",

        boxShadow:
          "0 3px 15px rgba(0,0,0,0.05)",
      }}
    >

      <h3
        style={{
          marginTop: 0,

          color: "#111827",
        }}
      >
        {title}
      </h3>


      <p
        style={{
          color: "#64748b",

          lineHeight: 1.6,
        }}
      >
        {description}
      </p>

    </div>

  );
}