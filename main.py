from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib

app = FastAPI()
client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    date: str = None  # YYYY-MM-DD, optional

def find_match(home_team: str, away_team: str, date: str = None):
    home = home_team.strip().lower()
    away = away_team.strip().lower()
    
    if date:
        events = client.get_events_by_date("football", date)
    else:
        # Search for home team
        search_results = client.search(home_team)
        team_id = None
        for r in search_results:
            if r.get("entity", {}).get("type") == "team" and home in r["entity"]["name"].lower():
                team_id = r["entity"]["id"]
                break
        if not team_id:
            return None, "Home team not found"
        events = client.get_team_events(team_id, direction="last")  # "last" or "next"
    
    for event in events:
        h_name = event.get("homeTeam", {}).get("name", "").lower()
        a_name = event.get("awayTeam", {}).get("name", "").lower()
        if (difflib.SequenceMatcher(None, home, h_name).ratio() > 0.8 and
            difflib.SequenceMatcher(None, away, a_name).ratio() > 0.8):
            return event["id"], event
    return None, "No match found"

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id, data = find_match(req.home_team, req.away_team, req.date)
    if match_id:
        graph = client.get_event_graph(match_id)
        return {
            "match_id": match_id,
            "home": data.get("homeTeam", {}).get("name"),
            "away": data.get("awayTeam", {}).get("name"),
            "momentum_points": graph.get("graphPoints", [])
        }
    return {"error": data}

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
