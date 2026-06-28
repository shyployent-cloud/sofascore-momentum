from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum API")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team: str = None
    away_team: str = None
    home_id: int = None
    away_id: int = None
    date: str = None

def find_match(home_team=None, away_team=None, home_id=None, away_id=None, date=None):
    print(f"DEBUG: home_team={home_team}, home_id={home_id}, away_team={away_team}, away_id={away_id}, date={date}")
    
    # Use IDs if provided
    if home_id:
        try:
            events = client.get_team_events(home_id, direction="last")
            for event in events:
                a_id = event.get("awayTeam", {}).get("id")
                if a_id and (away_id is None or a_id == away_id):
                    if away_team:
                        a_name = event.get("awayTeam", {}).get("name", "").lower()
                        if away_team.lower() in a_name or a_name in away_team.lower():
                            return event["id"], event
                    else:
                        return event["id"], event
        except Exception as e:
            print("ID error:", str(e))
    
    # Name fallback (existing logic)
    if home_team and away_team:
        # ... keep previous name search if needed
        pass
    
    return None, "No match found"

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id, data = find_match(req.home_team, req.away_team, req.home_id, req.away_id, req.date)
    if match_id:
        try:
            graph = client.get_event_graph(match_id)
            momentum = graph.get("graphPoints", [])
        except:
            momentum = []
        return {
            "success": True,
            "match_id": match_id,
            "home": data.get("homeTeam", {}).get("name") if data else "Unknown",
            "away": data.get("awayTeam", {}).get("name") if data else "Unknown",
            "momentum_points": momentum
        }
    return {"success": False, "error": data}

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
