from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import os

app = FastAPI(title="Sofascore Momentum - Team ID Version")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team_id: int
    away_team_id: int

@app.post("/get-match")
def get_match(req: MatchRequest):
    try:
        # Get recent matches for the home team
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
    return {"status": "ok - use home_team_id and away_team_id"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
