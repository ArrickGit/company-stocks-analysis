from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.llm_chat import ask_about_latest_analysis
from app.news import get_company_news, match_news_with_movements
from app.stocks import get_major_movements
from app.storage import save_analysis

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Stock Movement Explainer",
    description="Finds major stock movements and relevant news.",
)

class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
    )

# main page
@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(BASE_DIR / "index.html")

# analysis endpoint returns major stock movements and relevant news articles
@app.get("/analysis/{ticker}")
def analyse_stock(
    ticker: str,
    start_date: str = Query(description="Start date in MM/DD/YYYY format"),
    end_date: str = Query(description="End date in MM/DD/YYYY format"),
    threshold: float = Query(default=2.0, gt=0),
):
    try:
        parsed_start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
        parsed_end_date = datetime.strptime(end_date, "%m/%d/%Y").date()
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail="Dates must use MM/DD/YYYY format, for example 01/31/2025",
        ) from error

    if parsed_start_date >= parsed_end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date",
        )

    try:
        movements = get_major_movements(
            ticker=ticker,
            start_date=parsed_start_date.isoformat(),
            end_date=parsed_end_date.isoformat(),
            threshold=threshold,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    unique_news_urls = set()

    # Fetches a small news window for each movement so heavily covered companies
    for movement in movements:
        movement_date = datetime.strptime(
            movement["date"],
            "%m/%d/%Y",
        ).date()
        news_start_date = movement_date - timedelta(days=5)

        try:
            articles = get_company_news(
                ticker=ticker,
                start_date=news_start_date.isoformat(),
                end_date=movement_date.isoformat(),
            )
        except Exception as error:
            raise HTTPException(
                status_code=502,
                detail="Unable to fetch news from Finnhub",
            ) from error

        movement["news"] = match_news_with_movements(
            movement["date"],
            articles,
        )

        for article in movement["news"]:
            if article.get("url"):
                unique_news_urls.add(article["url"])

    analysis = {
        "ticker": ticker.strip().upper(),
        "start_date": start_date,
        "end_date": end_date,
        "threshold": threshold,
        "movement_count": len(movements),
        "major_movements": movements,
        "unique_news_articles_matched": len(unique_news_urls),
    }

    # Save the analysis to a JSON file
    save_analysis(analysis)

    return analysis

# chat endpoint returns an answer to a question about the latest stock analysis
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        answer = ask_about_latest_analysis(
            request.question
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Unable to generate a response from Groq",
        ) from error

    return {
        "answer": answer,
    }
