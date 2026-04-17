from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def fetch_channel_messages(token: str, channel_name: str, limit: int = 50) -> str:
    client = WebClient(token=token)

    # 채널 이름으로 ID 조회
    channel_id = None
    try:
        result = client.conversations_list(types="public_channel,private_channel", limit=200)
        for ch in result["channels"]:
            if ch["name"] == channel_name.lstrip("#"):
                channel_id = ch["id"]
                break
    except SlackApiError as e:
        return f"[Slack 채널 조회 실패: {e.response['error']}]"

    if not channel_id:
        return f"[채널 #{channel_name}을 찾을 수 없습니다]"

    return _get_messages(client, channel_id, limit)


def search_messages_by_keyword(token: str, keyword: str, limit: int = 30) -> str:
    client = WebClient(token=token)
    try:
        result = client.search_messages(query=keyword, count=limit)
        matches = result.get("messages", {}).get("matches", [])
        if not matches:
            return f"['{keyword}' 관련 슬랙 메시지 없음]"

        lines = []
        for m in matches:
            channel = m.get("channel", {}).get("name", "unknown")
            user = m.get("username", "unknown")
            text = m.get("text", "").replace("\n", " ")[:200]
            lines.append(f"[#{channel}] {user}: {text}")
        return "\n".join(lines)
    except SlackApiError as e:
        return f"[Slack 검색 실패: {e.response['error']}]"


def _get_messages(client: WebClient, channel_id: str, limit: int) -> str:
    try:
        result = client.conversations_history(channel=channel_id, limit=limit)
        messages = result.get("messages", [])
        if not messages:
            return "[해당 채널에 메시지 없음]"

        lines = []
        for m in reversed(messages):  # 시간순 정렬
            if m.get("type") == "message" and not m.get("subtype"):
                text = m.get("text", "").replace("\n", " ")[:300]
                lines.append(f"- {text}")
        return "\n".join(lines)
    except SlackApiError as e:
        return f"[메시지 조회 실패: {e.response['error']}]"
