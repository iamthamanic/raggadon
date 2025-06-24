#!/bin/bash

# Raggadon Service Installer für macOS

SERVICE_NAME="com.raggadon.server"
PLIST_FILE="raggadon.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🔧 Installiere Raggadon als Systemdienst..."

# Erstelle LaunchAgents Verzeichnis falls es nicht existiert
mkdir -p "$LAUNCH_AGENTS_DIR"

# Kopiere plist Datei
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# Lade den Service
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "✅ Raggadon Service installiert!"
echo "📍 Server startet automatisch bei Login"
echo "🔧 Befehle:"
echo "   Start:   launchctl start $SERVICE_NAME"
echo "   Stop:    launchctl stop $SERVICE_NAME"
echo "   Status:  launchctl list | grep raggadon"
echo "   Remove:  launchctl unload $LAUNCH_AGENTS_DIR/$PLIST_FILE"