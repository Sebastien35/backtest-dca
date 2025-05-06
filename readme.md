# 📰 Blockchain News Sentiment Analyzer

This project fetches the latest blockchain-related news using the Alpha Vantage API, extracts titles and summaries, analyzes sentiment using Hugging Face transformers, and groups average sentiment scores by broad themes like Finance, Regulation, Crypto, etc.

## 🚀 Features

- Fetches real-time news articles on blockchain topics.
- Extracts titles and summaries for simplicity.
- Detects themes like Regulation, Finance, Crypto, etc.
- Uses Hugging Face models for accurate sentiment analysis.
- Provides a Flask API to serve simulation and news processing.
- Investment simulations

---

## 🔧 Installation

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/blockchain-news-sentiment.git
cd blockchain-news-sentiment
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run Server**
```bash
python server.py
```