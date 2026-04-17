"""HTML slide renderer — system Korean fonts, no external dependencies."""

import re
import html as _html

W, H = 1280, 720

TYPE_COLOR = {
    "background":  "#1A56DB",
    "issues":      "#D6171A",
    "problems":    "#D6171A",
    "solution":    "#057A55",
    "impact":      "#1771D3",
    "toc":         "#111827",
    "rfp":         "#D97706",
    "credentials": "#057A55",
    "timeline":    "#7654F8",
}
TYPE_ICON = {
    "background":  "📋", "issues": "⚠️", "problems": "🔍",
    "solution":    "💡", "impact": "🎯", "toc": "📑",
    "rfp":         "📌", "credentials": "🏆", "timeline": "📅",
}

_BASE = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width:1280px; height:720px; overflow:hidden;
  font-family:'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕',
              'Noto Sans KR','나눔고딕',sans-serif;
  background:#F9FAFB; color:#111827;
  -webkit-font-smoothing:antialiased;
}
"""

def _e(t):
    return _html.escape(str(t or ""))

def _strip_num(text):
    return re.sub(r'^[❶❷❸❹❺❻❼❽]\s*', '', str(text).strip())

def _parse_tag(text):
    """[레이블] content → styled pill + content."""
    text = _strip_num(text)
    m = re.match(r'^\[([^\]]+)\]\s*(.*)', text, re.DOTALL)
    if m:
        tag = _e(m.group(1))
        body = _e(m.group(2))
        return tag, body
    return None, _e(text)

def _card(text, idx, accent, fs, span=1):
    tag, body = _parse_tag(text)
    tag_html = (
        f'<span style="display:inline-block;background:{accent}18;color:{accent};'
        f'font-size:8.5px;font-weight:700;padding:1px 6px;border-radius:3px;'
        f'margin-bottom:3px;letter-spacing:.3px;">{tag}</span><br>'
    ) if tag else ""
    return f"""
    <div style="background:#fff;border-radius:6px;border-left:3px solid {accent};
                padding:12px 14px;box-shadow:0 1px 4px rgba(0,0,0,.07);
                display:flex;gap:10px;align-items:flex-start;
                height:100%;min-height:0;overflow:hidden;">
      <div style="min-width:20px;height:20px;background:{accent};border-radius:3px;
                  color:#fff;font-size:9px;font-weight:700;flex-shrink:0;
                  display:flex;align-items:center;justify-content:center;
                  margin-top:1px;">{idx}</div>
      <div style="font-size:{fs}px;line-height:1.55;color:#1F2937;word-break:keep-all;
                  flex:1;min-width:0;">{tag_html}{body}</div>
    </div>"""


# ── COVER ─────────────────────────────────────────────────────────────────
def render_cover(data):
    title = _e(data.get("title", "제안서"))
    subtitle = _e(data.get("subtitle", ""))
    creds = [
        ("1,276억", "2024년 매출 | 코스닥 상장(2025.01)"),
        ("30만+",   "연간 수강생 규모"),
        ("2,000+",  "현업 전문가 강사진"),
        ("3년",     "HolonIQ 혁신 에듀테크 연속 선정"),
    ]
    cred_html = "".join(f"""
      <div style="display:flex;align-items:center;gap:10px;padding:9px 13px;
                  background:#fff;border-radius:7px;border-left:3px solid #1A56DB;
                  box-shadow:0 1px 3px rgba(0,0,0,.06);">
        <div style="font-size:17px;font-weight:700;color:#1A56DB;min-width:52px;">{n}</div>
        <div style="font-size:10px;color:#6B7280;line-height:1.4;">{l}</div>
      </div>""" for n, l in creds)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{_BASE}</style></head><body>
<div style="display:flex;width:{W}px;height:{H}px;">
  <div style="width:490px;height:720px;
              background:linear-gradient(155deg,#1A56DB 0%,#0E3A96 100%);
              padding:55px 44px;display:flex;flex-direction:column;
              justify-content:space-between;position:relative;">
    <div style="position:absolute;top:0;left:0;width:100%;height:4px;
                background:linear-gradient(90deg,#0E9F6E,#06D6A0);"></div>
    <div style="font-size:9px;color:#93C5FD;letter-spacing:2.5px;font-weight:500;">
      BUSINESS PROPOSAL
    </div>
    <div style="font-size:25px;font-weight:700;color:#fff;line-height:1.45;
                word-break:keep-all;">{title}</div>
    <div>
      <div style="font-size:11.5px;color:#BFDBFE;line-height:1.65;margin-bottom:14px;">
        {subtitle}
      </div>
      <div style="font-size:9px;color:#93C5FD;letter-spacing:1px;">
        데이원컴퍼니 (패스트캠퍼스)
      </div>
    </div>
  </div>
  <div style="flex:1;height:720px;background:#F9FAFB;padding:48px 42px;
              display:flex;flex-direction:column;justify-content:center;gap:11px;">
    <div style="font-size:9px;color:#1A56DB;letter-spacing:2px;font-weight:600;
                margin-bottom:2px;">COMPANY OVERVIEW</div>
    {cred_html}
    <div style="margin-top:4px;padding:10px 13px;
                background:linear-gradient(90deg,#EFF6FF,#F0FDF4);
                border-radius:7px;font-size:9.5px;color:#374151;line-height:1.5;">
      IT·AX·DT 교육 국내 최고 파트너 | HolonIQ 동아시아 혁신 에듀테크 3년 연속 |
      타임지 글로벌 혁신 에듀테크 선정 | 업계 유일 소버린 AI 프로젝트 참여
    </div>
  </div>
</div></body></html>"""


# ── TOC ───────────────────────────────────────────────────────────────────
def render_toc(data, total, idx):
    points = data.get("key_points", [])
    half = (len(points) + 1) // 2
    col1, col2 = points[:half], points[half:]

    def item(pt, bar):
        return f"""
        <div style="display:flex;align-items:center;gap:12px;padding:9px 14px;
                    background:#fff;border-radius:6px;height:100%;
                    box-shadow:0 1px 3px rgba(0,0,0,.05);">
          <div style="width:3px;min-height:26px;background:{bar};align-self:stretch;
                      border-radius:2px;flex-shrink:0;"></div>
          <div style="font-size:11.5px;color:#111827;font-weight:500;
                      word-break:keep-all;">{_e(pt.strip())}</div>
        </div>"""

    n_rows = max(len(col1), len(col2))
    c1 = "".join(item(p, "#1A56DB") for p in col1)
    c2 = "".join(item(p, "#0E9F6E") for p in col2)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{_BASE}</style></head><body>
<div style="height:4px;background:#111827;"></div>
<div style="display:flex;height:{H-4}px;">
  <div style="width:210px;background:linear-gradient(180deg,#111827 0%,#1F2937 100%);
              padding:44px 30px;display:flex;flex-direction:column;
              justify-content:center;gap:10px;">
    <div style="font-size:9px;color:#9CA3AF;letter-spacing:2px;">CONTENTS</div>
    <div style="font-size:28px;font-weight:700;color:#fff;line-height:1.2;">목차</div>
    <div style="width:28px;height:3px;background:#0E9F6E;border-radius:2px;
                margin-top:4px;"></div>
    <div style="font-size:10px;color:#6B7280;margin-top:10px;line-height:1.6;">
      데이원컴퍼니<br>제안서
    </div>
  </div>
  <div style="flex:1;padding:36px 40px;height:100%;">
    <div style="display:flex;gap:10px;height:100%;">
      <div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;gap:7px;">{c1}</div>
      <div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;gap:7px;">{c2}</div>
    </div>
  </div>
</div></body></html>"""


# ── CONTENT (all other types) ─────────────────────────────────────────────
def render_content(data, total, idx):
    stype   = data.get("type", "background")
    accent  = TYPE_COLOR.get(stype, "#1A56DB")
    icon    = TYPE_ICON.get(stype, "")
    title   = _e(data.get("title", ""))
    subtitle = _e(data.get("subtitle", ""))
    so_what  = _e(data.get("so_what", ""))
    details  = _e(data.get("details", ""))
    points   = data.get("key_points", [])

    n = len(points)
    if n <= 4:
        cols, fs = 1, 14
    elif n <= 6:
        cols, fs = 2, 13
    else:
        cols, fs = 3, 11.5

    rows = (n + cols - 1) // cols
    # 행 우선 CSS Grid — 카드가 슬라이드 전체에 균등 배치
    grid_style = (
        f"display:grid;"
        f"grid-template-columns:{'1fr ' * cols};"
        f"grid-template-rows:repeat({rows},1fr);"
        f"gap:10px;height:100%;"
    )
    cards = (
        f'<div style="{grid_style}">'
        + "".join(_card(p, i + 1, accent, fs) for i, p in enumerate(points))
        + "</div>"
    )
    title_size = 17 if len(data.get("title", "")) > 32 else 19

    subtitle_block = f"""
    <div style="font-size:9px;color:#9CA3AF;font-style:italic;
                padding:2px 40px 5px;">{subtitle}</div>""" if subtitle else ""

    so_what_block = f"""
    <div style="background:{accent};padding:9px 40px;
                font-size:10.5px;font-weight:600;color:#fff;line-height:1.4;">
      ▶&nbsp;&nbsp;{so_what}
    </div>""" if so_what else ""

    details_block = f"""
    <div style="padding:6px 40px;background:#fff;border-top:1px solid #E5E7EB;
                font-size:9px;color:#9CA3AF;font-style:italic;flex-shrink:0;">
      📌&nbsp;&nbsp;{details}
    </div>""" if details else ""

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{_BASE}</style></head><body>
<div style="display:flex;flex-direction:column;height:{H}px;">
  <div style="height:4px;background:{accent};flex-shrink:0;"></div>
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
              padding:10px 40px 4px;flex-shrink:0;">
    <div style="font-size:{title_size}px;font-weight:700;color:#111827;
                line-height:1.3;word-break:keep-all;flex:1;">
      {"<span style='margin-right:7px;'>"+icon+"</span>" if icon else ""}{title}
    </div>
    <div style="font-size:9px;color:#D1D5DB;white-space:nowrap;
                margin-left:12px;padding-top:4px;">{idx}&nbsp;/&nbsp;{total}</div>
  </div>
  {subtitle_block}
  {so_what_block}
  <div style="flex:1;overflow:hidden;padding:10px 40px 8px;">
    {cards}
  </div>
  {details_block}
</div></body></html>"""


# ── DISPATCHER ────────────────────────────────────────────────────────────
def render_slide(data: dict, total_slides: int = 13, slide_idx: int = 1) -> str:
    stype = data.get("type", "background")
    if stype == "cover":
        return render_cover(data)
    elif stype == "toc":
        return render_toc(data, total_slides, slide_idx)
    else:
        return render_content(data, total_slides, slide_idx)
