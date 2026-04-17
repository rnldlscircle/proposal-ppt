import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_website(url: str, max_chars: int = 3000) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 불필요한 태그 제거
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # 빈 줄 정리
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 20]
        result = "\n".join(lines)
        return result[:max_chars]
    except Exception as e:
        return f"[웹 스크래핑 실패: {str(e)}]"


def search_industry_news(keyword: str, max_chars: int = 2000) -> str:
    query = f"{keyword} 뉴스 트렌드 2026"
    url = f"https://search.naver.com/search.naver?where=news&query={requests.utils.quote(query)}&sort=1"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")

        articles = []
        for item in soup.select(".news_area")[:8]:
            title_tag = item.select_one(".news_tit")
            desc_tag = item.select_one(".dsc_txt_wrap")
            if title_tag:
                title = title_tag.get_text(strip=True)
                desc = desc_tag.get_text(strip=True)[:150] if desc_tag else ""
                articles.append(f"• {title}: {desc}")

        if not articles:
            return f"['{keyword}' 관련 뉴스를 가져올 수 없습니다]"
        return "\n".join(articles)[:max_chars]
    except Exception as e:
        return f"[뉴스 검색 실패: {str(e)}]"
