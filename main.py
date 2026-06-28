from fastapi import FastAPI
from pydantic import BaseModel
from sofascore_api import SofaScoreClient
import os

app = FastAPI(title="Sofascore Momentum")

client = SofaScoreClient()

class MatchRequest(BaseModel):
 match_id: int

@app.post("/get-match")
def get_match(req: MatchRequest):
 match_id = req.match_id

 try:
 graph = client.get_event_graph(match_id)
 momentum = graph.get("graphPoints", [])
 except:
 momentum = []

 embed_url = f"https://widgets.sofascore.com/embed/attackMomentum?id={match_id}&widgetTheme=dark"

 return {
 "success": True,
 "match_id": match_id,
 "embed_url": embed_url,
 "momentum_points": momentum
 }

@app.get("/")
def health():
 return {"status": "ok - use match_id"}

if __name__ == "__main__":
 import uvicorn
 uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
