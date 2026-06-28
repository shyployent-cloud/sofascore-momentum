from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum API")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str = None          # Can be name or ID (as string)
    away: str = None
    date: str = None

def find_match(home=None, away=None, date=None):
    print(f"DEBUG: home='{home}', away='{away}', date={date}")
    
    home_str = str(home).strip() if home else ""
    away_str = str(away).strip() if away else ""
    
    # Try ID first if numeric
    if home_str.isdigit():
        try:
            home_id = int(home_str)
            events = client.get_team_events(home_id, direction="last")
            for event in events:
                a_name = event.get("awayTeam", {}).get("name", "").lower()
                if away_str.lower() in a_name or a_name in away_str.lower():
                    return event["id"], event
        except:
            pass
    
    # Name-based search
    if home_str and away_str:
        if date:
            try:
                events = client.get_events_by_date("football", date)
                for event in events:
                    h_name = event.get("homeTeam", {}).get("name", "").lower()
                    a_name = event.get("awayTeam", {}).get("name", "").lower()
                    if (difflib.SequenceMatcher(None, home_str.lower(), h_name).ratio() > 0.7 and
                        difflib.SequenceMatcher(None, away_str.lower(), a_name).ratio() > 0.7):
                        return event["id"], event
            except:
                pass
        
        # Team search fallback
        search_results = client.search(home_str)
        team_id = None
        for r in search_results:
            entity = r.get("entity", {})
            if entity.get("type") == "team":
                team_id = entity.get("id")
                break
        if team_id:
            events = client.get_team_events(team_id, direction="last")
            for event in events:
                h_name
