#!/bin/bash

echo "🔧 Installiere rag CLI..."

# Erstelle bin Verzeichnis im Home falls nicht vorhanden
mkdir -p ~/bin

# Kopiere rag CLI
cp rag ~/bin/rag
chmod +x ~/bin/rag

# Füge ~/bin zum PATH hinzu falls noch nicht vorhanden
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
    echo "✅ PATH wurde aktualisiert. Führe aus: source ~/.zshrc"
fi

echo "✅ rag CLI installiert!"
echo ""
echo "📝 Verwendung:"
echo "  rag save \"Wichtige Info\"  # Speichert im aktuellen Projekt"
echo "  rag search \"keyword\"      # Sucht im aktuellen Projekt"
echo "  rag status                # Prüft Server-Status"
echo ""
echo "🚀 Falls PATH nicht aktualisiert: source ~/.zshrc"