import json
import os
from dotenv import load_dotenv
from groq import Groq
from .storage import get_latest_analysis

load_dotenv()

# ask_about_latest_analysis takes a question and returns an answer based on the latest stock analysis
def ask_about_latest_analysis(question):
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty")

    analysis = get_latest_analysis()

    if analysis is None:
        raise ValueError(
            "No analysis is available. Analyse a stock first."
        )

    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    compact_analysis = create_compact_context(analysis)
    analysis_context = json.dumps(compact_analysis, ensure_ascii=False)

    # giving grpo instructions and question, and asking it to answer based on the context
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You explain historical stock movements using only the supplied stock and news data. Treat news articles as possible explanations, not proof of causation. Mention relevant dates, percentage movements, headlines, and sources. If the supplied data cannot answer the question, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Stock analysis:\n{analysis_context}\n\n"
                    f"Question:\n{question}"
                ),
            },
        ],
    )

    return response.choices[0].message.content

# send a compact data version instead of original size due to limited token limit in gree grop
def create_compact_context(analysis):
    compact_analysis = {
        "ticker": analysis.get("ticker"),
        "start_date": analysis.get("start_date"),
        "end_date": analysis.get("end_date"),
        "threshold": analysis.get("threshold"),
        "major_movements": [],
    }

    for movement in analysis.get("major_movements", []):
        compact_movement = {
            "date": movement.get("date"),
            "percentage_change": movement.get("percentage_change"),
            "news": [],
        }

        for article in movement.get("news", [])[:3]:
            compact_movement["news"].append({
                "headline": article.get("headline"),
                "summary": (article.get("summary") or "")[:300],
                "source": article.get("source"),
                "published_date": article.get("published_date"),
            })

        compact_analysis["major_movements"].append(
            compact_movement
        )

    return compact_analysis

# testing function
if __name__ == "__main__":
    question = "What caused the major stock movements for NVDA between 2026-04-22 and 2026-05-22?"
    answer = ask_about_latest_analysis(question)
    print(answer)
