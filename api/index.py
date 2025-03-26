from http.server import BaseHTTPRequestHandler
import json
import anthropic
import os

class ClaudeClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Anthropic API-Schlüssel ist erforderlich")
        
        self.api_key = api_key
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

def get_html():
    return """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Unternehmensdaten-Finder</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
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
            
            .guide-step {
                display: flex;
                margin-bottom: 15px;
                align-items: flex-start;
            }
            
            .step-number {
                background-color: #f39c12;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 15px;
                flex-shrink: 0;
            }
            
            .step-content {
                flex-grow: 1;
            }
            
            .step-content h5 {
                margin-top: 0;
                margin-bottom: 5px;
            }
            
            .spinner-border {
                display: none;
                margin-left: 10px;
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
                        <button id="searchBtn" class="btn btn-primary btn-lg">
                            <i class="bi bi-search"></i> Unternehmensdaten suchen
                            <span id="spinner" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                        </button>
                    </div>
                    
                    <div id="results" class="mt-5" style="display: none;">
                        <div class="card">
                            <div class="card-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="bi bi-list-check"></i> Ergebnisse
                                    </div>
                                    <button id="exportBtn" class="btn btn-sm btn-outline-light">
                                        <i class="bi bi-download"></i> Als CSV exportieren
                                    </button>
                                </div>
                            </div>
                            <div class="card-body">
                                <p id="summary" class="text-muted"></p>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Unternehmen</th>
                                                <th>Telefon</th>
                                                <th>E-Mail</th>
                                                <th>Website</th>
                                            </tr>
                                        </thead>
                                        <tbody id="resultTable">
                                            <!-- Hier werden die Ergebnisse eingefügt -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
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
                    alert('Bitte geben Sie einen Anthropic API-Schlüssel ein.');
                    return;
                }
                
                if (!anthropicKey.startsWith('sk-ant-')) {
                    alert('Der API-Schlüssel scheint ungültig zu sein. Er sollte mit "sk-ant-" beginnen.');
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
                    
                    const response = await fetch('/api/search', {
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
                            <td><strong>${item.name}</strong></td>
                            <td>${item.phone || '-'}</td>
                            <td>${item.email || '-'}</td>
                            <td>
                                <div class="d-flex align-items-center justify-content-between">
                                    <a href="${item.website}" target="_blank" class="text-primary me-2 text-truncate" style="max-width: 70%;">${item.website || '-'}</a>
                                    ${(item.email || item.phone) && item.website ? 
                                        `<button class="btn btn-sm btn-success flex-shrink-0" 
                                            data-phone="${item.phone || ''}" 
                                            data-email="${item.email || ''}" 
                                            data-website="${item.website}">
                                            <i class="bi bi-lightning-fill"></i> Alles auf einmal
                                        </button>` : ''}
                                </div>
                            </td>
                        `;
                        
                        resultTable.appendChild(row);
                    });

                    document.getElementById('results').style.display = 'block';
                } catch (error) {
                    console.error('Fehler beim Suchen:', error);
                    alert('Es ist ein Fehler aufgetreten: ' + error.message);
                } finally {
                    document.getElementById('spinner').style.display = 'none';
                    document.getElementById('searchBtn').disabled = false;
                }
            });

            document.getElementById('exportBtn').addEventListener('click', function() {
                const table = document.getElementById('resultTable');
                const rows = table.querySelectorAll('tr');
                
                let csvContent = "Unternehmen,Telefon,E-Mail,Website\\n";
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    const rowData = Array.from(cells).slice(0, 4).map(cell => {
                        const link = cell.querySelector('a');
                        let value = link ? link.getAttribute('href') : cell.textContent;
                        
                        if (value.includes(',')) {
                            value = `"${value}"`;
                        }
                        
                        return value;
                    });
                    
                    csvContent += rowData.join(',') + '\\n';
                });
                
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.setAttribute('href', url);
                link.setAttribute('download', 'unternehmensdaten.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });

            document.addEventListener('click', function(e) {
                if (e.target.classList.contains('btn-success') || e.target.closest('.btn-success')) {
                    const button = e.target.classList.contains('btn-success') ? e.target : e.target.closest('.btn-success');
                    if (!button.hasAttribute('data-website')) return;
                    
                    const phone = button.getAttribute('data-phone');
                    const email = button.getAttribute('data-email');
                    const website = button.getAttribute('data-website');
                    
                    let contactInfo = '';
                    if (email) contactInfo += `E-Mail: ${email}\\n`;
                    if (phone) contactInfo += `Telefon: ${phone}`;
                    
                    navigator.clipboard.writeText(contactInfo).then(() => {
                        window.open(website, '_blank');
                        
                        const feedbackDiv = document.createElement('div');
                        feedbackDiv.className = 'alert alert-success position-fixed bottom-0 end-0 m-3';
                        feedbackDiv.style.zIndex = '1050';
                        feedbackDiv.innerHTML = `
                            <strong><i class="bi bi-check-circle"></i> Erfolg!</strong> Kontaktdaten kopiert und Website geöffnet.
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.body.appendChild(feedbackDiv);
                        
                        setTimeout(() => {
                            feedbackDiv.remove();
                        }, 3000);
                    });
                }
            });
        </script>
    </body>
    </html>
    """

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(get_html().encode())
        return
    
    def do_POST(self):
        if self.path == '/api/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                companies = data.get('companies', [])
                anthropic_key = data.get('anthropicKey')
                
                if not companies:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Keine Unternehmen angegeben'}).encode())
                    return
                
                if not anthropic_key:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Anthropic API-Schlüssel fehlt. Bitte geben Sie einen API-Schlüssel ein.'}).encode())
                    return
                
                # Claude-Client initialisieren
                try:
                    claude = ClaudeClient(api_key=anthropic_key)
                except ValueError as e:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': f'Fehler bei der Initialisierung des Claude-Clients: {str(e)}'}).encode())
                    return
                
                # Ergebnisse für jedes Unternehmen abrufen
                results = []
                for company in companies:
                    try:
                        result = claude.get_company_info(company)
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'name': company,
                            'phone': None,
                            'email': None,
                            'website': None
                        })
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'message': f"{len(results)} Unternehmen erfolgreich verarbeitet",
                    'data': results
                }).encode())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}'}).encode())
                return
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint nicht gefunden'}).encode())
            return