from app import app

# Für Vercel Serverless Functions
handler = app.wsgi_app 