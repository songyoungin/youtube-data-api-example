import random
from datetime import date, datetime, timedelta, timezone
from typing import Any
from googleapiclient.discovery import build

from dotenv import load_dotenv
from rich import print as rprint
import os

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def get_daily_search(query: str, today: date, max_pages: int = 5, window_days: int = 30) -> Any:
    # 실행 일자를 기준으로 랜덤 시드 / 오프셋 생성
    seed = int(today.strftime("%Y%m%d"))
    rnd = random.Random(seed)
    offset = rnd.randrange(window_days)
    page_index = rnd.randrange(max_pages)

    rprint(f"Today: {today}, Window days: {window_days}, Offset: {offset}, Page index: {page_index}")

    # 검색 기간 설정
    publishedAfter = (
        datetime.combine(today - timedelta(days=offset + window_days), datetime.min.time()).isoformat() + "Z"
    )
    publishedBefore = datetime.combine(today - timedelta(days=offset), datetime.min.time()).isoformat() + "Z"

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "relevance",
        "publishedAfter": publishedAfter,
        "publishedBefore": publishedBefore,
        "maxResults": 5,
        "regionCode": "KR",
        "relevanceLanguage": "ko",
    }
    rprint(params)

    # Youtube Data API 검색 요청
    response = youtube.search().list(**params).execute()

    # 페이지 인덱스만큼 반복 검색
    token = None
    for _ in range(page_index):
        token = response.get("nextPageToken")
        response = youtube.search().list(pageToken=token, **params).execute()

    return response["items"]


def main():
    query = "바나나 잎 혈당 스파이크"
    for days_ago in range(7):
        today = datetime.now(timezone.utc).date() - timedelta(days=days_ago)
        results = get_daily_search(query, today)
        rprint(results)


if __name__ == "__main__":
    main()
