import requests
import pandas as pd

def getNewsArticles():
    av_api_key = "OXHQ8P3KV5KQ58RQ"
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={av_api_key}&topics=blockchain'
    
    r = requests.get(url)
    data = r.json()

    if 'feed' in data:
        articles = [
            {
                'title': item.get('title', ''),
                'summary': item.get('summary', '')
            }
            for item in data['feed']
        ]

        # Save to CSV
        df = pd.DataFrame(articles)
        df.to_csv('blockchain_news.csv', index=False)
        print("✅ Saved to blockchain_news.csv")

        return articles
    else:
        print("error in response")
        return []
