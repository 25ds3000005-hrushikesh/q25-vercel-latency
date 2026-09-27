from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import statistics


app = FastAPI()


# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request format
class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float


# Telemetry data
DATA = [
    {"region": "apac", "latency_ms": 159.4, "uptime_pct": 99.49},
    {"region": "apac", "latency_ms": 112.88, "uptime_pct": 97.308},
    {"region": "apac", "latency_ms": 140.94, "uptime_pct": 97.996},
    {"region": "apac", "latency_ms": 202.51, "uptime_pct": 99.015},
    {"region": "apac", "latency_ms": 220.95, "uptime_pct": 98.861},
    {"region": "apac", "latency_ms": 109.87, "uptime_pct": 97.762},
    {"region": "apac", "latency_ms": 221.79, "uptime_pct": 98.736},
    {"region": "apac", "latency_ms": 152.6, "uptime_pct": 98.83},
    {"region": "apac", "latency_ms": 143.07, "uptime_pct": 98.102},
    {"region": "apac", "latency_ms": 141.95, "uptime_pct": 99.374},
    {"region": "apac", "latency_ms": 123.84, "uptime_pct": 98.681},
    {"region": "apac", "latency_ms": 207.85, "uptime_pct": 99.384},

    {"region": "emea", "latency_ms": 169.5, "uptime_pct": 99.283},
    {"region": "emea", "latency_ms": 162.82, "uptime_pct": 97.389},
    {"region": "emea", "latency_ms": 122.66, "uptime_pct": 98.399},
    {"region": "emea", "latency_ms": 163.43, "uptime_pct": 97.306},
    {"region": "emea", "latency_ms": 219.72, "uptime_pct": 98.3},
    {"region": "emea", "latency_ms": 103.51, "uptime_pct": 99.071},
    {"region": "emea", "latency_ms": 180.68, "uptime_pct": 98.2},
    {"region": "emea", "latency_ms": 206.17, "uptime_pct": 97.334},
    {"region": "emea", "latency_ms": 150, "uptime_pct": 98.849},
    {"region": "emea", "latency_ms": 184.68, "uptime_pct": 98.923},
    {"region": "emea", "latency_ms": 173.2, "uptime_pct": 98.921},
    {"region": "emea", "latency_ms": 218.79, "uptime_pct": 98.162},

    {"region": "amer", "latency_ms": 180.27, "uptime_pct": 98.288},
    {"region": "amer", "latency_ms": 122.63, "uptime_pct": 97.917},
    {"region": "amer", "latency_ms": 155.3, "uptime_pct": 99.193},
    {"region": "amer", "latency_ms": 201.28, "uptime_pct": 97.424},
    {"region": "amer", "latency_ms": 185.98, "uptime_pct": 98.469},
    {"region": "amer", "latency_ms": 147.84, "uptime_pct": 97.155},
    {"region": "amer", "latency_ms": 98.58, "uptime_pct": 97.404},
    {"region": "amer", "latency_ms": 137.97, "uptime_pct": 98.578},
    {"region": "amer", "latency_ms": 136.64, "uptime_pct": 98.923},
    {"region": "amer", "latency_ms": 217.64, "uptime_pct": 98.75},
    {"region": "amer", "latency_ms": 107.1, "uptime_pct": 97.702},
    {"region": "amer", "latency_ms": 121.08, "uptime_pct": 97.228},
]


# Handle CORS preflight request explicitly
@app.options("/")
def options():
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.post("/")
def analytics(request: AnalyticsRequest, response: Response):

    result = {}

    for region in request.regions:

        records = [
            row for row in DATA
            if row["region"] == region
        ]

        if not records:
            continue

        latencies = [row["latency_ms"] for row in records]
        uptimes = [row["uptime_pct"] for row in records]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),

            "p95_latency": statistics.quantiles(
                latencies,
                n=100,
                method="inclusive"
            )[94],

            "avg_uptime": sum(uptimes) / len(uptimes),

            "breaches": sum(
                latency > request.threshold_ms
                for latency in latencies
            )
        }

    # Explicitly add CORS header to POST response
    response.headers["Access-Control-Allow-Origin"] = "*"

    return result