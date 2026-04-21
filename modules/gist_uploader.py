"""Upload HTML report to GitHub Gist and return a shareable htmlpreview URL."""

import re
import requests


def upload_report(html: str, title: str, github_token: str) -> str:
    safe = re.sub(r'[^\w가-힣\s-]', '', title)[:40].strip() or "분석보고서"
    filename = f"{safe}.html"

    resp = requests.post(
        "https://api.github.com/gists",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "description": f"제안서 사전분석 보고서 — {title}",
            "public": True,
            "files": {filename: {"content": html}},
        },
        timeout=20,
    )
    resp.raise_for_status()
    gist = resp.json()
    gist_id = gist["id"]
    owner = gist["owner"]["login"]
    raw_url = f"https://gist.githubusercontent.com/{owner}/{gist_id}/raw/{filename}"
    return f"https://htmlpreview.github.io/?{raw_url}"
