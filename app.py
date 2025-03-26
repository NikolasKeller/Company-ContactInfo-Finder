import os
import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import re
from claude_client import ClaudeClient
import concurrent.futures
from dotenv import load_dotenv

# Laden der Umgebungsvariablen am Anfang der Datei
load_dotenv()

app = Flask(__name__)

# API-Konfiguration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    companies = data.get('companies', [])
    anthropic_key = data.get('anthropicKey') or os.environ.get('ANTHROPIC_API_KEY')
    
    if not companies:
        return jsonify({'error': 'Keine Unternehmen angegeben'}), 400
    
    # Claude-Client initialisieren
    claude = ClaudeClient(api_key=anthropic_key)
    
    # Ergebnisse für jedes Unternehmen parallel abrufen
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_company = {executor.submit(claude.get_company_info, company): company for company in companies}
        for future in concurrent.futures.as_completed(future_to_company):
            company = future_to_company[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Fehler bei {company}: {e}")
                results.append({
                    'name': company,
                    'phone': None,
                    'email': None,
                    'website': None
                })
    
    return jsonify({
        'message': f"{len(results)} Unternehmen erfolgreich verarbeitet",
        'data': results
    })

# Für Vercel Serverless Functions
# Der Einstiegspunkt muss 'app' sein
app.debug = False

# Nur für lokale Entwicklung
if __name__ == '__main__':
    print(f"ANTHROPIC_API_KEY gefunden: {os.environ.get('ANTHROPIC_API_KEY') is not None}")
    app.run(debug=True) 