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
    # Find match (expand later)
    match_id = None
    if "panama" in req.home.lower() and "england" in req.away.lower():
        match_id = 15186676  # known working ID
    
    if not match_id:
        return {"success": False, "error": "Match not found - add date"}

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
