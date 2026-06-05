import json
import os
from datetime import datetime

DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"research_history": [], "pdf_library": [], "settings": {
            "model": "groq/llama-3.3-70b-versatile",
            "max_results": 5,
            "max_pdf_chars": 2000
        }}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_research(query, report, time_taken):
    db = load_db()
    db["research_history"].append({
        "id": len(db["research_history"]) + 1,
        "query": query,
        "report": report,
        "time_taken": time_taken,
        "date": datetime.now().strftime("%B %d, %Y %I:%M %p")
    })
    save_db(db)

def get_research_history():
    db = load_db()
    return db["research_history"]

def save_pdf(filename, content_preview):
    db = load_db()
    existing = [p for p in db["pdf_library"] if p["filename"] == filename]
    if not existing:
        db["pdf_library"].append({
            "id": len(db["pdf_library"]) + 1,
            "filename": filename,
            "preview": content_preview[:200],
            "date": datetime.now().strftime("%B %d, %Y %I:%M %p")
        })
        save_db(db)

def get_pdf_library():
    db = load_db()
    return db["pdf_library"]

def get_settings():
    db = load_db()
    return db["settings"]

def save_settings(settings):
    db = load_db()
    db["settings"].update(settings)
    save_db(db)