from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum API")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str

def find_match_by_name(home: str, away: str):
    home = home.strip()
    away = away.strip()
    
    # Step 1: Search for home team and get its ID
    try:
        search_results = client.search(home)
        home_team_id = None
        for r in search_results:
            entity = r.get("entity", {})
            if entity.get("type") == "team":
                home_team_id = entity.get("id")
                break
        
        if home_team_id:
            # Step 2: Get recent matches for this team
            events = client.get_team_events(home_team_id, direction="last")
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "").lower()
                a_name = event.get("awayTeam", {}).get("name", "").lower()
                
                # Fuzzy match on both teams
                home_match = difflib.SequenceMatcher(None, home.lower(), h_name).ratio() > 0.75
                away_match = difflib.SequenceMatcher(None, away.lower(), a_name).ratio() > 0.75
                
                if home_match and away_match:
                    return event["id"], event.get("customId", "")
    except Exception as e:
        print("Error in search:", str(e))
    
    return None, None

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id, custom_id = find_match_by_name(req.home, req.away)
    if match_id:
        embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
        nice_url = f"https://www.sofascore.com/football/match/{req.home.lower()}-{req.away.lower()}/{custom_id}#id:{match_id}"
        return {
            "success": True,
            "match_id": match_id,
            "home": req.home,
            "away": req.away,
            "custom_id": custom_id,
            "embed_url": embed_url,
            "nice_url": nice_url
        }
    return {"success": False, "error": "Match not found - try exact team names"}

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
