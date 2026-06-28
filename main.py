from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import os

app = FastAPI(title="Sofascore Momentum")
client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team_id: int
    away_team_id: int

class MatchByNameRequest(BaseModel):
    home_team_name: str
    away_team_name: str

class FixturesRequest(BaseModel):
    fixtures: list

def search_team_id(team_name: str) -> int:
    results = client.search(team_name)
    
    if not isinstance(results, list):
        raise ValueError(f"Unexpected search result format for: {team_name}")
    
    football_teams = [
        r for r in results
        if r.get("type") == "team"
        and r.get("entity", {}).get("sport", {}).get("slug") == "football"
        and r.get("entity", {}).get("gender") == "M"
    ]
    
    if not football_teams:
        raise ValueError(f"No football team found for: {team_name}")
    
    for item in football_teams:
        name = item["entity"].get("name", "").lower()
        if name == team_name.lower():
            return item["entity"]["id"]
    
    return football_teams[0]["entity"]["id"]

@app.post("/get-team-ids-from-fixtures")
def get_team_ids_from_fixtures(req: FixturesRequest):
    results = []
    for fixture in req.fixtures:
        home_name = fixture.get("home_team_name", "")
        away_name = fixture.get("away_team_name", "")
        fixture_id = fixture.get("fixture_id", "")
        
        try:
            home_id = search_team_id(home_name)
        except:
            home_id = None
            
        try:
            away_id = search_team_id(away_name)
        except:
            away_id = None
        
        results.append({
            "fixture_id": fixture_id,
            "home_team_name": home_name,
            "home_sofascore_id": home_id,
            "away_team_name": away_name,
            "away_sofascore_id": away_id
        })
    
    return {"success": True, "results": results}

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
                
                return {
                    "success": True,
                    "match_id": match_id,
                    "home_team_id": home_id,
                    "away_team_id": away_id,
                    "custom_id": custom_id,
                    "embed_url": embed_url
                }
        
        return {"success": False, "error": "No recent match found"}
    
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
                embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
                
                return {
                    "success": True,
                    "match_id": match_id,
                    "embed_url": embed_url
                }
        
        return {"success": False, "error": "No match found"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/get-team-id")
def get_team_id(name: str):
    try:
        results = client.search(name)
        
        if not isinstance(results, list):
            return {"success": False, "error": "Unexpected format"}
        
        football_teams = [
            r for r in results
            if r.get("type") == "team"
            and r.get("entity", {}).get("sport", {}).get("slug") == "football"
            and r.get("entity", {}).get("gender") == "M"
        ]
        
        if not football_teams:
            return {"success": False, "error": f"No football team found for: {name}"}
        
        for item in football_teams:
            if item["entity"].get("name", "").lower() == name.lower():
                return {
                    "success": True,
                    "team_name": name,
                    "team_id": item["entity"]["id"]
                }
        
        return {
            "success": True,
            "team_name": name,
            "team_id": football_teams[0]["entity"]["id"]
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/search-team")
def search_team(name: str):
    try:
        results = client.search(name)
        return results
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
