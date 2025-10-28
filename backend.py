#!/usr/bin/env python3
"""Small Flask backend proxy for the Gemini generative API.

Usage:
  - Set environment variable GEMINI_API_KEY with your API key.
  - python backend.py

Exposes:
  POST /api/gemini  -> accepts JSON {systemPrompt, userQuery} and returns {text, raw}
  Static file serving for the frontend from the repo root.
"""
import os
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder='.')

GEMINI_URL = (
    'https://generativelang-stage.googleapis.com/v1beta/models/'
    'gemini-2.5-flash-preview-09-2025:generateContent'
)
API_KEY = os.environ.get('GEMINI_API_KEY')


@app.route('/api/gemini', methods=['POST'])
def proxy_gemini():
    """Proxy endpoint. Accepts {systemPrompt, userQuery} or a full payload.
    Returns JSON with at least `text` when possible and `raw` with the original response.
    """
    if not API_KEY:
        return jsonify({'error': 'Server misconfiguration: missing GEMINI_API_KEY env var.'}), 500

    data = request.get_json(silent=True) or {}

    systemPrompt = data.get('systemPrompt')
    userQuery = data.get('userQuery')

    if systemPrompt and userQuery:
        payload = {
            'contents': [{'parts': [{'text': userQuery}]}],
            'systemInstruction': {'parts': [{'text': systemPrompt}]}
        }
    else:
        # Allow clients to pass the full Gemini payload in 'payload' or as top-level
        payload = data.get('payload') or data

    params = {'key': API_KEY}
    headers = {'Content-Type': 'application/json'}

    try:
        resp = requests.post(GEMINI_URL, params=params, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        # Return useful debug info but avoid leaking secrets
        return jsonify({'error': 'Remote API error', 'details': str(exc), 'response_text': getattr(getattr(exc, 'response', None), 'text', None)}), 502

    result = resp.json()
    # try to extract main text
    text = None
    try:
        candidate = result.get('candidates', [None])[0]
        if candidate:
            text = candidate.get('content', {}).get('parts', [None])[0].get('text')
    except Exception:
        text = None

    return jsonify({'text': text, 'raw': result})


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    # Serve static files (index.html, frontend.html, etc.) from repo root
    return send_from_directory('.', path)


if __name__ == '__main__':
    # For development only. In production use a WSGI server.
    app.run(host='127.0.0.1', port=5000, debug=True)
