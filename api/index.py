from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import anthropic
import json

app = Flask(__name__)

# Vercel-Handler
class handler:
    def __call__(self, req):
        return app(req)

class ClaudeClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Anthropic API-Schlüssel ist erforderlich")
        
        self.api_key = api_key
        # Einfache Initialisierung ohne try/except
        self.client = anthropic.Client(api_key=self.api_key)
    
    def get_company_info(self, company_name):
        prompt = f"""
        Finde die folgenden Informationen für das Unternehmen "{company_name}":
        1. Telefonnummer (bevorzugt Festnetz, international formatiert mit Ländercode)
        2. E-Mail-Adresse (bevorzugt allgemeine Kontakt-E-Mail)
        3. Website-URL (mit https://)

        Für Telefonnummern:
        - Suche nach offiziellen Kontaktseiten oder "Kontakt"-Abschnitten auf der Unternehmenswebsite
        - Achte besonders auf Telefonnummern im Header oder Footer der Website
        - Suche nach Nummern, die als "Tel:", "Phone:", "Call us:" oder ähnlich gekennzeichnet sind
        - Stelle sicher, dass die Nummer vollständig ist (mit Ländervorwahl)
        - Behalte das originale Format der Nummer bei, z.B. (239) 325-5180 oder +1 877.800.1634
        - Überprüfe die Nummer sorgfältig - sie ist ein kritisches Element

        Für E-Mail-Adressen:
        - Suche nach allgemeinen Kontakt-E-Mails wie info@unternehmen.com
        - Überprüfe die E-Mail-Adresse auf Tippfehler

        Für Website-URLs:
        - Gib die Haupt-URL des Unternehmens an, nicht Unterseiten
        - Stelle sicher, dass die URL mit http:// oder https:// beginnt

        Gib die Informationen im folgenden JSON-Format zurück:
        {{
            "name": "Unternehmensname",
            "phone": "Telefonnummer oder null",
            "email": "E-Mail-Adresse oder null",
            "website": "Website-URL oder null"
        }}

        Wenn du eine Information nicht finden kannst, setze den Wert auf null.
        Gib NUR das JSON zurück, keine Erklärungen oder zusätzlichen Text.
        """
        
        try:
            # Verwende die einfachere completion-Methode
            response = self.client.completion(
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                model="claude-3-haiku-20240307",
                max_tokens_to_sample=1500,
                temperature=0.2
            )
            content = response.completion
            
            # Bereinige die Antwort, falls sie nicht direkt als JSON formatiert ist
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                # Versuche, JSON direkt aus dem Text zu extrahieren
                import re
                json_pattern = r'\{.*\}'
                match = re.search(json_pattern, content, re.DOTALL)
                if match:
                    json_str = match.group(0)
                else:
                    json_str = content.strip()
            
            # Versuche, das JSON zu parsen
            try:
                result = json.loads(json_str)
                # Stelle sicher, dass alle erforderlichen Felder vorhanden sind
                result["name"] = result.get("name", company_name)
                result["phone"] = result.get("phone")
                result["email"] = result.get("email")
                result["website"] = result.get("website")
                return result
            except json.JSONDecodeError:
                # Fallback, wenn das JSON nicht geparst werden kann
                return {
                    "name": company_name,
                    "phone": None,
                    "email": None,
                    "website": None
                }
                
        except Exception as e:
            print(f"Fehler bei der Anfrage an Claude für {company_name}: {e}")
            return {
                "name": company_name,
                "phone": None,
                "email": None,
                "website": None
            }

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Unternehmensdaten-Finder</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            /* CSS-Stile hier */
            body {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .container {
                max-width: 1200px;
                margin-top: 30px;
                margin-bottom: 50px;
            }
            
            .card {
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                margin-bottom: 25px;
            }
            
            .card-header {
                background-color: #2c3e50;
                color: white;
                font-weight: 600;
                border-top-left-radius: 10px !important;
                border-top-right-radius: 10px !important;
            }
            
            .api-key-section {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-10">
                    <h1 class="mb-4 text-center">Unternehmensdaten-Finder</h1>
                    
                    <div class="card mb-4 guide-card">
                        <div class="card-body">
                            <h4 class="card-title"><i class="bi bi-info-circle"></i> So funktioniert's</h4>
                            
                            <div class="guide-step">
                                <div class="step-number">1</div>
                                <div class="step-content">
                                    <h5>Unternehmensliste eingeben</h5>
                                    <p>Geben Sie die Namen der Unternehmen ein, für die Sie Kontaktdaten finden möchten. Ein Unternehmen pro Zeile.</p>
                                </div>
                            </div>
                            
                            <div class="guide-step">
                                <div class="step-number">2</div>
                                <div class="step-content">
                                    <h5>Suche starten</h5>
                                    <p>Klicken Sie auf "Unternehmensdaten suchen", um die KI-gestützte Suche zu starten.</p>
                                </div>
                            </div>
                            
                            <div class="guide-step">
                                <div class="step-number">3</div>
                                <div class="step-content">
                                    <h5>Ergebnisse nutzen</h5>
                                    <p>Für jedes gefundene Unternehmen können Sie mit dem grünen "Alles auf einmal"-Button die Kontaktdaten kopieren und gleichzeitig die Website öffnen.</p>
                                </div>
                            </div>
                            
                            <div class="guide-step">
                                <div class="step-number">4</div>
                                <div class="step-content">
                                    <h5>Daten exportieren</h5>
                                    <p>Nutzen Sie den "Als CSV exportieren"-Button, um alle gefundenen Daten für die weitere Verwendung zu speichern.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="api-key-section">
                        <h5><i class="bi bi-key"></i> API-Schlüssel erforderlich</h5>
                        <p>Diese Anwendung verwendet die Claude API von Anthropic, um Unternehmensinformationen zu finden. Sie benötigen einen API-Schlüssel, um fortzufahren.</p>
                        <p>So erhalten Sie einen API-Schlüssel:</p>
                        <ol>
                            <li>Besuchen Sie <a href="https://console.anthropic.com/" target="_blank">console.anthropic.com</a></li>
                            <li>Erstellen Sie ein Konto oder melden Sie sich an</li>
                            <li>Navigieren Sie zu "API Keys" und erstellen Sie einen neuen Schlüssel</li>
                            <li>Kopieren Sie den Schlüssel und fügen Sie ihn unten ein</li>
                        </ol>
                        <div class="form-group">
                            <label for="apiKey"><strong>Anthropic API-Schlüssel (erforderlich):</strong></label>
                            <input type="text" id="apiKey" class="form-control" placeholder="sk-ant-api...">
                            <small class="form-text text-muted">Ihr API-Schlüssel wird nur für diese Sitzung verwendet und nicht gespeichert.</small>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <i class="bi bi-building"></i> Unternehmensliste
                        </div>
                        <div class="card-body">
                            <div class="form-group">
                                <label for="companyList">Unternehmensnamen (ein Unternehmen pro Zeile):</label>
                                <textarea id="companyList" class="form-control" rows="10" placeholder="Beispiel:&#10;Anhui Heli Co., Ltd&#10;Anyline Inc.&#10;Apache Mills, Inc."></textarea>
                            </div>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button id="searchBtn" class="btn btn-primary">
                            <i class="bi bi-search"></i> Unternehmensdaten suchen
                            <span class="spinner-border spinner-border-sm" id="spinner" role="status" aria-hidden="true"></span>
                        </button>
                    </div>
                    
                    <div id="results" class="card mt-4" style="display: none;">
                        <div class="card-header">
                            <i class="bi bi-list-check"></i> Ergebnisse
                        </div>
                        <div class="card-body">
                            <div id="summary" class="alert alert-success"></div>
                            <div class="table-responsive">
                                <table class="table table-striped" style="width: 100%;">
                                    <thead>
                                        <tr>
                                            <th style="width: 20%;">Unternehmen</th>
                                            <th style="width: 15%;">Telefon</th>
                                            <th style="width: 15%;">E-Mail</th>
                                            <th style="width: 50%;">Website</th>
                                        </tr>
                                    </thead>
                                    <tbody id="resultTable">
                                    </tbody>
                                </table>
                            </div>
                            <button id="exportBtn" class="btn btn-success mt-3">
                                <i class="bi bi-download"></i> Als CSV exportieren
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('searchBtn').addEventListener('click', async function() {
                const companyListText = document.getElementById('companyList').value;
                if (!companyListText.trim()) {
                    alert('Bitte geben Sie mindestens ein Unternehmen ein.');
                    return;
                }
                
                const companies = companyListText.split('\\n')
                    .map(company => company.trim())
                    .filter(company => company.length > 0);
                
                // API-Schlüssel aus dem Eingabefeld holen
                const apiKeyInput = document.getElementById('apiKey');
                const anthropicKey = apiKeyInput ? apiKeyInput.value.trim() : '';
                
                if (!anthropicKey) {
                    alert('Bitte geben Sie einen Anthropic API-Schlüssel ein. Dieser ist erforderlich, um die Suche durchzuführen.');
                    apiKeyInput.focus();
                    return;
                }
                
                if (!anthropicKey.startsWith('sk-ant-')) {
                    alert('Der eingegebene API-Schlüssel scheint ungültig zu sein. Anthropic API-Schlüssel beginnen mit "sk-ant-".');
                    apiKeyInput.focus();
                    return;
                }
                
                // UI-Elemente aktualisieren
                document.getElementById('spinner').style.display = 'inline-block';
                document.getElementById('searchBtn').disabled = true;
                document.getElementById('results').style.display = 'none';
                
                try {
                    const requestData = {
                        companies: companies,
                        anthropicKey: anthropicKey
                    };
                    
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(requestData)
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        alert(data.error);
                        throw new Error(data.error);
                    }
                    
                    // Ergebnisse anzeigen
                    document.getElementById('summary').textContent = data.message;
                    
                    const resultTable = document.getElementById('resultTable');
                    resultTable.innerHTML = '';
                    
                    data.data.forEach(item => {
                        const row = document.createElement('tr');
                        
                        row.innerHTML = `