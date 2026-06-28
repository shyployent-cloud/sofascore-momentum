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

@app.post("/get
