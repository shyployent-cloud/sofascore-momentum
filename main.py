from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import os

app = FastAPI(title="Sofascore Momentum - Match ID")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    date: str

@app.post("/get-match")
def get_match(req: MatchRequest):
    try:
        events = client.get_team_events(req.home_team_id, direction="last")
        
        for event in events:
            h_id = event.get("homeTeam", {}).get("id")
            a_id = event.get("awayTeam", {}).get("id")
            
            if h_id == req.home_team_id and a_id == req.away_team_id:
                match_id = event["id"]
                custom_id = event.get("customId", "")
                
                embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
                
                return {
                    "success": True,
                    "match_id": match_id,
                    "custom_id": custom_id,
                    "embed_url": embed_url,
                    "nice_url": f"https://www.sofascore.com/football/match/?id={match_id}"
                }
        
        return {"success": False, "error": "No match found for these team IDs on this date"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def health():
    return {"status": "ok - match id endpoint ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
