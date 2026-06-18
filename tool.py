import os
from datetime import datetime
import mathematics

def extract_top_technologies(technologies: dict, limit: int = 5) -> list:
    return list(technologies.keys())[:limit]

def extract_recent_repository_context(repositories: list, limit: int = 10) -> list:
    sorted_repos = sorted(
        repositories, 
        key=lambda x: datetime.strptime(x.get('updated_at', '1970-01-01T00:00:00Z'), "%Y-%m-%dT%H:%M:%SZ"), 
        reverse=True
    )
    recent_context = []
    for repo in sorted_repos[:limit]:
        recent_context.append({
            "name": repo.get("name"),
            "description": repo.get("description") or "No description provided.",
            "primary_language": repo.get("primary_language") or "Unknown"
        })
    return recent_context

def compile_payload_from_memory(data: dict, weights_filepath: str = "weights.csv") -> dict:
    """Ingests raw dictionary data to calculate scores and build context."""
    profile = data.get('profile', {})
    repositories = data.get('repositories', [])
    username = profile.get('username', 'Unknown')

    # Load Weights
    weights = {}
    if os.path.exists(weights_filepath):
        import csv
        with open(weights_filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                weights[row['weight_type']] = float(row['weight_value'])
    else:
        weights = {"community": 0.30, "technology": 0.25, "consistency": 0.20, "management": 0.15, "advanced": 0.10}

    # Calculate Scores
    scores = {
        "consistency": mathematics.calculate_consistency_score(profile.get('monthly_contributions', {})),
        "community": mathematics.calculate_community_score(repositories),
        "technology": mathematics.calculate_technology_score(profile.get('technologies', {})),
        "advanced": mathematics.calculate_advanced_score(profile.get('forked_repositories', [])),
        "management": mathematics.calculate_management_score(profile)
    }
    final_score = mathematics.calculate_final_score(scores, weights)

    # Extract Narrative
    top_tech = extract_top_technologies(profile.get('technologies', {}))
    recent_repos = extract_recent_repository_context(repositories)

    return {
        "user_target": username,
        "bio": profile.get("bio", ""),
        "hard_metrics": {
            "final_score": final_score,
            "breakdown": scores
        },
        "narrative_context": {
            "top_technologies": top_tech,
            "recent_focus_areas": recent_repos
        }
    }