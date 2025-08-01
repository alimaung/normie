import requests

url = "http://localhost:8085/pinpoint/#/main"

response = requests.get("http://localhost:8085/pinpoint/#/main")

print(f"\033[92m{response.status_code}\033[0m")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(response.text)

    
    
