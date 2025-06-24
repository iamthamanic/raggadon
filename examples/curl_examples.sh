#!/bin/bash

# Beispiele für die Verwendung von Raggadon mit curl
# Diese Befehle kannst du direkt im Terminal ausführen

PROJECT="MeinProjekt"
RAGGADON_URL="http://127.0.0.1:8000"

echo "🚀 Raggadon API Beispiele"
echo "========================"

echo -e "\n1. Projekt-Info speichern:"
echo "curl -X POST \"$RAGGADON_URL/save\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"project\": \"$PROJECT\", \"role\": \"user\", \"content\": \"Wichtige Info über das Projekt\"}'"

echo -e "\n2. Nach Informationen suchen:"
echo "curl \"$RAGGADON_URL/search?project=$PROJECT&query=wichtige\""

echo -e "\n3. Health Check:"
echo "curl \"$RAGGADON_URL/health\""

echo -e "\n========================"
echo "Führe diese Beispiele aus:"

# Beispiel 1: Speichern
echo -e "\n📝 Speichere Projekt-Info..."
curl -X POST "$RAGGADON_URL/save" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "'"$PROJECT"'",
    "role": "system",
    "content": "Dieses Projekt verwendet TypeScript 5.0 und React 18"
  }'

echo -e "\n\n🔍 Suche nach TypeScript..."
curl "$RAGGADON_URL/search?project=$PROJECT&query=typescript"

echo -e "\n\n✅ Health Check..."
curl "$RAGGADON_URL/health"