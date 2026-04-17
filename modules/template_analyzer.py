"""API 키 없이도 기존 제안서 수준의 스토리라인 생성기"""

import re

# ── 데이원컴퍼니 고정 크레덴셜 ──────────────────────────────
DAY1_CREDENTIALS = {
    "company": "데이원컴퍼니 (패스트캠퍼스)",
    "revenue": "2024년 매출 1,276억원, 코스닥 상장(2025.01)",
    "growth": "연평균 성장률 15% 지속 성장",
    "students": "연 30만 수강생, 업계 최대 규모 교육 플랫폼",
    "instructors": "현업 전문가 2,000명+ 강사진 즉시 투입 가능",
    "awards": "HolonIQ 동아시아 혁신 에듀테크 3년 연속 선정 | 타임지 선정 글로벌 혁신 에듀테크 기업",
    "solution": "SkillMatch™ AI 역량 진단 시스템 | 기관 맞춤형 LMS | AX 스킬셋 프레임워크",
    "unique": "업계 유일 소버린 AI 프로젝트 직접 참여 | 온프레미스 생성형 AI 개발 경험 보유",
}

SECTION_KEYWORDS = {
    "background": [
        "배경", "현황", "현재", "기존", "도입", "계기", "이유", "상황", "환경",
        "트렌드", "변화", "시장", "업계", "동향", "필요성", "목적", "목표",
        "정책", "법령", "정부", "요구", "수요", "증가", "확대", "강화",
    ],
    "issues": [
        "이슈", "문제", "과제", "어려움", "불편", "비효율", "한계", "pain",
        "불만", "부재", "부족", "누락", "지연", "오류", "낭비", "손실",
        "격차", "미흡", "부재", "불가", "실패", "저하", "취약", "부담",
    ],
    "solution": [
        "해결", "솔루션", "방안", "제안", "도입", "개선", "시스템", "플랫폼",
        "서비스", "기능", "자동화", "구축", "연동", "적용", "활용", "지원",
        "교육", "과정", "커리큘럼", "학습", "훈련", "역량", "강화", "운영",
    ],
    "impact": [
        "효과", "기대", "결과", "절감", "향상", "증가", "개선", "ROI", "%",
        "시간", "비용", "생산성", "성과", "달성", "목표", "만족", "성장",
        "내재화", "확산", "전환", "혁신", "변화", "발전", "고도화",
    ],
}

NOISE_PATTERNS = [
    r"^\d+$",
    r"^[\.\-\*\#\|]+$",
    r"^.{1,5}$",
    r"^(페이지|슬라이드|slide|page|p\.\d+)\s*\d*$",
    r"^(www\.|http|copyright|ⓒ)",
    r"^\s*None\s*$",
    r"^[\d\s\|\.\,]+$",
]

# 사용자 지시어 패턴 — 내용이 아닌 명령/요청 문장 제거
INSTRUCTION_PATTERNS = [
    r"(해줘|해주세요|해주길|반영해|참고해|넣어줘|빼줘|만들어줘|작성해줘|써줘|고쳐줘|수정해줘)$",
    r"^(줄테니|참고로|그리고|그냥|일단|나중에|혹시|아마|그거|이거)",
    r"(자료\s*줄테니|제안서\s*줄테니|파일\s*줄테니)",
    r"^(ai가|claude가|너가|당신이|gpt가)",
]


def _is_noise(line: str) -> bool:
    line = line.strip()
    for pat in NOISE_PATTERNS:
        if re.match(pat, line, re.IGNORECASE):
            return True
    for pat in INSTRUCTION_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            return True
    return False


def _score(line: str, keywords: list) -> int:
    return sum(1 for kw in keywords if kw.lower() in line.lower())


def _extract_sentences(text: str) -> list:
    raw = re.split(r"[\n]+", text)
    sentences = []
    for line in raw:
        line = line.strip()
        # 파이프(|) 구분된 슬라이드 텍스트 분리
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            sentences.extend(parts)
        elif len(line) > 200:
            parts = re.split(r"[.。!?]+", line)
            sentences.extend(p.strip() for p in parts if p.strip())
        else:
            sentences.append(line)

    cleaned = []
    for s in sentences:
        s = s.strip()
        if s and not _is_noise(s) and len(s) > 8:
            cleaned.append(s)
    return cleaned


def _classify(sentences: list) -> dict:
    buckets = {k: [] for k in SECTION_KEYWORDS}
    unclassified = []

    for s in sentences:
        scores = {k: _score(s, kws) for k, kws in SECTION_KEYWORDS.items()}
        best_k = max(scores, key=scores.get)
        if scores[best_k] > 0:
            buckets[best_k].append(s)
        else:
            unclassified.append(s)

    # 미분류는 배경으로
    buckets["background"].extend(unclassified)
    return buckets


def _pick_unique(lst: list, n: int = 5, max_len: int = 100) -> list:
    seen = set()
    result = []
    for item in lst:
        key = re.sub(r"\s+", "", item)[:20]
        if key not in seen and len(result) < n:
            seen.add(key)
            trimmed = item.strip()[:max_len]
            if len(item.strip()) > max_len:
                trimmed += "..."
            result.append(trimmed)
    return result


def _numbered(lst: list, start: int = 1) -> list:
    """❶❷❸❹❺ 번호 붙이기"""
    numbers = ["❶", "❷", "❸", "❹", "❺", "❻", "❼"]
    return [f"{numbers[i]} {item}" for i, item in enumerate(lst) if i < len(numbers)]


def _fallback(label: str) -> list:
    return [f"❶ [{label}] 관련 내용을 직접 입력하거나 파일을 업로드해주세요"]


def analyze_without_api(text: str, customer_name: str = "") -> dict:
    title = f"{customer_name} AI 역량 강화 교육 제안서" if customer_name else "AI 역량 강화 교육 제안서"
    cred = DAY1_CREDENTIALS

    sentences = _extract_sentences(text)
    buckets = _classify(sentences)

    bg = buckets["background"]
    issues = buckets["issues"]
    solutions = buckets["solution"]
    impacts = buckets["impact"]

    # 부족한 섹션 보충
    if len(issues) < 3:
        issues = issues + [s for s in bg if len(s) > 30]
    if len(solutions) < 3:
        solutions = solutions + bg[:5]
    if len(impacts) < 3:
        impacts = impacts + solutions[:5]

    def make_points(lst, fallback_label, n=5):
        picked = _pick_unique(lst, n=n)
        if not picked:
            return _fallback(fallback_label)
        return _numbered(picked)

    def make_details(lst, start=5):
        extra = _pick_unique(lst[start:], n=6, max_len=80)
        return " | ".join(extra) if extra else ""

    slides = [
        {
            "type": "cover",
            "title": title,
            "subtitle": f"{customer_name} | 데이원컴퍼니 제안" if customer_name else "데이원컴퍼니 제안서",
        },
        {
            "type": "toc",
            "title": "목차",
            "subtitle": "Contents",
            "key_points": [
                "01  사업의 이해 및 RFP 과업범위",
                "02  제안 배경 — 대외환경 및 기관 현황",
                "03  핵심 이슈 및 사업 필요성",
                "04  데이원컴퍼니 제안 방향 및 특장점",
                "05  프로젝트 수행 프레임워크 (M1·M2·M3)",
                "06  수행 방법론 상세 (M1 진단·설계 / M2 운영)",
                "07  제안사 수행 역량 및 유사 실적",
                "08  추진 일정 및 산출물 계획",
            ],
            "details": "",
        },
        {
            "type": "rfp",
            "title": "RFP상 과업범위 직접 확인 및 이행 계획",
            "subtitle": "1. 사업의 이해 > RFP 과업범위 정의",
            "so_what": "과업지시서에 명시된 모든 요구사항을 빠짐없이 이행하는 것이 본 제안의 출발점입니다",
            "key_points": make_points(bg, "사업 개요") or [
                f"❶ [사업 개요] {customer_name} 대상 AI 역량 강화 교육과정 설계 및 운영 사업",
                "❷ [핵심 과업] 수준별 AI 교육과정 개발 및 교육 운영",
                "❸ [교육 대상] 구성원 전체 대상 AI 활용 역량 교육",
                "❹ [성과 목표] 교육 만족도 90% 이상, 수료율 85% 이상 달성",
            ],
            "details": "출처: 과업지시서 직접 인용",
        },
        {
            "type": "background",
            "title": "AI 전환 가속화와 디지털 역량 강화 정책 마련 필요",
            "subtitle": "2. 제안 배경 > 대외환경 및 정책 동향",
            "so_what": "정부 AI 정책과 글로벌 산업 변화가 조직의 AI 역량 교육을 더 이상 미룰 수 없게 만들고 있습니다",
            "key_points": make_points(bg, "대외환경"),
            "details": "출처: 과학기술정보통신부, 한국지능정보사회진흥원(NIA), 가트너 리포트 등",
        },
        {
            "type": "background",
            "title": f"{customer_name} 구성원 AI 역량 현황 및 교육 수요 확보 필요",
            "subtitle": "2. 제안 배경 > 기관 현황 및 교육 수요 분석",
            "so_what": "발주기관 구성원의 AI 역량 수준과 교육 수요를 정확히 파악해 맞춤형 솔루션을 설계합니다",
            "key_points": make_points(bg[3:] + issues[:2], "기관 현황"),
            "details": make_details(bg),
        },
        {
            "type": "issues",
            "title": "AI 교육 공백으로 인한 조직 경쟁력 약화 대응 시급",
            "subtitle": "2. 제안 배경 > 핵심 이슈 및 문제점",
            "so_what": "현재 조직이 직면한 AI 역량 격차와 교육 공백이 이 사업의 시급성을 명확히 증명합니다",
            "key_points": make_points(issues, "현황 이슈"),
            "details": make_details(issues),
        },
        {
            "type": "issues",
            "title": "주요 이슈 종합 및 AI 역량 강화 사업 추진 필요성 확인",
            "subtitle": "2. 제안 배경 > 이슈 종합 및 사업 필요성",
            "so_what": "대외환경·기관현황·핵심이슈를 종합하면 지금 이 사업 추진이 최우선 과제임이 분명합니다",
            "key_points": make_points(issues[2:] + bg[4:], "이슈 종합"),
            "details": make_details(issues),
        },
        {
            "type": "solution",
            "title": "데이원컴퍼니 AI 교육 파트너십 특장점 및 기대효과",
            "subtitle": "3. 제안사 특장점 > 핵심 역량 및 차별화 요소",
            "so_what": "글로벌 공신력·검증된 실적·독보적 AI 솔루션으로 본 사업의 최적 파트너임을 증명합니다",
            "key_points": [
                f"❶ [글로벌 공신력] {cred['awards']}",
                f"❷ [사업 실적] {cred['revenue']} | {cred['growth']}",
                f"❸ [AI 진단 솔루션] {cred['solution']}",
                f"❹ [강사 인프라] {cred['instructors']}",
                f"❺ [독보적 전문성] {cred['unique']}",
            ],
            "details": cred["students"],
        },
        {
            "type": "solution",
            "title": "M1·M2·M3 모듈 기반 수행 프레임워크 구조화 필요",
            "subtitle": "4. 수행 방법론 > 프로젝트 수행 프레임워크",
            "so_what": "진단-설계-운영-성과측정이 유기적으로 연결된 M1·M2·M3 모듈 프레임워크로 교육 효과를 극대화합니다",
            "key_points": [
                "❶ [M1: 진단·설계] SkillMatch™ 역량진단 → 수준별 교육과정 설계 → 맞춤형 콘텐츠 개발 (착수 후 4주)",
                "❷ [M2: 교육 운영] 집합·온라인·혼합형 교육 운영 → 현업 전문가 강사 투입 → 프로젝트형 실습 병행",
                "❸ [M3: 성과 측정] 사후 역량진단 → 현업 적용 지원 → 성과보고서 납품 → 우수사례 공유",
                "❹ [거버넌스] 주간 운영회의, 월간 성과점검, 이슈 에스컬레이션 체계로 리스크 즉시 대응",
                "❺ [품질 관리] 강사 사전 검증, 교육자료 전문 리뷰, VOC 익일 반영 체계로 교육 품질 보장",
            ],
            "details": "수행 프레임워크: SkillMatch™ 진단 → 맞춤설계 → 전문 운영 → 성과측정 → 확산",
        },
        {
            "type": "solution",
            "title": "M1 역량진단·교육설계 및 M2 교육운영 방법론 상세",
            "subtitle": "4. 수행 방법론 상세 > M1 진단·설계 / M2 교육운영 모듈",
            "so_what": "SkillMatch™ AI 진단으로 개인별 최적 학습경로를 설계하고 전문 강사진으로 교육 만족도 90% 이상을 달성합니다",
            "key_points": make_points(solutions, "수행 방법론"),
            "details": "M1 산출물: 역량진단 결과보고서, 교육과정 설계서 | M2 산출물: 교육 운영 일지, 만족도 조사, 이수현황",
        },
        {
            "type": "credentials",
            "title": "유사 수행 실적 및 제안사 수행 역량 증명",
            "subtitle": "5. 제안사 수행 역량 > 유사 실적 및 전문성",
            "so_what": "본 사업과 동일한 유형의 교육을 이미 성공적으로 수행한 검증된 파트너입니다",
            "key_points": [
                f"❶ [유사 실적] 공공기관·기업 대상 AI·디지털 역량 교육 다수 수행 — {cred['students']}",
                f"❷ [콘텐츠 품질] {cred['awards']}",
                f"❸ [AI 기술 역량] {cred['unique']}",
                f"❹ [재무 안정성] {cred['revenue']}",
                "❺ [파트너십] AWS, MS, Google 등 주요 AI·클라우드 기업 공식 교육 파트너 네트워크 보유",
            ],
            "details": "코스닥 상장(2025.01) | 신용등급 안정 | 2013년 설립 이후 12년 지속 성장",
        },
        {
            "type": "timeline",
            "title": "추진 일정 및 산출물 계획",
            "subtitle": "6. 추진 일정 > 월별 수행 계획 및 납품 산출물",
            "so_what": "RFP 사업기간 내 모든 과업을 완료하는 단계별 추진 일정과 명확한 산출물 계획을 제시합니다",
            "key_points": [
                "❶ [착수 (M1)] 사업 착수 후 1개월 — 킥오프, SkillMatch™ 역량 진단, 교육과정 설계서 확정",
                "❷ [교육 운영 (M2)] 사업 2~N개월 — 수준별 교육과정 순차 운영, 월간 운영보고서 납품",
                "❸ [성과 측정 (M3)] 마지막 1개월 — 사후 역량진단, 결과 분석, 최종 성과보고서 납품",
                "❹ [중간 산출물] 역량진단 결과보고서, 교육과정 설계서, 강사 프로필, 월별 운영 일지",
                "❺ [최종 납품물] 최종 성과보고서, 교육 이수증, 만족도 조사 결과보고서, 우수사례 자료집",
                "❻ [일정 보장] 주간 진척 보고 및 이슈 에스컬레이션 프로세스로 납기 리스크 사전 관리",
            ],
            "details": "납품 일정은 RFP 사업기간 기준 조정 | 지연 리스크 대응계획 포함",
        },
    ]

    # key_points가 아예 없는 슬라이드만 제거
    slides = [s for s in slides if s.get("type") == "cover" or s.get("key_points")]

    return {
        "title": title,
        "one_line_summary": (
            f"데이원컴퍼니의 AI 역량 진단-교육-성과측정 체계로 {customer_name}의 AX 전환을 완성합니다"
            if customer_name
            else "진단-교육-성과측정이 연결된 데이원컴퍼니만의 AI 역량 강화 솔루션"
        ),
        "narrative_thread": (
            "정책·환경 변화로 AI 전환이 시급한 상황에서, "
            "고객사의 현황 과제를 진단하고, "
            "데이원컴퍼니의 검증된 AX 교육 체계와 SkillMatch™ 솔루션으로 "
            "구성원 AI 역량을 내재화하여 지속 가능한 조직 혁신을 실현합니다."
        ),
        "slides": slides,
    }
