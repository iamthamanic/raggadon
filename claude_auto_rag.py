#!/usr/bin/env python3
"""
Claude Auto-RAG Integration
Dieses Script kann von Claude Code automatisch verwendet werden,
um wichtige Informationen proaktiv zu speichern.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Any

RAGGADON_URL = os.getenv("RAGGADON_URL", "http://127.0.0.1:8000")

class RaggadonAutoSaver:
    def __init__(self):
        self.project = Path.cwd().name
        self.saved_items = []
        
    def should_save(self, content: str) -> bool:
        """Entscheidet ob Content gespeichert werden soll"""
        # Wichtige Muster die gespeichert werden sollten
        important_patterns = [
            "class ", "def ", "function ",  # Code-Definitionen
            "API", "endpoint", "route",     # API-Infos
            "database", "schema", "model",   # Datenbank
            "config", "environment",         # Konfiguration
            "TODO", "FIXME", "IMPORTANT",    # Wichtige Notizen
            "architecture", "struktur",      # Architektur
            "dependency", "requirement",     # Dependencies
            "error", "bug", "issue",         # Probleme
        ]
        
        # Prüfe ob eines der Muster vorkommt
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in important_patterns)
    
    def extract_key_info(self, content: str) -> List[str]:
        """Extrahiert wichtige Informationen aus dem Content"""
        lines = content.split('\n')
        key_info = []
        
        for i, line in enumerate(lines):
            # Code-Definitionen
            if any(keyword in line for keyword in ['class ', 'def ', 'function ', 'const ', 'interface ']):
                # Nimm die Definition und die nächsten 2 Zeilen
                key_info.append('\n'.join(lines[i:min(i+3, len(lines))]))
            
            # Wichtige Kommentare
            elif any(marker in line.upper() for marker in ['TODO', 'FIXME', 'IMPORTANT', 'NOTE']):
                key_info.append(line.strip())
            
            # API Endpoints
            elif any(method in line for method in ['@app.', '@router.', 'app.get', 'app.post']):
                key_info.append('\n'.join(lines[i:min(i+5, len(lines))]))
        
        return key_info
    
    def save_to_rag(self, content: str, role: str = "assistant") -> bool:
        """Speichert Content in Raggadon"""
        try:
            response = requests.post(
                f"{RAGGADON_URL}/save",
                json={
                    "project": self.project,
                    "role": role,
                    "content": content
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def auto_save_from_conversation(self, messages: List[Dict[str, Any]]):
        """Analysiert Konversation und speichert wichtige Infos"""
        for msg in messages:
            if msg.get("role") in ["user", "assistant"]:
                content = msg.get("content", "")
                
                # Prüfe ob wichtig
                if self.should_save(content):
                    # Extrahiere Schlüsselinfos
                    key_infos = self.extract_key_info(content)
                    
                    # Speichere jede wichtige Info
                    for info in key_infos:
                        if info and info not in self.saved_items:
                            if self.save_to_rag(info, msg["role"]):
                                self.saved_items.append(info)
                                print(f"✅ Auto-saved: {info[:50]}...")

# CLI für Tests
if __name__ == "__main__":
    saver = RaggadonAutoSaver()
    
    if len(sys.argv) > 1:
        content = " ".join(sys.argv[1:])
        if saver.should_save(content):
            key_infos = saver.extract_key_info(content)
            for info in key_infos:
                if saver.save_to_rag(info):
                    print(f"✅ Gespeichert: {info}")
        else:
            print("ℹ️ Content nicht wichtig genug zum Speichern")
    else:
        print("Usage: python claude_auto_rag.py <content>")