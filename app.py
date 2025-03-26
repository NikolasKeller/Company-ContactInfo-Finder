import os
from dotenv import load_dotenv

if __name__ == '__main__':
    # API-Schlüssel aus .env-Datei laden
    if os.path.exists('.env'):
        load_dotenv()
        print("Umgebungsvariablen aus .env-Datei geladen")
        print(f"ANTHROPIC_API_KEY gefunden: {os.environ.get('ANTHROPIC_API_KEY') is not None}")
    
    # Für lokale Entwicklung
    app.run(debug=True) 