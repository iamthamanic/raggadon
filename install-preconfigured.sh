#!/bin/bash
# 🚀 Raggadon Installer (Mit vorkonfigurierten Credentials)

echo "🎯 Raggadon Quick Installer (Vorkonfiguriert)"
echo "============================================="

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

# Create .env file with preconfigured credentials
echo "🔧 Erstelle Konfiguration mit API Keys..."
cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=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

# Supabase Configuration  
SUPABASE_URL=https://vfrdoxhdphxiprvehbol.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZmcmRveGhkcGh4aXBydmVoYm9sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3NTY3NDcsImV4cCI6MjA2NjMzMjc0N30.yR7NpRTfvpfhng5xMSx49Ij1Z3ReSWwSVsRmqLqzIDM

# Development Settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Server Configuration (Optional)
HOST=0.0.0.0
PORT=8000
RELOAD=true
EOF

echo -e "${GREEN}✅ API Keys automatisch konfiguriert!${NC}"

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
echo -e "${GREEN}✅ API Keys bereits konfiguriert!${NC}"
echo ""
echo "🎯 Fertig! Führe aus:"
echo "   source ~/.zshrc"
echo "   rag status"
echo ""
echo "🚀 Raggadon ist sofort einsatzbereit!"