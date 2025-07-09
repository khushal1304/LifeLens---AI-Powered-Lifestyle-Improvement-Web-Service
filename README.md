# 🧠 LifeLens AI Flask Backend

This is the Flask backend for the **LifeLens** project — a health advisory system powered by **Gemini 1.5 Flash**.  
It receives lifestyle or symptom data via POST requests and returns AI-generated personalized insights in structured HTML format.

---

## 🚀 Features

- 🌐 RESTful Flask API with two endpoints:
  - `/generate_suggestion`: Lifestyle survey AI analysis
  - `/analyze_symptoms`: Symptom-based diagnosis
- 🤖 Powered by Gemini 1.5 Flash (Google Generative AI)
- 🎨 Returns formatted HTML for direct JSP integration
- ✅ Deployed via Render / local development supported
- 🔒 Uses `.env` to manage Gemini API Key securely

---

## 📦 Requirements

- Python 3.8+
- Flask
- google-generativeai
- python-dotenv

Install via:

```bash
pip install -r requirements.txt

