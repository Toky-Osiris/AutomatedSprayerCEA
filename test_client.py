import requests
import json

# Local Azure Function URL (change this if deployed)
url = "http://localhost:7071/api/analyze_crop"

# Prepare the payload
payload = {
    "container": "imagedata",               
    "image_blob": "stress_6_2024-09-20.png",      
    "send_signal": True              
}

headers = {
    "Content-Type": "application/json"
}

print("Sending request to Azure Function...")
response = requests.post(url, headers=headers, json=payload)

print("\n Status Code:", response.status_code)

try:
    print(" Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Could not parse JSON:", e)
    print(response.text)
