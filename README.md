# ClinicAssist – AI-Powered Clinic Enquiry Assistant

ClinicAssist is a beginner-friendly educational prototype built with Python, Streamlit and the Google Gemini API. It answers general administrative questions using a small fictional clinic FAQ file, identifies common enquiry categories with simple keyword rules, and saves demo appointment requests to a local CSV file.

**Important:** The clinic and all clinic information are fictional. Do not enter real patient or personal information. This is not a medical service, does not diagnose or recommend treatment, and does not confirm appointments.

## Features

- Chat interface powered by the Gemini API.
- Responses grounded in `clinic_faq.json` with instructions not to invent missing details.
- Basic keyword-based enquiry categories (appointments, hours, fees, services, location and contact).
- Demo appointment request form that saves to `data/appointment_requests.csv`.
- FAQ and clinic information page.

## Requirements

- Python 3.11–3.15
- A Google Gemini API key
- Internet connection for the AI chatbot

## Run on Windows

1. Install Python and VS Code.
2. Open this folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

5. Activate it in PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:

   ```cmd
   .venv\Scripts\activate.bat
   ```

6. Install libraries:

   ```powershell
   pip install -r requirements.txt
   ```

7. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
8. Open `.streamlit/secrets.toml` and replace the placeholder with your own Gemini API key:

   ```toml
   GEMINI_API_KEY = "your_real_key_here"
   ```

9. Run the app:

   ```powershell
   python -m streamlit run app.py
   ```

10. Your browser should open the app. If it does not, copy the local URL shown in the terminal (usually `http://localhost:8501`).

## Get a Gemini API key

Create a key in [Google AI Studio](https://aistudio.google.com/apikey). Keep it private. Do not paste it into `app.py`, upload it to GitHub, or share it in screenshots or recordings.

## Project files

- `app.py` – Streamlit application and Gemini integration.
- `clinic_faq.json` – fictional clinic facts and FAQ answers used as chatbot context.
- `requirements.txt` – Python dependencies.
- `.streamlit/secrets.toml.example` – safe template for local API-key configuration.
- `PROMPT_LOG_TEMPLATE.md` – template for recording the prompts you actually use.
- `data/` – local demo appointment requests are saved here; the CSV file is excluded from Git.

## Notes before public deployment

The local CSV is a demo-only storage method and may not persist on a hosted app. Do not use this prototype to collect real patient information. A production service would need secure authentication, privacy controls, durable database storage, consent and appropriate healthcare/legal review.

## License

Educational demonstration project. Use and modify for learning and interview assessment.
