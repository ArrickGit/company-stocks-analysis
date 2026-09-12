import os
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()
FINNHUB_URL = "https://finnhub.io/api/v1/company-news" # uses company news, there are other endspoints to use

# fetched news articles for a given stock ticker within date range
def get_company_news(ticker, start_date, end_date):
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY is missing")

    response = requests.get(
        FINNHUB_URL,
        headers={
            "X-Finnhub-Token": api_key, # add the API key to the request headers
        },
        params={
            "symbol": ticker.strip().upper(),
            "from": start_date,
            "to": end_date,
        },
        timeout=10,
    )

    response.raise_for_status()
    articles = response.json()
    # print(articles)
    # print(response.json())

    if isinstance(articles, dict) and articles.get("error"):
        raise ValueError(articles["error"])

    # convert the articles to a more readable format
    results = []
    for article in articles:
        published_date = datetime.fromtimestamp(
            article["datetime"],
            tz=timezone.utc,
        )
        results.append({
            "headline": article.get("headline"),
            "summary": article.get("summary"),
            "source": article.get("source"),
            "url": article.get("url"),
            "published_date": published_date.strftime("%m/%d/%Y"),
        })

    return results

# looks back 5 days from the movement date, gather all articles and return top 5
def match_news_with_movements(move_date, articles):
    matched_articles = []
    move_date = datetime.strptime(move_date, "%m/%d/%Y").date()
    for article in articles:
        article_date = datetime.strptime(article["published_date"], "%m/%d/%Y").date()
        days_difference = (move_date - article_date).days
        if 0 <= days_difference <= 5:
            matched_articles.append((days_difference, article)) # store the days difference along with the article

    # Sort articles by days difference (closest first)
    matched_articles.sort(key=lambda x: x[0])

    return [article for i, article in matched_articles[:5]]  # Return only the top 5 closest articles

# testing function
if __name__ == "__main__":
    news = get_company_news(
        ticker="GPRO",
        start_date="2026-04-22",
        end_date="2026-05-22",
    )

    print(f"Found {len(news)} articles")
    for article in news[:3]:
        print(article)
