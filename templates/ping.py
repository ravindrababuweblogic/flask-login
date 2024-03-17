import json
import os
import requests

def ping(url):
    # Making a get request 
    try:
        # url = f"http://{host}:{port}"
        response = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
        # If there's an exception, return a JSON object indicating that the host is not reachable
        return json.dumps({"reachable": False, "error": str(e)})

    if response.status_code == 200:
        # If the ping was successful, return a JSON object indicating that the host is reachable
        return json.dumps({"reachable": True})
    else:
        # If the ping failed, return a JSON object indicating that the host is not reachable
        return json.dumps({"reachable": False, "status_code": response.status_code})
