import json
import csv
import sys
import os
import mathematics  # Importing your modular formulas

def load_weights(filepath: str) -> dict:
    """Reads the weights from the CSV file."""
    weights = {}
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                weights[row['weight_type']] = float(row['weight_value'])
        return weights
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Ensure weights.csv exists.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python calculation.py <git_data_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    weights_file = 'weights.csv'
    output_file = 'scores.csv'

    # 1. Load the weights
    weights = load_weights(weights_file)

    # 2. Load the parsed JSON data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {json_file}")
        sys.exit(1)

    profile = data.get('profile', {})
    repositories = data.get('repositories', [])

    username = profile.get('username', 'Unknown')
    monthly_contributions = profile.get('monthly_contributions', {})
    technologies = profile.get('technologies', {})
    forked_repositories = profile.get('forked_repositories', [])

    # 3. Calculate individual module scores
    scores = {
        "consistency": mathematics.calculate_consistency_score(monthly_contributions),
        "community": mathematics.calculate_community_score(repositories),
        "technology": mathematics.calculate_technology_score(technologies),
        "advanced": mathematics.calculate_advanced_score(forked_repositories),
        "management": mathematics.calculate_management_score(profile)
    }

    # 4. Calculate the weighted final score
    final_score = mathematics.calculate_final_score(scores, weights)

    # 5. Format the output payload
    row_data = {
        "user_name": username,
        "consistency_score": scores["consistency"],
        "community_score": scores["community"],
        "technology_score": scores["technology"],
        "management_score": scores["management"],
        "advanced_score": scores["advanced"],
        "final_score": final_score
    }

    # 6. Append to CSV
    file_exists = os.path.isfile(output_file)
    headers = list(row_data.keys())

    with open(output_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # Write headers only if the file is being created for the first time
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(row_data)

    print(f"[+] Successfully calculated scores for {username}")
    print(f"[+] Data appended to {output_file}")
    print(json.dumps(row_data, indent=4))

if __name__ == "__main__":
    main()