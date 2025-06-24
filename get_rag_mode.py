#!/usr/bin/env python3
"""
Helper script to get current RAG mode for Claude
"""
import os

def get_rag_mode():
    config_file = os.path.expanduser("~/.rag_config")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            mode = f.read().strip()
            # Convert old verbose to active
            if mode == "verbose":
                mode = "active"
                with open(config_file, 'w') as f:
                    f.write("active")
            return mode
    return "active"  # Default mode

if __name__ == "__main__":
    print(get_rag_mode())