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
    date: str = None  # Optional: YYYY-MM-DD

def find_match(home_team: str, away_team: str, date: str = None):
    home_input = home_team.strip()
    away_input = away_team.strip()
    home = home_input.lower()
    away = away_input.lower()
    
    print(f"DEBUG: Searching for '{home_input}' vs '{away_input}'")  # helps in logs
    
    # 1. Try date-based search first
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "")
                a_name = event.get("awayTeam", {}).get("name", "")
                h_ratio = difflib.SequenceMatcher(None, home, h_name.lower()).ratio()
                a_ratio = difflib.SequenceMatcher(None, away, a_name.lower()).ratio()
                if h_ratio > 0.7 and a_ratio > 0.7:
                    print(f"DEBUG: Found match on date: {h_name} vs {a_name}")
                    return event["id"], event
        except Exception as e:
            print("DEBUG: Date search error:", str(e))
    
    # 2. Search for home team with variations
    variations = [
        home_input,
        home_input + " national",
        home_input + " national team",
        home_input + " u23",
        home_input + " u21"
    ]
    team_id = None
    found_name = None
    for var in variations:
        try:
            search_results = client.search(var)
            for r in search_results:
                entity = r.get("entity", {})
                if entity.get("type") == "team":
                    team_id = entity.get("id")
                    found_name = entity.get("name")
                    print(f"DEBUG: Found team ID {team_id} for '{var}'")
                    break
            if team_id:
                break
        except:
            continue
    
    if not team_id:
        return None, f"Home team '{home_input}' not found after variations"
    
    # 3. Get matches for that team
    try:
        events = client.get_team_events(team_id, direction="last")
        for event in events:
            h_name = event.get("homeTeam", {}).get("name", "")
            a_name = event.get("awayTeam", {}).get("name", "")
            h_ratio = difflib.SequenceMatcher(None, home, h_name.lower()).ratio()
            a_ratio = difflib.SequenceMatcher(None, away, a_name.lower()).ratio()
            if h_ratio > 0.7 and a_ratio > 0.7:
                print(f"DEBUG: Matched {h_name} vs {a_name}")
                return event["id"], event
    except Exception as e:
        print("DEBUG: Team events error:", str(e))
    
    return None, f"No matching match found for {home_input} vs {away_input}"

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

@app.get("/")
def health():
    return {"status": "ok", "message": "Sofascore Momentum API is running"}

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
