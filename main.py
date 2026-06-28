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
    date: str = None   # Optional but strongly recommended

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

def find_match(home: str, away: str, date: str = None):
    home = home.strip()
    away = away.strip()
    
    # Priority: Date-based search
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h = event.get("homeTeam", {}).get("name", "").lower()
                a = event.get("awayTeam", {}).get("name", "").lower()
                if (difflib.SequenceMatcher(None, home.lower(), h).ratio() > 0.75 and
                    difflib.SequenceMatcher(None, away.lower(), a).ratio() > 0.75):
                    return event["id"], event.get("customId", "")
        except:
            pass
    
    # Fallback: Team search (recent matches)
    try:
        search = client.search(home)
        team_id = None
        for r in search:
            entity = r.get("entity", {})
            if entity.get("type") == "team":
                team_id = entity.get("id")
                break
        if team_id:
            events = client.get_team_events(team_id, direction="last")
            for event in events:
                h = event.get("homeTeam", {}).get("name", "").lower()
                a = event.get("awayTeam", {}).get("name", "").lower()
                if (difflib.SequenceMatcher(None, home.lower(), h).ratio() > 0.7 and
                    difflib.SequenceMatcher(None, away.lower(), a).ratio() > 0.7):
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
