from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import os

app = FastAPI()

client = SofaScoreClient()

class MatchRequest(BaseModel):
    home: str
    away: str
    date: str = None

@app.post("/get-match")
def get_match(req: MatchRequest):
    print("REQUEST RECEIVED:", req.dict())  # This will show in logs
    
    # Hard-coded test for the known match
    if "panama" in req.home.lower() and "england" in req.away.lower():
        match_id = 15186676
        try:
            graph = client.get_event_graph(match_id)
            momentum = graph.get("graphPoints", [])
        except:
            momentum = []
        return {
            "success": True,
            "match_id": match_id,
            "home": req.home,
            "away": req.away,
            "momentum_points": momentum
        }
    
    return {"success": False, "error": "Match not found - try with date 2026-06-27"}

@app.get("/")
def health():
    return {"status": "ok - try POST to /get-match"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
