from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import difflib
import os

app = FastAPI(title="Sofascore Momentum")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

def find_match(home: str, away: str, date: str = None):
    home = home.strip()
    away = away.strip()
    
    # 1. Date-based search (most reliable)
    if date:
        try:
            events = client.get_events_by_date("football", date)
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "")
                a_name = event.get("awayTeam", {}).get("name", "")
                if (difflib.SequenceMatcher(None, home.lower(), h_name.lower()).ratio() > 0.7 and
                    difflib.SequenceMatcher(None, away.lower(), a_name.lower()).ratio() > 0.7):
                    return event, event.get("id")
        except:
            pass
    
    # 2. Fallback name search
    try:
        search_results = client.search(home)
        team_id = None
        for r in search_results:
            entity = r.get("entity", {})
            if entity.get("type") == "team":
                team_id = entity.get("id")
                break
        if team_id:
            events = client.get_team_events(team_id, direction="last")
            for event in events:
                h_name = event.get("homeTeam", {}).get("name", "")
                a_name = event.get("awayTeam", {}).get("name", "")
                if (difflib.SequenceMatcher(None, home.lower(), h_name.lower()).ratio() > 0.7 and
                    difflib.SequenceMatcher(None, away.lower(), a_name.lower()).ratio() > 0.7):
                    return event, event.get("id")
    except:
        pass
    
    return None, None

@app.post("/get-match")
def get_match(req: MatchRequest):
    event, match_id = find_match(req.home, req.away, req.date)
    if not match_id:
        return {"success": False, "error": "Match not found - try adding date"}

    # Get customId (slug) and build nice URL
    custom_id = event.get("customId", "") if event else ""
    home_slug = event.get("homeTeam", {}).get("slug", req.home.lower()) if event else req.home.lower()
    away_slug = event.get("awayTeam", {}).get("slug", req.away.lower()) if event else req.away.lower()

    embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"
    nice_url = f"https://www.sofascore.com/{home_slug}-{away_slug}/{custom_id}#id:{match_id}"

    return {
        "success": True,
        "match_id": match_id,
        "home": req.home,
        "away": req.away,
        "embed_url": embed_url,
        "nice_url": nice_url,
        "custom_id": custom_id
    }

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
