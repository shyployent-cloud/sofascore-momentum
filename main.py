from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import os

app = FastAPI(title="Sofascore Momentum")

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

@app.post("/get-match")
def get_match(req: MatchRequest):
    match_id = None
    if "panama" in req.home.lower() and "england" in req.away.lower():
        match_id = 15186676
    
    if not match_id:
        return {"success": False, "error": "Match not found - add date"}

    embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"

    return {
        "success": True,
        "match_id": match_id,
        "home": req.home,
        "away": req.away,
        "embed_url": embed_url,   # <-- This is the new line you wanted
        "embed_html": f'<iframe width="100%" height="286" src="{embed_url}" frameborder="1" scrolling="no"></iframe>'
    }

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
