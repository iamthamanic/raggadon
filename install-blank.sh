#!/bin/bash
# 🚀 Raggadon Installer (Blank - Eigene Credentials)

echo "🎯 Raggadon Installer (Eigene Credentials)"
echo "=========================================="

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

# Create .env file from example
echo "🔧 Erstelle Konfiguration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  .env erstellt - API Keys müssen eingetragen werden!${NC}"
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
echo -e "${YELLOW}📝 WICHTIG: API Keys eintragen!${NC}"
echo ""
echo "1. Öffne: ~/raggadon/.env"
echo "2. Trage ein:"
echo "   - OPENAI_API_KEY=dein-openai-key"
echo "   - SUPABASE_URL=deine-supabase-url"
echo "   - SUPABASE_API_KEY=dein-supabase-key"
echo ""
echo "3. Dann:"
echo "   source ~/.zshrc"
echo "   rag status"
echo ""
echo "🔗 OpenAI API Key: https://platform.openai.com/api-keys"
echo "🔗 Supabase: https://supabase.com/dashboard/project/_/settings/api"