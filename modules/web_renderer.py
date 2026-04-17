"""Web report renderer — dashboard-style 4-section analysis panels."""

import html as _html

_FONTS = ("'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕',"
          "'Noto Sans KR','나눔고딕',sans-serif")

_BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body, .report-root {{
  font-family:{_FONTS};
  background:#0F1117; color:#E5E7EB;
  -webkit-font-smoothing:antialiased;
}}
"""


def _e(t):
    return _html.escape(str(t or ""))


def _section_html(section: dict) -> str:
    acc     = section.get("accent", "#1A56DB")
    acc_e   = _e(acc)
    label   = _e(section.get("label", "01"))
    title   = _e(section.get("title", ""))
    sub     = _e(section.get("subtitle", ""))
    sw      = _e(section.get("so_what", ""))
    pts     = section.get("points", [])

    # ── section header ───────────────────────────────────────
    header = f"""
    <div style="display:flex;align-items:center;gap:16px;
                padding:20px 28px 18px;
                background:linear-gradient(90deg,{acc_e}22 0%,transparent 100%);
                border-bottom:1px solid {acc_e}33;">
      <div style="font-size:40px;font-weight:900;color:{acc_e};
                  opacity:.35;line-height:1;letter-spacing:-2px;flex-shrink:0;">{label}</div>
      <div>
        <div style="font-size:18px;font-weight:800;color:#F9FAFB;letter-spacing:-.3px;">{title}</div>
        <div style="font-size:11px;color:#6B7280;margin-top:3px;letter-spacing:.3px;">{sub.upper()}</div>
      </div>
      <div style="margin-left:auto;background:{acc_e}22;border:1px solid {acc_e}44;
                  border-radius:6px;padding:8px 16px;max-width:560px;">
        <div style="font-size:10px;color:{acc_e};font-weight:700;
                    letter-spacing:.8px;margin-bottom:4px;">KEY INSIGHT</div>
        <div style="font-size:12px;color:#D1D5DB;line-height:1.55;">{sw}</div>
      </div>
    </div>"""

    # ── cards ────────────────────────────────────────────────
    cards_html = ""
    for i, pt in enumerate(pts):
        tag      = _e(pt.get("tag", ""))
        stat     = _e(pt.get("stat") or "")
        headline = _e(pt.get("headline", ""))
        body     = _e(pt.get("body", ""))

        # split body sentences for visual paragraph spacing
        sentences = [s.strip() for s in body.replace("。","。|").replace(". ",".|").split("|") if s.strip()]
        body_html = "".join(
            f'<p style="margin-bottom:6px;color:#9CA3AF;">{s}</p>'
            for s in sentences
        )

        stat_block = (
            f'<div style="font-size:30px;font-weight:900;color:{acc_e};'
            f'line-height:1;margin-bottom:4px;letter-spacing:-1px;">{stat}</div>'
            f'<div style="width:24px;height:2px;background:{acc_e};'
            f'border-radius:2px;margin-bottom:10px;"></div>'
        ) if stat else (
            f'<div style="width:3px;height:36px;background:{acc_e};'
            f'border-radius:2px;margin-bottom:10px;opacity:.6;"></div>'
        )

        num_badge = (
            f'<div style="width:22px;height:22px;border-radius:4px;'
            f'background:{acc_e};color:#fff;font-size:10px;font-weight:800;'
            f'display:flex;align-items:center;justify-content:center;'
            f'flex-shrink:0;margin-bottom:10px;">{i+1}</div>'
        )

        cards_html += f"""
        <div style="background:#1A1D27;border-radius:10px;border:1px solid #2D3142;
                    border-top:2px solid {acc_e};padding:20px 22px;
                    display:flex;flex-direction:column;">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;
                      gap:8px;margin-bottom:10px;">
            {num_badge}
            <span style="background:{acc_e}18;color:{acc_e};font-size:9px;
                         font-weight:700;padding:3px 9px;border-radius:20px;
                         letter-spacing:.5px;white-space:nowrap;">{tag}</span>
          </div>
          {stat_block}
          <div style="font-size:13.5px;font-weight:700;color:#F3F4F6;
                      line-height:1.55;margin-bottom:12px;word-break:keep-all;">{headline}</div>
          <div style="font-size:12px;line-height:1.8;word-break:keep-all;flex:1;">
            {body_html}
          </div>
        </div>"""

    grid = f"""
    <div style="display:grid;grid-template-columns:repeat(2,1fr);
                gap:14px;padding:20px 28px 24px;">
      {cards_html}
    </div>"""

    return f"""
    <div style="background:#13161F;border-radius:12px;overflow:hidden;
                border:1px solid #2D3142;margin-bottom:20px;
                box-shadow:0 8px 32px rgba(0,0,0,.4);">
      {header}
      {grid}
    </div>"""


def render_section_html(section: dict) -> str:
    """Single section for st.components.v1.html() embedding."""
    body = _section_html(section)
    return f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<style>{_BASE_CSS}
body {{ background:#0F1117; padding:12px 8px 4px; }}
</style>
</head><body>{body}</body></html>"""


def render_full_page(analysis: dict) -> str:
    """Standalone downloadable HTML page."""
    title  = _e(analysis.get("title", "분석 보고서"))
    client = _e(analysis.get("client", ""))
    date   = _e(analysis.get("date", "2026년"))

    sections_html = "".join(_section_html(s) for s in analysis.get("sections", []))

    page_header = f"""
    <div style="padding:36px 32px 28px;border-bottom:1px solid #2D3142;margin-bottom:28px;">
      <div style="font-size:10px;color:#6B7280;letter-spacing:3px;margin-bottom:8px;">
        PROPOSAL ANALYSIS REPORT
      </div>
      <div style="font-size:28px;font-weight:900;color:#F9FAFB;line-height:1.3;
                  word-break:keep-all;margin-bottom:6px;">{title}</div>
      <div style="font-size:12px;color:#6B7280;">{client}&nbsp;&nbsp;|&nbsp;&nbsp;{date}</div>
    </div>"""

    return f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{_BASE_CSS}
body {{ padding:0 32px 48px;max-width:1200px;margin:0 auto; }}
</style>
</head><body>
{page_header}
{sections_html}
</body></html>"""


def section_display_height(section: dict) -> int:
    pts  = len(section.get("points", []))
    rows = (pts + 1) // 2
    # header ~120 + per row ~260
    return 140 + rows * 280 + 40
