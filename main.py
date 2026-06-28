from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum API")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    date: str = None

def find_match(home_team: str, away_team: str, date: str = None):
    home = home_team.strip().lower()
    away = away_team.strip().lower()
    
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h = event.get("homeTeam", {}).get("name", "").lower()
                a = event.get("awayTeam", {}).get("name", "").lower()
                if (difflib.SequenceMatcher(None, home, h).ratio() > 0.75 and
                    difflib.SequenceMatcher(None, away, a).ratio() > 0.75):
                    return event["id"], event
        except:
            pass
    
    # Team search fallback
    search_results = client.search(home_team)
    team_id = None
    for r in search_results:
        e = r.get("entity", {})
        if e.get("type") == "team" and home in e.get("name", "").lower():
            team_id = e.get("id")
            break
    
    if not team_id:
        search_results = client.search(home_team + " national")
        for r in search_results:
            e = r.get("entity", {})
            if e.get("type") == "team":
                team_id = e.get("id")
                break
    
    if not team_id:
        return None, f"Home team '{home_team}' not found"
    
    events = client.get_team_events(team_id, direction="last")
    for event in events:
        h = event.get("homeTeam", {}).get("name", "").lower()
        a = event.get("awayTeam", {}).get("name", "").lower()
        if (difflib.SequenceMatcher(None, home, h).ratio() > 0.75 and
            difflib.SequenceMatcher(None, away, a).ratio() > 0.75):
            return event["id"], event
    return None, "No matching match found"

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id, data = find_match(req.home_team, req.away_team, req.date)
    if match_id:
        try:
            graph = client.get_event_graph(match_id)
            momentum = graph.get("graphPoints", [])
        except:
            momentum = []
        return {
            "success": True,
            "match_id": match_id,
            "home": data.get("homeTeam", {}).get("name") if isinstance(data, dict) else req.home_team,
            "away": data.get("awayTeam", {}).get("name") if isinstance(data, dict) else req.away_team,
            "momentum_points": momentum
        }
    return {"success": False, "error": data}

# Health check
@app.get("/")
def health():
    return {"status": "ok"}

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
