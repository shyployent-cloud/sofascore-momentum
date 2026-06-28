from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import matplotlib.pyplot as plt
import io
import base64
import os
from datetime import datetime

app = FastAPI(title="Sofascore Momentum")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

@app.post("/get-match")
def get_match(req: MatchRequest):
    # Find match (expand later)
    match_id = None
    if "panama" in req.home.lower() and "england" in req.away.lower():
        match_id = 15186676
    
    if not match_id:
        return {"success": False, "error": "Match not found"}

    try:
        graph = client.get_event_graph(match_id)
        points = graph.get("graphPoints", [])
    except:
        points = []

    # Generate PNG chart
    minutes = [p["minute"] for p in points]
    values = [p["value"] for p in points]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(minutes, values, color='blue', linewidth=2)
    ax.fill_between(minutes, values, where=[v > 0 for v in values], color='green', alpha=0.3)
    ax.fill_between(minutes, values, where=[v < 0 for v in values], color='red', alpha=0.3)
    ax.set_title(f"{req.home} vs {req.away} Momentum")
    ax.set_xlabel("Minute")
    ax.set_ylabel("Momentum")
    ax.grid(True)

    # Save to base64 for URL
    buf = io.BytesIO
