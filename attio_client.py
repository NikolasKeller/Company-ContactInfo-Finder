import requests

class AttioClient:
    def __init__(self, api_key, workspace_id):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.base_url = "https://api.attio.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search_companies(self, company_name):
        """Sucht nach Unternehmen in Attio basierend auf dem Namen"""
        url = f"{self.base_url}/workspaces/{self.workspace_id}/companies"
        params = {
            "query": company_name,
            "limit": 1
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            raise Exception(f"Fehler bei der Suche nach Unternehmen: {response.text}")
    
    def create_company(self, company_data):
        """Erstellt ein neues Unternehmen in Attio"""
        url = f"{self.base_url}/workspaces/{self.workspace_id}/companies"
        
        payload = {
            "attributes": {
                "name": company_data["name"],
                "website": company_data.get("website", ""),
                "custom_fields": {
                    "booth_number": company_data.get("booth_number", ""),
                    "event_source": company_data.get("event_source", "")
                }
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Fehler beim Erstellen des Unternehmens: {response.text}")
    
    def update_company(self, company_id, company_data):
        """Aktualisiert ein bestehendes Unternehmen in Attio"""
        url = f"{self.base_url}/workspaces/{self.workspace_id}/companies/{company_id}"
        
        payload = {
            "attributes": {
                "custom_fields": {}
            }
        }
        
        if "website" in company_data:
            payload["attributes"]["website"] = company_data["website"]
        
        if "booth_number" in company_data:
            payload["attributes"]["custom_fields"]["booth_number"] = company_data["booth_number"]
        
        if "event_source" in company_data:
            payload["attributes"]["custom_fields"]["event_source"] = company_data["event_source"]
        
        response = requests.patch(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Fehler beim Aktualisieren des Unternehmens: {response.text}") 