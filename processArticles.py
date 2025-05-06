import pandas as pd
import re
from collections import defaultdict, Counter
from nltk.corpus import stopwords
from transformers import pipeline
import nltk

# Download stopwords
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

# Load sentiment analysis pipeline (defaults to distilbert-base-uncased-finetuned-sst-2-english)
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

def clean_text(text):
    """Removes stopwords and irrelevant words from the text."""
    return [word for word in re.sub(r'[^a-zA-Z\s]', '', text.lower()).split() if word not in STOPWORDS and len(word) > 2]

def process_articles(csv_file):
    df = pd.read_csv(csv_file)
    theme_sentiments = defaultdict(list)
    theme_labels = defaultdict(list)
    theme_keywords = defaultdict(list)

    for _, row in df.iterrows():
        combined = f"{row['title']} {row['summary']}"
        themes = detect_themes(combined)
        sentiment_score = analyze_sentiment(combined)
        words = clean_text(combined)

        for theme in themes:
            theme_sentiments[theme].append(sentiment_score)
            theme_labels[theme].append('POSITIVE' if sentiment_score > 0 else 'NEGATIVE')
            theme_keywords[theme].extend(words)

    summary = []
    for theme, scores in theme_sentiments.items():
        avg = round(sum(scores)/len(scores), 3)
        label_counts = Counter(theme_labels[theme])
        dominant_label = label_counts.most_common(1)[0][0]

        top_keywords = [w for w, _ in Counter(theme_keywords[theme]).most_common(5)]

        summary.append({
            "theme": theme,
            "avg_sentiment": avg,
            "dominant_feeling": dominant_label,
            "top_keywords": top_keywords,
            "summary": f"Most articles are {dominant_label.lower()} with focus on: {', '.join(top_keywords)}"
        })

    return pd.DataFrame(summary).sort_values(by="avg_sentiment", ascending=False)
