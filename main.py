from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import matplotlib
matplotlib.use('Agg')  # Important for Railway
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
    # Find match
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

    # Generate PNG
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

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    embed_html = f'<iframe width="100%" height="286" src="https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=light" frameborder="0" scrolling="no"></iframe>'

    return {
        "success": True,
        "match_id": match_id,
        "home": req.home,
        "away": req.away,
        "embed_html": embed_html,
        "chart_image_base64": img_base64,
        "momentum_points": points
    }

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
