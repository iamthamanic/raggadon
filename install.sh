#!/bin/bash
# 🚀 Raggadon One-Line Installer

echo "🎯 Raggadon Quick Installer"
echo "=========================="

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git ist nicht installiert!${NC}"
    exit 1
fi

# Clone Repository
echo "📦 Klone Raggadon..."
cd ~
git clone https://github.com/iamthamanic/raggadon.git raggadon_temp
cd raggadon_temp

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 ist nicht installiert!${NC}"
    exit 1
fi

# Create .env file
echo "🔧 Erstelle Konfiguration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env erstellt - Bitte API Keys eintragen!${NC}"
    echo ""
    echo "📝 Öffne .env und trage ein:"
    echo "   - OPENAI_API_KEY"
    echo "   - SUPABASE_URL" 
    echo "   - SUPABASE_API_KEY"
fi

# Install dependencies
echo "📚 Installiere Dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Install CLI
echo "🔧 Installiere CLI..."
./install_rag_cli.sh > /dev/null 2>&1

# Install service
echo "🚀 Installiere Service..."
./install_service.sh > /dev/null 2>&1

# Move to final location
echo "📁 Verschiebe nach ~/raggadon..."
cd ..
rm -rf ~/raggadon 2>/dev/null
mv raggadon_temp ~/raggadon

echo ""
echo -e "${GREEN}✅ Raggadon erfolgreich installiert!${NC}"
echo ""
echo "📝 Nächste Schritte:"
echo "1. Bearbeite ~/raggadon/.env mit deinen API Keys"
echo "2. source ~/.zshrc"
echo "3. rag status"
echo ""
echo "🎉 Fertig!"