import requests
import base64
import yaml
import json
import os

# GitHub token (expected to be provided by GitHub Actions or environment)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Applications and environments configuration
applications = {
    "app_name1": {
        "environments": {
            "us-uat": {
                "repo": "org/app_name1-repo",
                "path": "path/to/us-uat/values.yaml"
            },
            "us-prod": {
                "repo": "org/app_name1-repo",
                "path": "path/to/us-prod/values.yaml"
            }
        }
    }
    # Add additional applications and environments as needed
}

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Headers for GitHub API authentication
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to fetch and decode content from GitHub
def fetch_values_yaml(repo, path):
    url = f"{GITHUB_API_URL}/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    content = response.json().get("content", "")
    decoded_content = base64.b64decode(content).decode("utf-8")
    return yaml.safe_load(decoded_content)

# Aggregate infrastructure details
def aggregate_infra_details(applications):
    infra_details = {}

    for app, app_data in applications.items():
        infra_details[app] = {}
        for env, env_data in app_data["environments"].items():
            repo = env_data["repo"]
            path = env_data["path"]

            try:
                values_yaml = fetch_values_yaml(repo, path)

                # Extract the relevant infrastructure details, falling back to 'default' if app-specific values are missing
                min_replicas = values_yaml.get("minreplicas", {}).get(app, values_yaml.get("minreplicas", {}).get("default", "N/A"))
                max_replicas = values_yaml.get("maxreplicas", {}).get(app, values_yaml.get("maxreplicas", {}).get("default", "N/A"))
                cpu_requests = values_yaml.get("cpu", {}).get("requests", {}).get("default", "N/A")
                cpu_limits = values_yaml.get("cpu", {}).get("limits", {}).get("default", "N/A")
                memory_requests = values_yaml.get("memory", {}).get("requests", {}).get("default", "N/A")
                memory_limits = values_yaml.get("memory", {}).get("limits", {}).get("default", "N/A")

                # Store the gathered details in the dictionary
                infra_details[app][env] = {
                    "minReplicas": min_replicas,
                    "maxReplicas": max_replicas,
                    "cpuRequests": cpu_requests,
                    "cpuLimits": cpu_limits,
                    "memoryRequests": memory_requests,
                    "memoryLimits": memory_limits
                }

            except requests.HTTPError as e:
                print(f"Failed to fetch values.yaml for {app} in {env}: {e}")
    
    return infra_details

# Save the aggregated data to a JSON file
def save_to_json(data, filename="infrastructure_details.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

# Execute the aggregation and save process
if __name__ == "__main__":
    infra_details = aggregate_infra_details(applications)
    save_to_json(infra_details)
