def search_team_id(team_name: str) -> int:
    results = client.search(team_name)
    
    if not isinstance(results, list):
        raise ValueError(f"Unexpected search result format for: {team_name}")
    
    # Filter to football teams only (male)
    football_teams = [
        r for r in results
        if r.get("type") == "team"
        and r.get("entity", {}).get("sport", {}).get("slug") == "football"
        and r.get("entity", {}).get("gender") == "M"
    ]
    
    if not football_teams:
        raise ValueError(f"No football team found for: {team_name}")
    
    # Try exact name match first
    for item in football_teams:
        name = item["entity"].get("name", "").lower()
        if name == team_name.lower():
            return item["entity"]["id"]
    
    # Fallback to highest scoring result
    return football_teams[0]["entity"]["id"]
