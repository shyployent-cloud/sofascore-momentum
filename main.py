from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os

app = FastAPI(title="Sofascore Momentum")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id = None
    if "panama" in req.home.lower() and "england" in req.away.lower():
        match_id = 15186676
    
    if not match_id:
        return {"success": False, "error": "Match not found - add date"}

    try:
        graph = client.get_event_graph(match_id)
        points = graph.get("graphPoints", [])
    except:
        points = []

    # Nicer Dark Chart
    minutes = [p["minute"] for p in points]
    values = [p["value"] for p in points]

    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0f0f0f')
    ax.set_facecolor('#1a1a1a')
    
    ax.plot(minutes, values, color='#00b4d8', linewidth=3, marker='o', markersize=5, label='Momentum')
    ax.fill_between(minutes, values, 0, where=[v > 0 for v in values], color='#00ff9d', alpha=0.4, label='Home Advantage')
    ax.fill_between(minutes, values, 0, where=[v < 0 for v in values], color='#ff4d4d', alpha=0.4, label='Away Advantage')
    
    ax.set_title(f"{req.home} vs {req.away} Momentum", color='white', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel("Minute
