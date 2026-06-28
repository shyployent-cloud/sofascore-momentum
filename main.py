from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
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

    # Get full event details to extract customId + slugs
    try:
        event_data = client.get_event_data(match_id)   # or direct API call
        event = event_data.get("event", {})
        custom_id = event.get("customId", "")
        home_slug = event.get("homeTeam", {}).get("slug", req.home.lower())
        away_slug = event.get("awayTeam", {}).get("slug", req.away.lower())
    except:
        custom_id = ""
        home_slug = req.home.lower()
        away_slug = req.away.lower()

    embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
    nice_url = f"https://www.sofascore.com/{home_slug}-{away_slug}/{custom_id}#id:{match_id}"

    return {
        "success": True,
        "match_id": match_id,
        "home": req.home,
        "away": req.away,
        "embed_url": embed_url,
        "embed_html": f'<iframe width="100%" height="286" src="{embed_url}" frameborder="0" scrolling="no"></iframe>',
        "custom_id": custom_id,
        "nice_url": nice_url,                    # <-- The full pretty URL
        "momentum_points": []                    # add real data if you want
    }

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
