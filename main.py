from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os
import requests

app = FastAPI(title="Sofascore Momentum API")

client = SofaScoreClient()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

def get_events(date: str, use_inverse: bool = False):
    suffix = "/inverse" if use_inverse else ""
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date}{suffix}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("events", [])
    except:
        pass
    return []

def find_match(home: str, away: str, date: str = None):
    home = home.strip().lower()
    away = away.strip().lower()
    
    if not date:
        return None, None
    
    # Try normal endpoint first
    events = get_events(date, use_inverse=False)
    if not events:
        events = get_events(date, use_inverse=True)  # fallback to inverse
    
    for event in events:
        h = event.get("homeTeam", {}).get("name", "").lower()
        a = event.get("awayTeam", {}).get("name", "").lower()
        if (difflib.SequenceMatcher(None, home, h).ratio() > 0.75 and
            difflib.SequenceMatcher(None, away, a).ratio() > 0.75):
            return event["id"], event.get("customId", "")
    
    return None, None

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
    return {"success": False, "error": "Match not found - try exact names + date"}

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
