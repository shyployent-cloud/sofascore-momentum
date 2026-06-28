def find_match(home_team: str, away_team: str, date: str = None):
    home = home_team.strip().lower()
    away = away_team.strip().lower()
    
    # Try direct date search first (best)
    if date:
        events = client.get_events_by_date("football", date)
        for event in events:
            h_name = event.get("homeTeam", {}).get("name", "").lower()
            a_name = event.get("awayTeam", {}).get("name", "").lower()
            if (difflib.SequenceMatcher(None, home, h_name).ratio() > 0.75 and
                difflib.SequenceMatcher(None, away, a_name).ratio() > 0.75):
                return event["id"], event
    
    # Fallback: Search for home team
    search_results = client.search(home_team)
    team_id = None
    for r in search_results:
        entity = r.get("entity", {})
        if entity.get("type") == "team" and home in entity.get("name", "").lower():
            team_id = entity.get("id")
            break
    
    if not team_id:
        # Try partial search or common variations
        search_results = client.search(home_team + " national")
        for r in search_results:
            entity = r.get("entity", {})
            if entity.get("type") == "team":
                team_id = entity.get("id")
                break
    
    if not team_id:
        return None, f"Home team '{home_team}' not found"
    
    events = client.get_team_events(team_id, direction="last")
    
    for event in events:
        h_name = event.get("homeTeam", {}).get("name", "").lower()
        a_name = event.get("awayTeam", {}).get("name", "").lower()
        if (difflib.SequenceMatcher(None, home, h_name).ratio() > 0.75 and
            difflib.SequenceMatcher(None, away, a_name).ratio() > 0.75):
            return event["id"], event
    
    return None, "No matching match found for teams"
