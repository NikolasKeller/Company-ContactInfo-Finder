from flask import Flask
from app import app

# Für Vercel Serverless Functions
def handler(request):
    """Handle a request to the Vercel serverless function."""
    return app(request.headers, request.method, request.url, request.body) 