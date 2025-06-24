#!/bin/bash

# Raggadon Server Starter Script
cd "$(dirname "$0")"

echo "🚀 Starte Raggadon RAG-Middleware..."

# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Server starten
python main.py