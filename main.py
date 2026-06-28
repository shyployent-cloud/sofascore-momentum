from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI()

# Railway port handling
PORT = int(os.getenv("PORT", 8000))
client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    date: str = None  # Optional: YYYY-MM-DD

def find_match(home_team: str, away_team: str, date: str = None):
    home = home_team.strip().lower()
    away = away_team.strip().lower()
    
    # 1. Try by date first (most accurate)
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "").lower()
                a_name = event.get("awayTeam", {}).get("name", "").lower()
                if (difflib.SequenceMatcher(None, home, h_name).ratio() > 0.75 and
                    difflib.SequenceMatcher(None, away, a_name).ratio() > 0.75):
                    return event["id"], event
        except:
            pass  # fallback if date search fails
    
    # 2. Search for home team
    search_results = client.search(home_team)
    team_id = None
    for r in search_results:
        entity = r.get("entity", {})
        if entity.get("type") == "team" and home in entity.get("name", "").lower():
            team_id = entity.get("id")
            break
    
    # Try national team variation if not found
    if not team_id:
        search_results = client.search(home_team + " national")
        for r in search_results:
            entity = r.get("entity", {})
            if entity.get("type") == "team":
                team_id = entity.get("id")
                break
    
    if not team_id:
        return None, f"Home team '{home_team}' not found"
    
    # Get recent matches for the team
    events = client.get_team_events(team_id, direction="last")  # change to "next" for upcoming
    
    for event in events:
        h_name = event.get("homeTeam
