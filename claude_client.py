import os
import requests
import json

class ClaudeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API-Schlüssel ist erforderlich")
        
        print(f"API-Schlüssel verwendet: {self.api_key[:10]}...")  # Nur die ersten 10 Zeichen anzeigen
        
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    def extract_company_info(self, company_name, website_content=None):
        """
        Verwendet Claude, um Kontaktinformationen für ein Unternehmen zu extrahieren
        """
        system_prompt = """
        Du bist ein Assistent, der schnell und präzise Kontaktinformationen von Unternehmen findet.
        Extrahiere die offizielle Website, E-Mail-Adresse und Telefonnummer des Unternehmens.
        Gib nur die gefundenen Informationen zurück, ohne zusätzlichen Text.
        Formatiere die Antwort als JSON mit den Feldern "website", "email" und "phone".
        Wenn du eine Information nicht finden kannst, setze den Wert auf null.
        Antworte so schnell wie möglich.
        """
        
        # Kürzere Prompts für schnellere Antworten
        if website_content:
            user_prompt = f"""Unternehmen: {company_name}
            Extrahiere Website, E-Mail und Telefon aus diesem Inhalt:
            {website_content[:15000]}"""  # Auf 15.000 Zeichen begrenzen für schnellere Verarbeitung
        else:
            user_prompt = f"""Finde schnell Kontaktdaten für: {company_name}"""
        
        payload = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 150,  # Reduziert für schnellere Antworten
            "temperature": 0,   # Niedrigere Temperatur für konsistentere Antworten
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [])
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    
                    # Versuchen, JSON aus der Antwort zu extrahieren
                    try:
                        # Suche nach JSON in der Antwort
                        import re
                        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            json_str = text
                        
                        data = json.loads(json_str)
                        return {
                            "website": data.get("website"),
                            "email": data.get("email"),
                            "phone": data.get("phone")
                        }
                    except json.JSONDecodeError:
                        # Wenn kein gültiges JSON gefunden wurde, versuchen wir, die Informationen manuell zu extrahieren
                        website_match = re.search(r'Website:?\s*(https?://[^\s,]+)', text)
                        email_match = re.search(r'E-Mail:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                        phone_match = re.search(r'Telefon:?\s*([\+\d\s\(\)\-\.]+)', text)
                        
                        return {
                            "website": website_match.group(1) if website_match else None,
                            "email": email_match.group(1) if email_match else None,
                            "phone": phone_match.group(1) if phone_match else None
                        }
            
            # Bei Fehler
            print(f"Fehler bei der Anfrage an Claude API: {response.status_code}")
            print(response.text)
            return {"website": None, "email": None, "phone": None}
            
        except Exception as e:
            print(f"Fehler bei der Verwendung der Claude API: {str(e)}")
            return {"website": None, "email": None, "phone": None} 