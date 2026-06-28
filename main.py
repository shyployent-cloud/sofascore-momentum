class FixturesRequest(BaseModel):
    fixtures: list

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
