from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum API")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str   # Required for reliable results (as per API docs)

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id, custom_id = find_match(req.home, req.away, req.date)
    if match_id:
        embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
        nice_url = f"https://www.sofascore.com/football/match/{req.home.lower()}-{req.away.lower()}/{custom_id}#id:{match_id}"
        return {
            "success": True,
            "match_id": match_id,
            "home": req.home,
            "away": req.away,
            "custom_id": custom_id,
            "embed_url": embed_url,
            "nice_url": nice_url
        }
    return {"success": False, "error": "Match not found - use exact names + date"}

def find_match(home: str, away: str, date: str):
    home = home.strip().lower()
    away = away.strip().lower()
    
    try:
        events = client.get_events_by_date("football", date)
        for event in events:
            h = event.get("homeTeam", {}).get("name", "").lower()
            a = event.get("awayTeam", {}).get("name", "").lower()
            if (difflib.SequenceMatcher(None, home, h).ratio() > 0.8 and
                difflib.SequenceMatcher(None, away, a).ratio() > 0.8):
                return event["id"], event.get("customId", "")
    except:
        pass
    return None, None

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
