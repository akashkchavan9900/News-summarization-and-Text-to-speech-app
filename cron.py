import pandas as pd
import pickle
from utils.news_scraper import scrape_news_articles
from utils.gemini_service import summarize_article, analyze_sentiment, extract_topics, compare_sentiment_coverage
from utils.text_to_speech import generate_hindi_tts
import os
import json

OUTPUT_DIR = "data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True) # Create output directory if it doesn't exist

def process_company_news(company_name):
    """
    Processes news for a given company: scrapes, analyzes, generates TTS, and saves results.
    """
    print(f"Processing news for: {company_name}")
    articles = scrape_news_articles(company_name)
    if not articles:
        print(f"No articles scraped for {company_name}.")
        return None

    processed_articles = []
    for article in articles:
        summary = summarize_article(article['Content'])
        sentiment, justification, score, _ = analyze_sentiment(article['Content']) # Ignore raw output for now
        topics = extract_topics(article['Content'])

        processed_article = {
            "Title": article['Title'],
            "Summary": summary,
            "Sentiment": sentiment,
            "Sentiment Score": score,
            "Topics": topics
        }
        processed_articles.append(processed_article)

    comparative_analysis = compare_sentiment_coverage(processed_articles)
    final_sentiment_summary = f"{company_name}'s latest news coverage is mostly {comparative_analysis['Sentiment Distribution'].get('Positive', 0) > comparative_analysis['Sentiment Distribution'].get('Negative', 0) and 'positive' or 'negative' if comparative_analysis['Sentiment Distribution'].get('Positive', 0) != comparative_analysis['Sentiment Distribution'].get('Negative', 0) else 'mixed'}, with {', '.join([f'{v} {k} article(s)' for k, v in comparative_analysis['Sentiment Distribution'].items() if v > 0])}." 
    hindi_tts_text = final_sentiment_summary
    hindi_audio_file = generate_hindi_tts(hindi_tts_text, output_filename=os.path.join(OUTPUT_DIR, f"{company_name.lower()}_sentiment_audio.mp3"))
    hindi_tts_info = {
        "Text": translator.translate(hindi_tts_text, dest='hi').text if 'translator' in globals() else "Translation unavailable", # Use translator from TTS module if available
        "Audio_URL": f"/audio/{company_name.lower()}_sentiment_audio.mp3" # Placeholder URL for API (adjust as needed)
    } if hindi_audio_file else None


    output_data = {
        "Company": company_name,
        "Articles": processed_articles,
        "Comparative Sentiment Score": comparative_analysis,
        "Final Sentiment Analysis": final_sentiment_summary,
        "Hindi_TTS": hindi_tts_info
    }

    # Save as JSON
    json_filepath = os.path.join(OUTPUT_DIR, f"{company_name.lower()}_news_sentiment.json")
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False) # Ensure UTF-8 for Hindi

    # Save as pickle (optional, if needed for faster loading in API)
    pickle_filepath = os.path.join(OUTPUT_DIR, f"{company_name.lower()}_news_sentiment.pkl")
    with open(pickle_filepath, 'wb') as f:
        pickle.dump(output_data, f)

    print(f"Processed and saved data for {company_name} to JSON: {json_filepath} and Pickle: {pickle_filepath}")
    return output_data


if __name__ == '__main__':
    company_df = pd.read_csv("data/company_list.csv")
    for company in company_df['Company Name']:
        process_company_news(company)