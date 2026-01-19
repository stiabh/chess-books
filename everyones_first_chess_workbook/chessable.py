import re

import requests

HEADERS = {
    "cookie": "intercom-id-qzot1t7g=4e5a03a7-4710-4c75-a13b-112c0817f53d; intercom-session-qzot1t7g=; intercom-device-id-qzot1t7g=faf68d2b-22f2-450c-83a2-d5665890ee31; uidsessid=2085854; unamesessid=Stiahans; loginstringsessid=d04b160b918e6880%3A02992b1619d782ea0054d032e74cab1c; sec_session_id=c8d9c95a1db6075070bcdfe4f554dd28; amp_dfb317=eVmPuTdiWceakFXg5HnL0D.MjA4NTg1NA==..1jf88oksj.1jf88p3nr.4n.j.5a",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}

HEADERS_V1 = {
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njg3MzI0OTcsImV4cCI6MTc2OTMzNzI5NywidXNlciI6eyJ1aWQiOjIwODU4NTQsInVuYW1lIjoiU3RpYWhhbnMiLCJzaG93T3ZlciI6dHJ1ZSwiY3VycmVudF9jbGFzcyI6InJvb2siLCJjdXJyZW50X2NsYXNzX2NvbG9yIjoiYmFkZ2VNb2ppdG8iLCJzdHJlYWtfbWF4X2JhZGdlX2RhdGEiOnsibWluIjo1LCJjb2xvciI6IlRpdGFuaXVtIiwic3RyZWFrX2JhZGdlX2ljb24iOiI1In0sInJhbmtfdGl0bGUiOiJSb29raWUiLCJyYW5rX3F1b3RlIjoiUGxheSB0aGUgb3BlbmluZyBsaWtlIGEgYm9vaywgdGhlIG1pZGRsZWdhbWUgbGlrZSBhIG1hZ2ljaWFuLCBhbmQgdGhlIGVuZGdhbWUgbGlrZSBhIG1hY2hpbmUuIiwicmFua19xdW90ZV9hdXRob3IiOiJSdWRvbHBoIFNwaWVsbWFubiIsInBlcmNlbnRfbmV4dF9yYW5rIjoiOTklIiwicG9pbnRfbmV4dF9yYW5rIjoiODAiLCJuZXh0X3JhbmtfdGl0bGUiOiJBcHByZW50aWNlIiwibmV4dF9jbGFzc19jb2xvciI6ImJhZGdlTW9qaXRvIiwibmV4dF9jbGFzcyI6InF1ZWVuIiwiaXNGaXJzdEdhbWVUb2RheSI6ZmFsc2UsInVucmVhZCI6Mjc3LCJzdHVkZW50X29mIjpudWxsLCJoYXNfc3R1ZGVudHMiOjAsImhhc19jbGFzc3Jvb20iOjAsImlzX3N1YmNvYWNoIjpmYWxzZSwiY2xhc3Nyb29tX2xpc3QiOltdLCJjbGFzc2VzX2xpc3QiOltdLCJ0aW1lem9uZSI6IlVUQyIsImVtYWlsIjoiU3RpYWhhbnNAZ21haWwuY29tIiwicG9pbnRzIjo5OTIwLCJydWJ5IjoyMCwiYm9va3NfcGVuZGluZ19hcHByb3ZhbCI6MCwicHJlbWl1bV90b3RpbWUiOjE3NjkxNTE4OTQsInNraXBfdHV0b3JpYWwiOjIsInNpZ251cF9maW5pc2hlZCI6MSwic3RyZWFrX2N1cnJlbnQiOjUsInN0cmVha19tYXgiOjUsInN0cmVha19pc19jdXJyZW50bHlfZnJvemVuIjpudWxsLCJib251c19mcmVlemUiOjAsImJvbnVzX3N0cmVha19kYXRlIjpudWxsLCJpbWFnZV9zbWFsbCI6bnVsbCwiaW1hZ2VfbWVkaXVtIjpudWxsLCJpbWFnZV9sYXJnZSI6bnVsbCwiZW1haWxfdmVyaWZpZWQiOjEsImlzX2F1dGhvciI6MCwiam9pbmVkX29uX3RvdGltZSI6MTczNzIzMDIxMywibnVtYmVyT2ZJdGVtc0luQ2FydCI6MCwiaGFzX2Jvb2siOjEsImNoZWNrb3V0X2N1cnJlbmN5IjoiVVNEIiwiY2hlc3Nib2FyZF9kZXNpZ24iOm51bGwsImNoZXNzX3BpZWNlc19kZXNpZ24iOiJuZW8iLCJzZXNzaW9uX251bWJlciI6MTgsIm5ld19jb3Vyc2VzIjowLCJyYW5rQmFkZ2UiOnsiaWQiOjEsIm5hbWUiOiJSb29raWUiLCJ0aXRsZSI6IjksOTIwIiwiZGVzY3JpcHRpb24iOiJSZWFjaGVkIHRoaXMgQ2hlc3NhYmxlIHJhbmsuIiwidHlwZSI6InJhbmsiLCJpY29uIjoidHJlZSIsInJhcml0eUNsYXNzIjoicmFuazQiLCJjb3VudCI6MjQsInZhbHVlIjo0LCJpc0FjaGlldmVkIjp0cnVlLCJleHRyYURhdGEiOm51bGwsImFjaGlldmVkQXQiOjE3Njg3MzI0OTcsInF1b3RlIjoiUGxheSB0aGUgb3BlbmluZyBsaWtlIGEgYm9vaywgdGhlIG1pZGRsZWdhbWUgbGlrZSBhIG1hZ2ljaWFuLCBhbmQgdGhlIGVuZGdhbWUgbGlrZSBhIG1hY2hpbmUuIiwicXVvdGVBdXRob3IiOiJSdWRvbHBoIFNwaWVsbWFubiJ9LCJuZXh0UmFua0JhZGdlIjp7ImlkIjoxLCJuYW1lIjoiQXBwcmVudGljZSIsInRpdGxlIjoie3tleHRyYURhdGF9fSBwb2ludHMgdG8iLCJkZXNjcmlwdGlvbiI6IlJlYWNoZWQgdGhpcyBDaGVzc2FibGUgcmFuay4iLCJ0eXBlIjoicmFuayIsImljb24iOiJ0cmVlcyIsInJhcml0eUNsYXNzIjoicmFuazUiLCJjb3VudCI6MjQsInZhbHVlIjo1LCJpc0FjaGlldmVkIjp0cnVlLCJleHRyYURhdGEiOiI4MCIsImFjaGlldmVkQXQiOjE3Njg3MzI0OTcsInF1b3RlIjoiSW4gbGlmZSwgYXMgaW4gY2hlc3MsIGZvcmV0aG91Z2h0IHdpbnMuIiwicXVvdGVBdXRob3IiOiJDaGFybGVzIEJ1eHRvbiJ9LCJicmVhZGNydW1ic0RhdGEiOnsicmFua3MiOlt7ImJvbnVzIjowLCJ0aXRsZSI6IiJ9LHsiYm9udXMiOjUwLCJ0aXRsZSI6IiJ9LHsiYm9udXMiOjE1MCwidGl0bGUiOiIifSx7ImJvbnVzIjoyNTAsInRpdGxlIjoiIn0seyJib251cyI6MzUwLCJ0aXRsZSI6IiJ9LHsiYm9udXMiOjUwMCwidGl0bGUiOiIiLCJhY3RpdmUiOiJhY3RpdmUifSx7ImJvbnVzIjoxMDAwLCJ0aXRsZSI6IiJ9XSwidG9tb3Jyb3dSYW5rQm9udXMiOiIyIFJ1YmllcyIsImhpZGVTdHJlYWtCcmVhZENydW1icyI6dHJ1ZX0sImFkbWluVW5zYWZlIjpmYWxzZSwibW9kZXJhdG9yVW5zYWZlIjpmYWxzZSwiaXNfcHJlbWl1bV91bnNhZmUiOnRydWUsInByZW1pdW1FbmRVbnNhZmUiOiIyMDI2LTAxLTIzIDA3OjA0OjU0IiwiYWNjb3VudERlbGV0aW9uVGltZUxlZnQiOm51bGwsImFjY291bnREZWxldGlvbkRhdGVUaW1lIjpudWxsLCJyaWdodHMiOltdLCJzZWN1cmVBY2Nlc3MiOmZhbHNlLCJwZl9sYW5ndWFnZSI6ImVuIn0sImp0aSI6ImQwNGIxNjBiOTE4ZTY4ODA6MDI5OTJiMTYxOWQ3ODJlYTAwNTRkMDMyZTc0Y2FiMWMifQ.0Rr4AsKtEOtXF2JqaHS0kHt1AQJDl2HD_mLuj2Ao_HE",
    "cookie": "intercom-id-qzot1t7g=4e5a03a7-4710-4c75-a13b-112c0817f53d; intercom-session-qzot1t7g=; intercom-device-id-qzot1t7g=faf68d2b-22f2-450c-83a2-d5665890ee31; uidsessid=2085854; unamesessid=Stiahans; loginstringsessid=d04b160b918e6880%3A02992b1619d782ea0054d032e74cab1c; sec_session_id=5653e731af8be9c7d32bab394a345e0c; amp_dfb317=eVmPuTdiWceakFXg5HnL0D.MjA4NTg1NA==..1jf88oksj.1jf8aofv4.4t.k.5h",
}


def add_chapter(session: requests.Session, name: str) -> None:
    url = "https://www.chessable.com/bookadmin.php"
    params = {"bid": "398409", "a": "edit"}
    payload = {"title": name}
    response = session.post(url, data=payload, headers=headers, params=params)
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
    pass


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


chapter_data = edit_variations(session, 0)
chapter_titles = chapter_data["course"]["chapters"]
chapter_titles = [re.sub(r"\d+\. ", "", c["title"]) for c in chapter_titles]

for i, chapter_title in enumerate(chapter_titles):
    print(chapter_title)
    chapter_data = edit_variations(session, i)
    for variation in chapter_data["variations"]:
        if chapter_title not in variation["name"]:
            new_name = f"{variation['name']} - {chapter_title}"
            update_opening(variation["oid"], new_name)

# for chapter in chapters:
#     add_chapter(session, chapter)
