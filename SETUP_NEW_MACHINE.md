# 🚀 Raggadon auf neuem Rechner einrichten

## 1. Repository klonen

```bash
cd ~/Desktop
git clone https://github.com/iamthamanic/raggadon.git
cd raggadon
```

## 2. Umgebung einrichten

```bash
# Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

## 3. Konfiguration

```bash
# .env Datei erstellen
cp .env.example .env

# .env bearbeiten und ausfüllen:
# OPENAI_API_KEY=dein-openai-key
# SUPABASE_URL=deine-supabase-url
# SUPABASE_API_KEY=dein-supabase-key
```

## 4. CLI installieren

```bash
# Rag CLI global verfügbar machen
./install_rag_cli.sh
source ~/.zshrc
```

## 5. Automatischer Start einrichten

```bash
# Service für automatischen Start installieren
./install_service.sh
```

## 6. Testen

```bash
# Status prüfen
rag status

# Falls Server nicht läuft
rag start

# Test-Eintrag
rag save "Test auf neuem Rechner"
rag search "test"
```

## 🔧 Troubleshooting

### Server läuft nicht?
```bash
# Manuell starten
./start_server.sh

# Oder im Hintergrund
nohup ./start_server.sh > raggadon.log 2>&1 &
```

### Permission Fehler?
```bash
chmod +x start_server.sh
chmod +x install_*.sh
chmod +x rag
```

### Port 8000 belegt?
Ändere Port in `main.py` (Zeile 165)