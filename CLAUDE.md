# Raggadon Integration für Claude Code

Dieses Dokument definiert, wie Claude Code mit Raggadon interagieren soll.

## Befehle

Wenn der User einen der folgenden Befehle eingibt, führe die entsprechende Aktion aus:

### `rag status`
Zeige den Status des Raggadon-Servers und das aktuelle Projekt.

### `rag save`
Speichere automatisch relevante Informationen aus dem aktuellen Kontext:
- Code-Snippets die besprochen werden
- Wichtige Entscheidungen
- Projekt-Struktur Informationen
- API-Definitionen
- Konfigurationen

### `rag search <begriff>`
Suche nach Informationen im Projektgedächtnis.

### `rag summary`
Zeige eine Zusammenfassung der gespeicherten Informationen für das aktuelle Projekt.

## Automatische Integration

Claude sollte proaktiv:
1. Wichtige Informationen in Raggadon speichern wenn sie besprochen werden
2. Bei Fragen zuerst in Raggadon nach vorherigen Informationen suchen
3. Den User informieren wenn relevante Informationen gefunden wurden

## Projekt-Kontext

Das aktuelle Projekt wird automatisch aus dem Verzeichnisnamen ermittelt.