import requests

# Token del log del frontend
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNzgxMDkwLCJpYXQiOjE3MzI3NzczNDksImp0aSI6ImZlNTYzZWJlNGE2OTQ2ZWY4ZjBhMGNjNjY1ZDMxOWJjIiwidXNlcl9pZCI6MTAwNCwicm9sIjoiQURNSU4iLCJlbWFpbCI6ImFkbWluQGNsaW5pY2FkZW1vMS5jb20iLCJub21icmVfY29tcGxldG8iOiJBZG1pbiBTaXN0ZW1hIiwidGVuYW50X2lkIjoiY2xpbmljYV9kZW1vIn0._fUJ_eIms6Qr4PsUH8lP2t6ff66A0CJ6OcXurgkrhRM"

url = "https://clinica-dental-backend.onrender.com/api/backups/history/"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Tenant-ID": "clinica_demo",
    "Content-Type": "application/json"
}

print("=== PROBANDO ENDPOINT DE BACKUPS ===")
print(f"URL: {url}")
print(f"Headers: {headers}")

response = requests.get(url, headers=headers)

print(f"\n=== RESPUESTA ===")
print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Content: {response.text[:500]}")
