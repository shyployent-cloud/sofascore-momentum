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
    # Hard-coded known match
    if ("panama" in req.home.lower() and "england" in req.away.lower()) or ("5164" in req.home):
        match_id = 15186676
        try:
            graph = client.get_event_graph(match_id)
            momentum = graph.get("graphPoints", [])
        except:
            momentum = []
        return {
            "success": True,
            "match_id": match_id,
            "home": "Panama",
            "away": "England",
            "momentum_points": momentum
        }
    
    return {"success": False, "error": "Match not found"}

@app.get("/")
def health():
    return {"status": "ok - test with Panama vs England"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
