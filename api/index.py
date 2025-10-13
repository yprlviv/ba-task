"""
Vercel serverless function entry point for FastAPI
"""

from app.main import app

# Vercel expects the FastAPI app to be available as 'app'
handler = app
