import pandas as pd
from collections import defaultdict
from transformers import pipeline

# Load sentiment analysis pipeline (defaults to `distilbert-base-uncased-finetuned-sst-2-english`)
sentiment_model = pipeline("sentiment-analysis")

# Define broad themes
THEMES = {
    'Regulation': ['regulation', 'law', 'legal', 'bill', 'compliance', 'ban', 'policy', 'legislation'],
    'Finance': ['finance', 'investment', 'bank', 'economy', 'market', 'money', 'funding'],
    'Blockchain': ['blockchain', 'decentralized', 'ledger'],
    'Crypto': ['crypto', 'bitcoin', 'ethereum', 'altcoin', 'stablecoin'],
    'Security': ['hack', 'breach', 'vulnerability', 'attack', 'scam'],
    'Politics': ['democrat', 'republican', 'trump', 'government', 'minister', 'political'],
}

def detect_themes(text):
    text = text.lower()
    return {theme for theme, keywords in THEMES.items() if any(word in text for word in keywords)}

def analyze_sentiment(text):
    result = sentiment_model(text[:512])[0]  # Truncate text to 512 tokens max
    score = result['score']
    return score if result['label'] == 'POSITIVE' else -score

def process_articles(csv_file):
    df = pd.read_csv(csv_file)
    theme_sentiments = defaultdict(list)

    for _, row in df.iterrows():
        combined = f"{row['title']} {row['summary']}"
        themes = detect_themes(combined)
        sentiment_score = analyze_sentiment(combined)

        for theme in themes:
            theme_sentiments[theme].append(sentiment_score)

    result = {
        theme: round(sum(scores)/len(scores), 3)
        for theme, scores in theme_sentiments.items() if scores
    }

    return pd.DataFrame(result.items(), columns=["theme", "avg_sentiment"]).sort_values(by='avg_sentiment', ascending=False)
