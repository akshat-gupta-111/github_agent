import math

def calculate_consistency_score(monthly_contributions: dict, target_commits: int = 15, cap: int = 30) -> float:
    """
    Calculates the consistency score using a capped intensity and active floor model.
    """
    if not monthly_contributions:
        return 0.0

    total_months = len(monthly_contributions)
    active_months = 0
    capped_commits_sum = 0

    for commits in monthly_contributions.values():
        if commits > 0:
            active_months += 1
        capped_commits_sum += min(commits, cap)

    # Calculate the two halves of the score
    floor_score = 0.5 * (active_months / total_months)
    intensity_ratio = capped_commits_sum / (total_months * target_commits)
    intensity_score = 0.5 * min(1.0, intensity_ratio)

    return round((floor_score + intensity_score) * 100, 2)

def calculate_community_score(repositories: list) -> float:
    """
    Calculates the community score based on collaborative repositories,
    rewarding users who hit the 'Collaboration Sweet Spot' (15% - 85% of commits).
    """
    if not repositories:
        return 0.0

    engagement_sum = 0
    total_stars = 0
    total_forks = 0

    for repo in repositories:
        total_stars += repo.get("stars", 0)
        total_forks += repo.get("forks", 0)
        
        deep_metrics = repo.get("deep_metrics", {})
        commits_data = deep_metrics.get("commits", {})
        
        user_ratio = commits_data.get("user_commit_ratio", 0.0)
        total_commits = commits_data.get("total_repo_commits", 0)
        user_commits = commits_data.get("user_commits_count", 0)

        # Identify shared repositories (where the user isn't the sole contributor)
        if total_commits > user_commits:
            # Collaboration Sweet Spot Check
            if 0.15 <= user_ratio <= 0.85:
                engagement_sum += 1.0
            elif user_ratio > 0.0:
                # Partial credit if they contributed, but fell outside the ideal band
                engagement_sum += 0.2 

    # Base points from engagement (20 points per healthy collab), plus small bonuses for stars/forks
    score = (engagement_sum * 20) + (total_stars * 2) + (total_forks * 5)
    
    return round(min(100.0, score), 2)

def calculate_technology_score(technologies: dict) -> float:
    """
    Calculates the technology score balancing breadth (total languages) 
    and depth (logarithmic scaling of usage frequency).
    """
    if not technologies:
        return 0.0

    total_languages = len(technologies)
    
    # Breadth: Maxes out at 8 distinct technologies (40% of the tech score)
    breadth_score = (min(total_languages, 8) / 8.0) * 40

    # Depth: Logarithmic sum of frequencies (60% of the tech score)
    depth_sum = sum(math.log2(count + 1) for count in technologies.values())
    depth_score = min(1.0, depth_sum / 20.0) * 60

    return round(min(100.0, breadth_score + depth_score), 2)

def calculate_advanced_score(forked_repositories: list) -> float:
    """
    Calculates the advanced score, rewarding users who push code to 
    highly starred/forked upstream repositories.
    """
    if not forked_repositories:
        return 0.0

    score = 0.0
    for fork in forked_repositories:
        stars = fork.get("stars_count", 0)
        forks = fork.get("forks_count", 0)
        user_commits = fork.get("user_commits_count", 0)

        if user_commits > 0:
            # The impact of the repo is logarithmic, multiplied by the user's active commits
            repo_impact = 10 * math.log10(stars + forks + 1)
            score += repo_impact * user_commits

    return round(min(100.0, score), 2)

def calculate_management_score(profile: dict) -> float:
    """
    Calculates the management score based on profile completeness and README ratios.
    """
    readme_ratio = profile.get("readme_ratio", 0.0)
    has_bio = bool(profile.get("bio"))
    has_name = bool(profile.get("name"))

    # 85 points available for hitting the target readme ratio (75%)
    readme_score = min(1.0, readme_ratio / 0.75) * 85
    
    # Flat bonuses for filling out the profile
    bio_score = 10 if has_bio else 0
    name_score = 5 if has_name else 0

    return round(min(100.0, readme_score + bio_score + name_score), 2)

def calculate_final_score(scores: dict, weights: dict) -> float:
    """
    Generates the final weighted score based on the individual module scores 
    and the weights loaded from the CSV.
    """
    final_score = 0.0
    for category, score in scores.items():
        weight = float(weights.get(category, 0.0))
        final_score += score * weight
        
    return round(final_score, 2)