"""
Beispiel: Raggadon in Python-Projekten verwenden
"""
import requests
import json

# Raggadon Server URL
RAGGADON_URL = "http://127.0.0.1:8000"
PROJECT_NAME = "MeinProjekt"  # Ändere dies für jedes Projekt

def save_to_memory(content, role="user"):
    """Speichert wichtige Informationen im Projektgedächtnis"""
    response = requests.post(
        f"{RAGGADON_URL}/save",
        json={
            "project": PROJECT_NAME,
            "role": role,
            "content": content
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Gespeichert! Tokens: {data['tokens_used']}, Kosten: ${data['estimated_cost_usd']:.4f}")
        return data
    else:
        print(f"❌ Fehler: {response.text}")
        return None

def search_memory(query):
    """Sucht relevante Informationen im Projektgedächtnis"""
    response = requests.get(
        f"{RAGGADON_URL}/search",
        params={
            "project": PROJECT_NAME,
            "query": query
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"🔍 {len(data['results'])} Ergebnisse gefunden")
        for result in data['results']:
            print(f"\n📄 {result['role']}: {result['content'][:100]}...")
            print(f"   Ähnlichkeit: {result['similarity']:.2f}")
        return data
    else:
        print(f"❌ Fehler: {response.text}")
        return None

# Beispiel-Verwendung:
if __name__ == "__main__":
    # Wichtige Projekt-Info speichern
    save_to_memory("Die Hauptdatenbank heißt 'production_db' und läuft auf PostgreSQL 14")
    save_to_memory("Der API-Key für externe Services ist in der .env Datei unter EXTERNAL_API_KEY")
    
    # Nach Informationen suchen
    search_memory("datenbank")
    search_memory("api key")