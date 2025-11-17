# examples/requests_example.py
import requests

def get_github_user(username: str) -> dict:
    response = requests.get(f"https://api.github.com/users/{username}")
    return response.json()
