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

def find_match(home: str, away: str, date: str = None):
    home = home.strip()
    away = away.strip()
    
    # Date-based search (recommended)
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "")
                a_name = event.get("awayTeam", {}).get("name", "")
                if (difflib.SequenceMatcher(None, home.lower(), h_name.lower()).ratio() > 0.7 and
                    difflib.SequenceMatcher(None, away.lower(), a_name.lower()).ratio() > 0.7):
                    return event["id"], event
        except:
            pass
    
    # Fallback team ID/name search
    try:
        search = client.search(home)
        team_id = None
        for r in search:
            if r.get("entity", {}).get("type") == "team":
                team_id = r["entity"]["id"]
                break
        if team_id:
            events = client.get_team_events(team_id, direction="last")
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "")
                a_name = event.get("awayTeam", {}).get("name", "")
                if (difflib.SequenceMatcher(None, home.lower(), h_name.lower()).ratio() > 0.7 and
                    difflib.SequenceMatcher(None, away.lower(), a_name.lower()).ratio() > 0.7):
                    return event["id"], event
    except:
        pass
    
    return None, None

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
            "home": data.get("homeTeam", {}).get("name") if data else req.home,
            "away": data.get("awayTeam", {}).get("name") if data else req.away,
            "momentum_points": momentum
        }
    return {"success": False, "error": "Match not found"}

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
