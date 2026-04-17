"""Web report renderer — light theme, rich visualization, full content preserved."""

import html as _html
import re

_FONTS = ("'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕',"
          "'Noto Sans KR','나눔고딕',sans-serif")

_BASE_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');
:root {{
  --primary:#1B2A4A; --gray-50:#F9FAFB; --gray-100:#F3F4F6;
  --gray-200:#E5E7EB; --gray-500:#6B7280; --gray-700:#374151;
  --gray-900:#111827; --radius:14px;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body, .report-root {{
  font-family:'Noto Sans KR',{_FONTS};
  background:#F0F2F5; color:var(--gray-900);
  line-height:1.7; -webkit-font-smoothing:antialiased;
}}
"""


def _e(t):
    return _html.escape(str(t or ""))


def _extract_source(body: str):
    """Pull (출처: ...) from body text, return (clean_body, source)."""
    m = re.search(r'\(출처[:\s：]+([^)]+)\)', body)
    if m:
        source = m.group(1).strip()
        clean = body[:m.start()].strip() + body[m.end():].strip()
        return clean.strip(), source
    return body, ""


def _split_sentences(text: str):
    """Split Korean body text into sentence list."""
    parts = re.split(r'(?<=[다요습니까])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def _bar_chart(stat_raw: str, acc: str) -> str:
    """Descriptive stat label; adds % bar only when stat contains a % value."""
    if not stat_raw:
        return ""
    label = (
        f'<div data-e="1" style="font-size:13.5px;font-weight:700;color:{_e(acc)};'
        f'line-height:1.5;margin:8px 0 8px;word-break:keep-all;">{_e(stat_raw)}</div>'
    )
    pct_m = re.search(r'(\d+(?:\.\d+)?)\s*%', stat_raw)
    if pct_m:
        pct = min(float(pct_m.group(1)), 100)
        bar = (
            f'<div style="background:#E5E7EB;border-radius:999px;height:7px;'
            f'overflow:hidden;margin-bottom:12px;">'
            f'<div style="width:{pct:.0f}%;height:100%;'
            f'background:linear-gradient(90deg,{_e(acc)},{_e(acc)}88);'
            f'border-radius:999px;"></div></div>'
        )
        return label + bar
    return label


def _section_html(section: dict) -> str:
    acc   = section.get("accent", "#3B82F6")
    acc_e = _e(acc)
    label = _e(section.get("label", "01"))
    title = _e(section.get("title", ""))
    sub   = _e(section.get("subtitle", ""))
    sw    = _e(section.get("so_what", ""))
    pts   = section.get("points", [])

    # Section index for urgency bars (1st card = highest weight)
    n_pts = len(pts)

    # ── section header ─────────────────────────────────────
    header = f"""
    <div style="margin-bottom:24px;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
        <span style="font-size:32px;font-weight:900;color:{acc_e};
                     opacity:.2;line-height:1;letter-spacing:-2px;">{label}</span>
        <div>
          <div style="font-size:20px;font-weight:800;color:var(--primary);
                      line-height:1.25;">{title}</div>
          <div style="font-size:11px;color:var(--gray-500);
                      letter-spacing:.3px;margin-top:2px;">{sub}</div>
        </div>
      </div>
      <div style="display:flex;align-items:flex-start;gap:10px;
                  background:{acc_e}0f;border-left:3px solid {acc_e};
                  border-radius:0 8px 8px 0;padding:10px 16px;">
        <span style="font-size:11px;font-weight:700;color:{acc_e};
                     white-space:nowrap;letter-spacing:.5px;padding-top:1px;">
          KEY INSIGHT
        </span>
        <span data-e="1" style="font-size:13px;color:var(--gray-700);line-height:1.6;">{sw}</span>
      </div>
    </div>"""

    # ── cards ───────────────────────────────────────────────
    cards_html = ""
    for i, pt in enumerate(pts):
        tag      = _e(pt.get("tag", ""))
        stat_raw = pt.get("stat") or ""
        headline = _e(pt.get("headline", ""))
        raw_body = pt.get("body", "")
        clean_body, source = _extract_source(raw_body)
        sentences = _split_sentences(clean_body)

        lead    = _e(sentences[0]) if sentences else ""
        rest    = sentences[1:] if len(sentences) > 1 else []

        # urgency dots: more dots = higher priority (first cards = higher)
        urgency = n_pts - i
        dots = "".join(
            f'<span style="width:7px;height:7px;border-radius:50%;'
            f'background:{acc_e};display:inline-block;margin-right:3px;'
            f'opacity:{1.0 - j*0.22:.2f};"></span>'
            for j in range(urgency)
        ) + "".join(
            f'<span style="width:7px;height:7px;border-radius:50%;'
            f'background:#E5E7EB;display:inline-block;margin-right:3px;"></span>'
            for j in range(n_pts - urgency)
        )

        vis = _bar_chart(stat_raw, acc) if stat_raw else ""

        rest_html = "".join(
            f'<p data-e="1" style="font-size:13px;color:var(--gray-500);'
            f'line-height:1.8;margin-bottom:6px;">{_e(s)}</p>'
            for s in rest
        )

        source_html = (
            f'<div style="margin-top:10px;padding-top:8px;'
            f'border-top:1px solid var(--gray-100);'
            f'font-size:10.5px;color:var(--gray-500);font-style:italic;">'
            f'📌 출처: {_e(source)}</div>'
        ) if source else ""

        cards_html += f"""
        <div style="background:#fff;border-radius:var(--radius);
                    border:1px solid var(--gray-200);
                    border-left:4px solid {acc_e};
                    padding:20px 22px;
                    box-shadow:0 1px 4px rgba(0,0,0,0.05);
                    display:flex;flex-direction:column;
                    transition:box-shadow .15s;">
          <!-- top row -->
          <div style="display:flex;align-items:center;
                      justify-content:space-between;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:22px;height:22px;border-radius:6px;
                          background:{acc_e};color:#fff;
                          font-size:10px;font-weight:800;flex-shrink:0;
                          display:flex;align-items:center;justify-content:center;">
                {i+1}
              </div>
              <span style="background:{acc_e}15;color:{acc_e};
                           font-size:9.5px;font-weight:700;
                           padding:2px 9px;border-radius:100px;
                           letter-spacing:.3px;">{tag}</span>
            </div>
            <div style="display:flex;align-items:center;">{dots}</div>
          </div>
          <!-- stat visualization -->
          {vis}
          <!-- headline -->
          <div data-e="1" style="font-size:14.5px;font-weight:700;color:var(--primary);
                      line-height:1.55;margin-bottom:10px;word-break:keep-all;">
            {headline}
          </div>
          <!-- lead sentence -->
          <p data-e="1" style="font-size:13.5px;color:var(--gray-700);
                    line-height:1.8;margin-bottom:8px;word-break:keep-all;
                    font-weight:500;">{lead}</p>
          <!-- supporting sentences -->
          {rest_html}
          <!-- source citation -->
          {source_html}
        </div>"""

    grid = f"""
    <div style="display:grid;grid-template-columns:repeat(2,1fr);
                gap:16px;">
      {cards_html}
    </div>"""

    return f"""
    <div style="background:#fff;border-radius:18px;
                border:1px solid var(--gray-200);
                padding:28px 32px 32px;
                margin-bottom:24px;
                box-shadow:0 2px 12px rgba(0,0,0,0.05);">
      {header}
      {grid}
    </div>"""


_EDIT_JS = """
<script>
function toggleEdit(btn){
  var on=btn.dataset.on==='1';
  document.querySelectorAll('[data-e]').forEach(function(el){
    el.contentEditable=on?'false':'true';
    el.style.outline=on?'none':'2px dashed rgba(59,130,246,0.4)';
    el.style.borderRadius=on?'':'4px';
    el.style.padding=on?'':'1px 3px';
  });
  btn.dataset.on=on?'0':'1';
  btn.textContent=on?'✏️ 편집':'✓ 완료';
  btn.style.background=on?'rgba(27,42,74,0.08)':'#10B981';
  btn.style.color=on?'#374151':'#fff';
  btn.style.borderColor=on?'rgba(27,42,74,0.2)':'#10B981';
}
</script>"""

_EDIT_BTN = """
<div style="position:fixed;top:10px;right:10px;z-index:999;">
  <button onclick="toggleEdit(this)" data-on="0"
    style="background:rgba(27,42,74,0.08);color:#374151;
           border:1px solid rgba(27,42,74,0.2);border-radius:8px;
           padding:5px 13px;font-size:11px;font-weight:700;cursor:pointer;">
    ✏️ 편집
  </button>
</div>"""


def render_section_html(section: dict) -> str:
    body = _section_html(section)
    return f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<style>{_BASE_CSS}
body {{ background:#F0F2F5; padding:10px 8px 4px; }}
</style>
</head><body>{_EDIT_BTN}{body}{_EDIT_JS}</body></html>"""


def render_full_page(analysis: dict) -> str:
    title  = _e(analysis.get("title", "분석 보고서"))
    client = _e(analysis.get("client", ""))
    date   = _e(analysis.get("date", "2026년"))

    sections_html = "".join(_section_html(s) for s in analysis.get("sections", []))

    hero = f"""
    <div style="background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 55%,#2563EB 100%);
                color:#fff;padding:52px 48px 44px;margin-bottom:28px;
                border-radius:0 0 20px 20px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-40%;right:-10%;width:500px;height:500px;
                  border-radius:50%;background:rgba(59,130,246,0.12);"></div>
      <div style="position:relative;z-index:1;">
        <span style="display:inline-block;background:rgba(255,255,255,0.15);
                     border:1px solid rgba(255,255,255,0.25);
                     padding:5px 16px;border-radius:100px;
                     font-size:11px;font-weight:600;letter-spacing:1px;
                     margin-bottom:18px;">PROPOSAL ANALYSIS REPORT</span>
        <div style="font-size:28px;font-weight:800;line-height:1.35;
                    margin-bottom:8px;word-break:keep-all;">{title}</div>
        <div style="font-size:13px;opacity:.7;">{client}&nbsp;&nbsp;|&nbsp;&nbsp;{date}</div>
      </div>
    </div>"""

    fab = """
<div id="fab" style="position:fixed;bottom:28px;right:28px;z-index:9999;display:flex;gap:10px;">
  <button id="editBtn" onclick="toggleEdit(this)" data-on="0"
    style="background:#1B2A4A;color:#fff;border:none;border-radius:12px;
           padding:12px 20px;font-size:13px;font-weight:700;cursor:pointer;
           box-shadow:0 4px 16px rgba(0,0,0,0.2);">✏️ 편집</button>
  <button onclick="printPDF()"
    style="background:#2563EB;color:#fff;border:none;border-radius:12px;
           padding:12px 20px;font-size:13px;font-weight:700;cursor:pointer;
           box-shadow:0 4px 16px rgba(0,0,0,0.2);">⬇️ PDF 저장</button>
</div>"""

    pdf_js = """
<script>
function toggleEdit(btn){
  var on=btn.dataset.on==='1';
  document.querySelectorAll('[data-e]').forEach(function(el){
    el.contentEditable=on?'false':'true';
    el.style.outline=on?'none':'2px dashed rgba(59,130,246,0.4)';
    el.style.borderRadius=on?'':'4px';
    el.style.padding=on?'':'1px 3px';
  });
  btn.dataset.on=on?'0':'1';
  btn.textContent=on?'✏️ 편집':'✓ 완료';
  btn.style.background=on?'#1B2A4A':'#10B981';
}
function printPDF(){
  var editBtn=document.getElementById('editBtn');
  if(editBtn.dataset.on==='1') toggleEdit(editBtn);
  window.print();
}
</script>"""

    return f"""<!DOCTYPE html><html><head>
<meta charset="utf-8"><title>{title}</title>
<style>{_BASE_CSS}
body {{ padding:0 32px 48px;max-width:1200px;margin:0 auto; }}
@media print {{
  #fab {{ display:none !important; }}
  body {{ padding:0 16px; }}
  [data-e] {{ outline:none !important; }}
}}
</style>
</head><body>{hero}{sections_html}{fab}{pdf_js}</body></html>"""


def section_display_height(section: dict) -> int:
    pts  = len(section.get("points", []))
    rows = (pts + 1) // 2
    return 180 + rows * 320 + 40
