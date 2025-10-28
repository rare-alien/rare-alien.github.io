# Backend proxy for frontend IA calls

This small repo addition implements a local Flask backend that proxies requests to the Gemini generative API so the frontend doesn't need to embed the API key client-side.

Quick start (Windows PowerShell):

1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Set your Gemini API key (do NOT commit this)

```powershell
$env:GEMINI_API_KEY = 'YOUR_KEY_HERE'
```

3. Run the backend

```powershell
python backend.py
```

4. Open the frontend in your browser

Navigate to http://127.0.0.1:5000/frontend.html (or to `index.html`) and use the IA buttons. The frontend will call `/api/gemini` on the same host.

Notes:
- The backend extracts `text` from the Gemini response and also returns the raw response under `raw` for debugging.
- For production, run the app behind a proper WSGI server and protect the API key.
