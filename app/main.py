from fastapi import FastAPI
from openai import OpenAI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import date, timedelta
import os
import json

app = FastAPI()

# ---------------------------
# GROQ CONFIG
# ---------------------------

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

# ---------------------------
# GSC CONFIG
# ---------------------------

SERVICE_ACCOUNT_FILE = "foxora-seo-agent-2119f123369f.json"

def get_gsc_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=[
            "https://www.googleapis.com/auth/webmasters.readonly"
        ]
    )

    return build(
        "searchconsole",
        "v1",
        credentials=credentials
    )

def get_date_range():
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    return (
        start_date.isoformat(),
        end_date.isoformat()
    )

# ---------------------------
# BASIC ENDPOINTS
# ---------------------------

@app.get("/")
def home():
    return {
        "status": "Foxora SEO Agent Running"
    }

@app.get("/health")
def health():
    return {
        "healthy": True
    }

# ---------------------------
# SEO GENERATOR
# ---------------------------

@app.get("/seo")
def seo(keyword: str):

    prompt = f"""
Generate SEO data for keyword: {keyword}

Return ONLY valid JSON:

{{
  "keyword": "{keyword}",
  "seo_title": "",
  "meta_description": "",
  "keywords": []
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text)
        except:
            return {
                "keyword": keyword,
                "raw_response": text
            }

    except Exception as e:
        return {"error": str(e)}

@app.get("/seo/title")
def seo_title(keyword: str):

    prompt = f"""
Generate 5 SEO optimized titles for:

{keyword}

Return ONLY JSON:

{{
  "titles": []
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        return {"error": str(e)}

@app.get("/seo/meta")
def seo_meta(keyword: str):

    prompt = f"""
Generate 3 SEO meta descriptions for:

{keyword}

Return ONLY JSON:

{{
  "meta_descriptions": []
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        return {"error": str(e)}

@app.get("/seo/outline")
def seo_outline(keyword: str):

    prompt = f"""
Generate SEO outline for:

{keyword}

Return ONLY JSON:

{{
  "title": "",
  "headings": []
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        return {"error": str(e)}

@app.get("/seo/brief")
def seo_brief(keyword: str):

    prompt = f"""
Generate a complete SEO content brief for:

{keyword}

Return JSON:

{{
  "search_intent": "",
  "target_audience": "",
  "competitors": [],
  "keywords": [],
  "outline": []
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text)
        except:
            return {
                "keyword": keyword,
                "brief": text
            }

    except Exception as e:
        return {"error": str(e)}

# ---------------------------
# GOOGLE SEARCH CONSOLE
# ---------------------------

@app.get("/gsc/sites")
def gsc_sites():

    try:
        service = get_gsc_service()
        return service.sites().list().execute()

    except Exception as e:
        return {"error": str(e)}

@app.get("/gsc/keywords")
def gsc_keywords(site_url: str):

    try:
        service = get_gsc_service()

        start_date, end_date = get_date_range()

        request = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 100
        }

        return service.searchanalytics().query(
            siteUrl=site_url,
            body=request
        ).execute()

    except Exception as e:
        return {"error": str(e)}

@app.get("/gsc/pages")
def gsc_pages(site_url: str):

    try:
        service = get_gsc_service()

        start_date, end_date = get_date_range()

        request = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page"],
            "rowLimit": 100
        }

        return service.searchanalytics().query(
            siteUrl=site_url,
            body=request
        ).execute()

    except Exception as e:
        return {"error": str(e)}

