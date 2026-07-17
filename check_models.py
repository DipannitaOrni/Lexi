import httpx

API_KEY = "AQ.Ab8RN6KMOjjgydDW3t8ZX3skCOzqL2sbDEJlGO2xbwfiwzaeeQ"
MODEL = "gemma-4-26b-a4b-it"

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

payload = {
    "contents": [{"role": "user", "parts": [{"text": "Say hello"}]}]
}

resp = httpx.post(url, json=payload)
print("Status:", resp.status_code)
print(resp.text)