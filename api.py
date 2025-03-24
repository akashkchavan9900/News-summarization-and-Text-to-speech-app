from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import pickle
import json
import streamlit as st
import requests

app = FastAPI()

DATA_DIR = "data/output"
AUDIO_DIR = DATA_DIR # For simplicity, assuming audio files are in the same output dir. Adjust if needed.

app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio") # Serve audio files from /audio URL

@app.get("/")
async def root():
    """
    Root endpoint to handle base URL.
    """
    return JSONResponse(content={"message": "Welcome to the News API"})

@app.get("/company/{company_name}")
def get_company_news(company_name: str):
    # Your code to fetch and process company news
    data = {
        "Company": company_name,
        "Articles": [
            {
                "Title": "Sample Article",
                "Content": "This is a sample article content.",
                "URL": "http://example.com/sample-article"
            }
        ],
        "Comparative Sentiment Score": {
            "Positive": 5,
            "Negative": 3,
            "Neutral": 2
        },
        "Final Sentiment Analysis": f"{company_name}'s latest news coverage is mostly positive.",
        "Hindi_TTS": {
            "Text": "यह एक नमूना पाठ है।",
            "Audio_URL": "/audio/sample_audio.mp3"
        }
    }
    print(data)  # Debugging statement to print the response data
    return data

@app.get("/company/{company_name}")
async def get_company_data(company_name: str):
    """
    API endpoint to get processed news data for a specific company.
    """
    json_filepath = os.path.join(DATA_DIR, f"{company_name.lower()}_news_sentiment.json")
    if os.path.exists(json_filepath):
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "Data not found for company"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) # Enable reload for development

def main():
    st.title("Company News Sentiment Analysis")

    company_name = st.text_input("Enter the company name:")
    if st.button("Get News Sentiment"):
        if company_name:
            response = requests.get(f"http://localhost:8000/company/{company_name}")
            if response.status_code == 200:
                data = response.json()
                st.write(data)  # Print the API response to see its structure
                st.header(f"News Sentiment Analysis for {data['Company']}")
                # ... existing code ...
            else:
                st.error("Error fetching data from API")

if __name__ == "__main__":
    main()