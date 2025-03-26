import anthropic
import json
import os

class ClaudeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API-Schlüssel ist erforderlich")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def get_company_info(self, company_name):
        prompt = f"""
        Finde die folgenden Informationen für das Unternehmen "{company_name}":
        1. Telefonnummer (bevorzugt Festnetz, international formatiert)
        2. E-Mail-Adresse (bevorzugt allgemeine Kontakt-E-Mail)
        3. Website-URL (mit https://)

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
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0,
                system="Du bist ein hilfreicher Assistent, der Unternehmensinformationen recherchiert und im JSON-Format zurückgibt.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extrahiere das JSON aus der Antwort
            content = response.content[0].text
            
            # Bereinige die Antwort, falls sie nicht direkt als JSON formatiert ist
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
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