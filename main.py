from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import requests
import os

app = FastAPI(title="Sofascore Momentum")
client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team_id: int
    away_team_id: int

class MatchByNameRequest(BaseModel):
    home_team_name: str
    away_team_name: str

def search_team_id(team_name: str) -> int:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    url = f"https://api.sofascore.com/api/v1/search/teams?q={team_name}"
    response = requests.get(url, headers=headers)
    data = response.json()
    teams = data.get("teams", [])
    
    if not teams:
        raise ValueError(f"No team found for: {team_name}")
    
    # Try exact match first
    for team in teams:
        name = team.get("name", "").lower()
        short = team.get("shortName", "").lower()
        if name == team_name.lower() or short == team_name.lower():
            return team["id"]
    
    # Fallback to first result
    return teams[0]["id"]

@app.post("/get-match-by-name")
def get_match_by_name(req: MatchByNameRequest):
    try:
        home_id = search_team_id(req.home_team_name)
        away_id = search_team_id(req.away_team_name)
        
        events = client.get_team_events(home_id, direction="last")
        
        for event in events:
            h_id = event.get("homeTeam", {}).get("id")
            a_id = event.get("awayTeam", {}).get("id")
            
            if h_id == home_id and a_id == away_id:
                match_id = event["id"]
                custom_id = event.get("customId", "")
                embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
                nice_url = f"https://www.sofascore.com/football/match/?id={match_id}"
                
                return {
                    "success": True,
                    "match_id": match_id,
                    "home_team_name": req.home_team_name,
                    "away_team_name": req.away_team_name,
                    "home_team_id": home_id,
                    "away_team_id": away_id,
                    "custom_id": custom_id,
                    "embed_url": embed_url,
                    "nice_url": nice_url
                }
        
        return {"success": False, "error": "No recent match found between these teams"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/get-match")
def get_match(req: MatchRequest):
    try:
        events = client.get_team_events(req.home_team_id, direction="last")
        
        for event in events:
            home_id = event.get("homeTeam", {}).get("id")
            away_id = event.get("awayTeam", {}).get("id")
            
            if home_id == req.home_team_id and away_id == req.away_team_id:
                match_id = event["id"]
                custom_id = event.get("customId", "")
                embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
                nice_url = f"https://www.sofascore.com/football/match/?id={match_id}"
                
                return {
                    "success": True,
                    "match_id": match_id,
                    "home_team_id": req.home_team_id,
                    "away_team_id": req.away_team_id,
                    "custom_id": custom_id,
                    "embed_url": embed_url,
                    "nice_url": nice_url
                }
        
        return {"success": False, "error": "No recent match found between these two teams"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
