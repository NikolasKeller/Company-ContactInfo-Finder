from flask import Flask
from app import app

# Für Vercel Serverless Functions
def handler(request, response):
    """Handle a request to the Vercel serverless function."""
    return app 