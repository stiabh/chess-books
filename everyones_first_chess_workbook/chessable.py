import re

import requests

HEADERS = {
    "cookie": "intercom-id-qzot1t7g=4e5a03a7-4710-4c75-a13b-112c0817f53d; intercom-session-qzot1t7g=; intercom-device-id-qzot1t7g=faf68d2b-22f2-450c-83a2-d5665890ee31; uidsessid=2085854; unamesessid=Stiahans; loginstringsessid=d04b160b918e6880%3A02992b1619d782ea0054d032e74cab1c; sec_session_id=c8d9c95a1db6075070bcdfe4f554dd28; amp_dfb317=eVmPuTdiWceakFXg5HnL0D.MjA4NTg1NA==..1jf88oksj.1jf88p3nr.4n.j.5a",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}

HEADERS_V1 = {
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njg4NTkyNzcsImV4cCI6MTc2OTQ2NDA3NywidXNlciI6eyJ1aWQiOjIwODU4NTQsInVuYW1lIjoiU3RpYWhhbnMiLCJzaG93T3ZlciI6dHJ1ZSwiY3VycmVudF9jbGFzcyI6InBhd24iLCJjdXJyZW50X2NsYXNzX2NvbG9yIjoiYmFkZ2VDaGVycnkiLCJzdHJlYWtfbWF4X2JhZGdlX2RhdGEiOnsibWluIjo1LCJjb2xvciI6IlRpdGFuaXVtIiwic3RyZWFrX2JhZGdlX2ljb24iOiI1In0sInJhbmtfdGl0bGUiOiJQcm92aXNpb25hbGx5IEFibGUiLCJyYW5rX3F1b3RlIjoiQ2hlc3MsIGxpa2UgbG92ZSwgbGlrZSBtdXNpYywgaGFzIHRoZSBwb3dlciB0byBtYWtlIG1lbiBoYXBweS4iLCJyYW5rX3F1b3RlX2F1dGhvciI6IlNpZWdiZXJ0IFRhcnJhc2NoIiwicGVyY2VudF9uZXh0X3JhbmsiOiI5NCUiLCJwb2ludF9uZXh0X3JhbmsiOiIxLDEzMCIsIm5leHRfcmFua190aXRsZSI6IlJhbmstcmlzZXIiLCJuZXh0X2NsYXNzX2NvbG9yIjoiYmFkZ2VDaGVycnkiLCJuZXh0X2NsYXNzIjoia25pZ2h0IiwiaXNGaXJzdEdhbWVUb2RheSI6ZmFsc2UsInVucmVhZCI6MjgxLCJzdHVkZW50X29mIjpudWxsLCJoYXNfc3R1ZGVudHMiOjAsImhhc19jbGFzc3Jvb20iOjAsImlzX3N1YmNvYWNoIjpmYWxzZSwiY2xhc3Nyb29tX2xpc3QiOltdLCJjbGFzc2VzX2xpc3QiOltdLCJ0aW1lem9uZSI6IlVUQyIsImVtYWlsIjoiU3RpYWhhbnNAZ21haWwuY29tIiwicG9pbnRzIjoxODg3MCwicnVieSI6MjEsImJvb2tzX3BlbmRpbmdfYXBwcm92YWwiOjAsInByZW1pdW1fdG90aW1lIjoxNzY5MTUxODk0LCJza2lwX3R1dG9yaWFsIjoyLCJzaWdudXBfZmluaXNoZWQiOjEsInN0cmVha19jdXJyZW50Ijo2LCJzdHJlYWtfbWF4Ijo2LCJzdHJlYWtfaXNfY3VycmVudGx5X2Zyb3plbiI6bnVsbCwiYm9udXNfZnJlZXplIjowLCJib251c19zdHJlYWtfZGF0ZSI6bnVsbCwiaW1hZ2Vfc21hbGwiOm51bGwsImltYWdlX21lZGl1bSI6bnVsbCwiaW1hZ2VfbGFyZ2UiOm51bGwsImVtYWlsX3ZlcmlmaWVkIjoxLCJpc19hdXRob3IiOjAsImpvaW5lZF9vbl90b3RpbWUiOjE3MzcyMzAyMTMsIm51bWJlck9mSXRlbXNJbkNhcnQiOjAsImhhc19ib29rIjoxLCJjaGVja291dF9jdXJyZW5jeSI6IlVTRCIsImNoZXNzYm9hcmRfZGVzaWduIjpudWxsLCJjaGVzc19waWVjZXNfZGVzaWduIjoibmVvIiwic2Vzc2lvbl9udW1iZXIiOjIxLCJuZXdfY291cnNlcyI6MCwicmFua0JhZGdlIjp7ImlkIjoxLCJuYW1lIjoiUHJvdmlzaW9uYWxseSBBYmxlIiwidGl0bGUiOiIxOCw4NzAiLCJkZXNjcmlwdGlvbiI6IlJlYWNoZWQgdGhpcyBDaGVzc2FibGUgcmFuay4iLCJ0eXBlIjoicmFuayIsImljb24iOiJwYXBlci1wbGFuZSIsInJhcml0eUNsYXNzIjoicmFuazYiLCJjb3VudCI6MjQsInZhbHVlIjo2LCJpc0FjaGlldmVkIjp0cnVlLCJleHRyYURhdGEiOm51bGwsImFjaGlldmVkQXQiOjE3Njg4NTkyNzcsInF1b3RlIjoiQ2hlc3MsIGxpa2UgbG92ZSwgbGlrZSBtdXNpYywgaGFzIHRoZSBwb3dlciB0byBtYWtlIG1lbiBoYXBweS4iLCJxdW90ZUF1dGhvciI6IlNpZWdiZXJ0IFRhcnJhc2NoIn0sIm5leHRSYW5rQmFkZ2UiOnsiaWQiOjEsIm5hbWUiOiJSYW5rLXJpc2VyIiwidGl0bGUiOiJ7e2V4dHJhRGF0YX19IHBvaW50cyB0byIsImRlc2NyaXB0aW9uIjoiUmVhY2hlZCB0aGlzIENoZXNzYWJsZSByYW5rLiIsInR5cGUiOiJyYW5rIiwiaWNvbiI6ImtpdGUiLCJyYXJpdHlDbGFzcyI6InJhbms3IiwiY291bnQiOjI0LCJ2YWx1ZSI6NywiaXNBY2hpZXZlZCI6dHJ1ZSwiZXh0cmFEYXRhIjoiMSwxMzAiLCJhY2hpZXZlZEF0IjoxNzY4ODU5Mjc3LCJxdW90ZSI6IkNoZXNzIGlzIGxpZmUgaW4gbWluaWF0dXJlLiBDaGVzcyBpcyBzdHJ1Z2dsZSwgY2hlc3MgaXMgYmF0dGxlcy4iLCJxdW90ZUF1dGhvciI6IkdhcnJ5IEthc3Bhcm92In0sImJyZWFkY3J1bWJzRGF0YSI6eyJyYW5rcyI6W3siYm9udXMiOjAsInRpdGxlIjoiIn0seyJib251cyI6NTAsInRpdGxlIjoiIn0seyJib251cyI6MTUwLCJ0aXRsZSI6IiJ9LHsiYm9udXMiOjI1MCwidGl0bGUiOiIifSx7ImJvbnVzIjozNTAsInRpdGxlIjoiIn0seyJib251cyI6NTAwLCJ0aXRsZSI6IiJ9LHsiYm9udXMiOjEwMDAsInRpdGxlIjoiIiwiYWN0aXZlIjoiYWN0aXZlIn1dLCJ0b21vcnJvd1JhbmtCb251cyI6IjIgUnViaWVzIiwiaGlkZVN0cmVha0JyZWFkQ3J1bWJzIjp0cnVlfSwiYWRtaW5VbnNhZmUiOmZhbHNlLCJtb2RlcmF0b3JVbnNhZmUiOmZhbHNlLCJpc19wcmVtaXVtX3Vuc2FmZSI6dHJ1ZSwicHJlbWl1bUVuZFVuc2FmZSI6IjIwMjYtMDEtMjMgMDc6MDQ6NTQiLCJhY2NvdW50RGVsZXRpb25UaW1lTGVmdCI6bnVsbCwiYWNjb3VudERlbGV0aW9uRGF0ZVRpbWUiOm51bGwsInJpZ2h0cyI6W10sInNlY3VyZUFjY2VzcyI6ZmFsc2UsInBmX2xhbmd1YWdlIjoiZW4ifSwianRpIjoiZDA0YjE2MGI5MThlNjg4MDowMjk5MmIxNjE5ZDc4MmVhMDA1NGQwMzJlNzRjYWIxYyJ9.FIUdUwzVcoh94HFan7eDwr0fRzT9mtM8yN5jX6BrKMA",
    "cookie": "intercom-id-qzot1t7g=4e5a03a7-4710-4c75-a13b-112c0817f53d; intercom-session-qzot1t7g=; intercom-device-id-qzot1t7g=faf68d2b-22f2-450c-83a2-d5665890ee31; uidsessid=2085854; unamesessid=Stiahans; loginstringsessid=d04b160b918e6880%3A02992b1619d782ea0054d032e74cab1c; sec_session_id=cb6d9adfd2359faf8408605bab794b0a; amp_dfb317=eVmPuTdiWceakFXg5HnL0D.MjA4NTg1NA==..1jfc24ns8.1jfc3l6gc.6c.o.74",
}


def add_chapter(session: requests.Session, name: str) -> None:
    url = "https://www.chessable.com/bookadmin.php"
    params = {"bid": "398409", "a": "edit"}
    payload = {"title": name}
    response = session.post(url, data=payload, headers=HEADERS, params=params)
    response.raise_for_status()
    print(name)


# get all variations in a chapter (response includes list of chapters)
def edit_variations(session: requests.Session, chapter_id: str | int) -> dict:
    url = "https://www.chessable.com/api/v1/editVariations"
    headers = HEADERS | HEADERS_V1
    params = {
        "bid": "396107",  # course_id
        "lid": str(chapter_id),  # chapter_id
        "includeDeleted": "0",
        "locale": "en",
    }
    response = session.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()["data"]


def update_opening(variation_id: int | str, new_name: str) -> None:
    url = "https://www.chessable.com/api/v1/updateOpening"
    headers = HEADERS | HEADERS_V1

    variation_id = str(variation_id)

    params = {
        "uid": "2085854",
        "oid": variation_id,
        "mode": "name",
        "val": new_name,
        "locale": "en",
    }

    response = session.get(url, headers=headers, params=params)
    response.raise_for_status()
    print(variation_id, new_name)


def auto_set_color(session: requests.Session, chapter_id: str | int) -> None:
    url = "https://www.chessable.com/api/v1/autoSetColor"
    headers = HEADERS | HEADERS_V1
    params = {"bid": "398409", "lid": str(chapter_id)}

    response = session.get(url, headers=headers, params=params)
    response.raise_for_status()
    print(chapter_id)


chapter_titles = [
    "Part I - General Board Visualization",
    "1. Capturing Free Pieces",
    "2. Counting Attackers and Defenders",
    "3. Intro to Defense",
    "4. Assorted Checkmates in One",
    "Part II - Introduction to Chess Tactics",
    "5. Forks",
    "6. Pins",
    "7. Skewer",
    "8. Discovered Attack",
    "9. Discovered Check and Double Check",
    "10. Removing the Guard",
    "11. In-Between Move",
    "12. Decoy",
    "13. Overloaded",
    "14. X-Ray",
    "15. Interference",
    "16. Trapping Pieces",
    "17. Defense/Recognizing Threats",
    "Part III - Intermediate Checkmates and Combinations",
    "18. Assorted Checkmates in Two",
    "19. Themed Checkmate Patterns",
    "20. Combinations/Setting up Tactics",
    "21. Finish like the World Champions",
]

session = requests.Session()

for i, chapter in enumerate(chapter_titles):
    auto_set_color(session, i)

# chapter_data = edit_variations(session, 0)
# chapter_titles = chapter_data["course"]["chapters"]
# chapter_titles = [re.sub(r"\d+\. ", "", c["title"]) for c in chapter_titles]

# for i, chapter_title in enumerate(chapter_titles):
#     print(chapter_title)
#     chapter_data = edit_variations(session, i)
#     for variation in chapter_data["variations"]:
#         if chapter_title not in variation["name"]:
#             new_name = f"{variation['name']} - {chapter_title}"
#             update_opening(variation["oid"], new_name)

# for chapter in chapters:
#     add_chapter(session, chapter)
