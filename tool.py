from datetime import datetime
import mathematics

def extract_top_technologies(technologies: dict, limit: int = 5) -> list:
    """Extracts the most frequently used technologies from the frequency map."""
    return list(technologies.keys())[:limit]

def extract_recent_repository_context(repositories: list, limit: int = 10) -> list:
    """Extracts the metadata of the most recently updated repositories for the LLM context."""
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

def compile_payload_from_memory(data: dict, engine_config: dict = None) -> dict:
    """
    Ingests raw dictionary data to calculate scores and build context.
    Acts as the bridge between the UI constants and the Math engine.
    """
    profile = data.get('profile', {})
    repositories = data.get('repositories', [])
    username = profile.get('username', 'Unknown')

    # Establish Failsafe Defaults (In case engine_config fails to pass)
    if not engine_config:
        engine_config = {
            "persona": "Default (Balanced Assessor)",
            "weights": {"consistency": 0.20, "community": 0.30, "technology": 0.25, "management": 0.15, "advanced": 0.10},
            "constants": {
                "epsilon": 1.0, "alpha": 5.0, "beta": 3.0, "breadth_ceiling": 8.0,
                "gamma": 10.0, "adv_target": 3,
                "sweet_spot_low": 0.15, "sweet_spot_high": 0.85, "points_per_collab": 20.0,
                "partial_credit": 0.2, "star_bonus": 2.0, "fork_bonus": 5.0,
                "target_ratio": 0.75, "bio_bonus": 10.0, "name_bonus": 5.0
            }
        }

    weights = engine_config.get("weights", {})
    c = engine_config.get("constants", {})

    # Execute Mathematics with Dynamic Constants explicitly mapped
    con_data = mathematics.calculate_consistency_score(
        profile.get('monthly_contributions', {}), 
        epsilon=c.get("epsilon", 1.0)
    )
    
    com_data = mathematics.calculate_community_score(
        repositories, 
        sweet_spot_low=c.get("sweet_spot_low", 0.15), 
        sweet_spot_high=c.get("sweet_spot_high", 0.85), 
        points_per_collab=c.get("points_per_collab", 20.0),
        partial_credit=c.get("partial_credit", 0.2),
        star_bonus=c.get("star_bonus", 2.0),
        fork_bonus=c.get("fork_bonus", 5.0)
    )
    
    tech_data = mathematics.calculate_technology_score(
        profile.get('technologies', {}), 
        alpha=c.get("alpha", 5.0), 
        beta=c.get("beta", 3.0),
        breadth_ceiling=c.get("breadth_ceiling", 8.0)
    )
    
    adv_data = mathematics.calculate_advanced_score(
        profile.get('forked_repositories', []), 
        gamma=c.get("gamma", 10.0),
        adv_target=c.get("adv_target", 3)
    )
    
    man_data = mathematics.calculate_management_score(
        profile, 
        target_ratio=c.get("target_ratio", 0.75), 
        bio_bonus=c.get("bio_bonus", 10.0), 
        name_bonus=c.get("name_bonus", 5.0)
    )

    # Bundle calculated components and execute Final Score logic
    scores_payload = {
        "consistency": con_data,
        "community": com_data,
        "technology": tech_data,
        "advanced": adv_data,
        "management": man_data
    }

    final_score_data = mathematics.calculate_final_score(scores_payload, weights)

    # Extract Narrative Context
    top_tech = extract_top_technologies(profile.get('technologies', {}))
    recent_repos = extract_recent_repository_context(repositories)

    # Build the structured Context Payload returned to the main UI
    return {
        "user_target": username,
        "bio": profile.get("bio", ""),
        "evaluation_persona": engine_config.get("persona", "Default"),
        "hard_metrics": {
            "final_score": final_score_data["score"],
            "category_scores": {
                "consistency": con_data["score"],
                "community": com_data["score"],
                "technology": tech_data["score"],
                "advanced": adv_data["score"],
                "management": man_data["score"]
            },
            "breakdowns": {
                "final": final_score_data["details"],
                "consistency": con_data["details"],
                "community": com_data["details"],
                "technology": tech_data["details"],
                "advanced": adv_data["details"],
                "management": man_data["details"]
            }
        },
        "narrative_context": {
            "top_technologies": top_tech,
            "recent_focus_areas": recent_repos
        }
    }