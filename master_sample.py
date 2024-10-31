import requests
import base64
import yaml
import json

# GitHub personal access token
GITHUB_TOKEN = 'your_github_token'

# List of applications with their repository and path to the values.yaml file for each environment
applications = {
    "app1": {
        "environments": {
            "us-uat": {
                "repo": "org/app1-repo",
                "path": "path/to/us-uat/values.yaml"
            },
            "us-prod": {
                "repo": "org/app1-repo",
                "path": "path/to/us-prod/values.yaml"
            }
        }
    },
    "app2": {
        "environments": {
            "eu-uat": {
                "repo": "org/app2-repo",
                "path": "path/to/eu-uat/values.yaml"
            },
            "eu-prod": {
                "repo": "org/app2-repo",
                "path": "path/to/eu-prod/values.yaml"
            }
        }
    }
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

# Main function to aggregate infrastructure details
def aggregate_infra_details(applications):
    infra_details = {}

    for app, app_data in applications.items():
        infra_details[app] = {}
        for env, env_data in app_data["environments"].items():
            repo = env_data["repo"]
            path = env_data["path"]

            try:
                values_yaml = fetch_values_yaml(repo, path)
                
                # Extract relevant infrastructure details
                infra_details[app][env] = {
                    "minPods": values_yaml.get("hpa", {}).get("minPods", "N/A"),
                    "maxPods": values_yaml.get("hpa", {}).get("maxPods", "N/A"),
                    "cpuRequests": values_yaml.get("resources", {}).get("requests", {}).get("cpu", "N/A"),
                    "cpuLimits": values_yaml.get("resources", {}).get("limits", {}).get("cpu", "N/A"),
                    "memoryRequests": values_yaml.get("resources", {}).get("requests", {}).get("memory", "N/A"),
                    "memoryLimits": values_yaml.get("resources", {}).get("limits", {}).get("memory", "N/A")
                }
                
            except requests.HTTPError as e:
                print(f"Failed to fetch values.yaml for {app} in {env}: {e}")
    
    return infra_details

# Generate the JSON file
def save_to_json(data, filename="infrastructure_details.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

# Run the aggregation and save to JSON
if __name__ == "__main__":
    infra_details = aggregate_infra_details(applications)
    save_to_json(infra_details)
