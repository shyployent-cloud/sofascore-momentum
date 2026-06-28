from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id, data = find_match(req.home, req.away, req.date)
    if match_id:
        try:
            graph = client.get_event_graph(match_id)
            momentum = graph.get("graphPoints", [])
        except:
            momentum = []
        return {
            "success": True,
            "match_id": match_id,
            "home": req.home,
            "away": req.away,
            "momentum_points": momentum
        }
    return {"success": False, "error": "Match not found - try exact names + date"}

def find_match(home: str, away: str, date: str = None):
    home = home.strip()
    away = away.strip()
    
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h = event.get("homeTeam", {}).get("name", "")
                a = event.get("awayTeam", {}).get("name", "")
                if (difflib.SequenceMatcher(None, home.lower(), h.lower()).ratio() > 0.75 and
                    difflib.SequenceMatcher(None, away.lower(), a.lower()).ratio() > 0.75):
                    return event["id"], event
        except:
            pass
    
    return None, None

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
