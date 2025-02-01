import json
import requests
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

# 環境変数から取得
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GOOGLE_CREDENTIALS_FILE = "google_credentials.json"
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# Notion API から予定を取得
def get_notion_events():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)
    data = response.json()

    events = []
    for result in data["results"]:
        properties = result["properties"]
        
        title = properties["名前"]["title"][0]["text"]["content"]
        start_date = properties["日付"]["date"]["start"]

        events.append({
            "summary": title,
            "start": start_date
        })

    return events

# Google カレンダーに予定を登録
def add_event_to_google_calendar(event):
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=credentials)

    event_body = {
        "summary": event["summary"],
        "start": {"dateTime": event["start"], "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": event["start"], "timeZone": "Asia/Tokyo"}
    }

    event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event_body).execute()
    print(f"Event created: {event.get('htmlLink')}")

def sync_notion_to_gcal():
    events = get_notion_events()
    for event in events:
        add_event_to_google_calendar(event)

if __name__ == "__main__":
    sync_notion_to_gcal()
