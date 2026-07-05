# AI 리터러시 케어 에이전트 — 2번 역할: Content & RAG Agent

> 2026 AI/SW 경진대회 출품작 | **2번 역할: 콘텐츠 처리 / RAG 기술리드**

## 역할 한 줄 정의

사용자의 인지 수준에 맞게 원문을 재구성하고, 환각 없는 신뢰 출처 기반 용어풀이와 동적 퀴즈를 제공하여 자기주도적 독해를 지원하는 콘텐츠 처리 엔진.

---

## 프로젝트 구조

```
ai-literacy-care-agent/
├── ARCHITECTURE_2.md          # 2번 역할 아키텍처 문서
├── DELIVERY_PLAN_2.md         # 2번 역할 개발 실행 계획
├── requirements.txt
├── .env.example               # 환경 변수 템플릿
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── content_reducer/
│       │   │   ├── __init__.py
│       │   │   ├── agent.py          # 에이전트 진입점
│       │   │   ├── contracts.py      # 입출력 타입 정의
│       │   │   ├── readability.py    # 한국어 가독성 분석
│       │   │   ├── chunker.py        # 의미 단위 청킹
│       │   │   ├── restructurer.py   # LLM 텍스트 재구성
│       │   │   ├── rag_engine.py     # RAG 용어풀이 엔진
│       │   │   ├── quiz_generator.py # 퀴즈 생성기
│       │   │   ├── router.py         # LLM 난이도 라우팅
│       │   │   ├── prompts.py        # 프롬프트 템플릿
│       │   │   └── fallbacks.py      # 서브모듈 실패 처리
│       │   └── stubs/
│       │       ├── __init__.py
│       │       └── content_reducer_stub.py  # E2E 더미 구현
│       └── tests/
│           ├── __init__.py
│           ├── test_readability.py
│           ├── test_chunker.py
│           ├── test_rag_engine.py
│           ├── test_quiz_generator.py
│           └── test_content_e2e.py
├── data/
│   └── term_dictionary.json   # 신뢰 출처 용어집 (RAG 데이터)
└── docs/
    ├── CONTENT_AGENT_CONTRACT.md
    ├── RAG_ARCHITECTURE.md
    ├── QUIZ_DESIGN.md
    └── READABILITY_FORMULA.md
```

---

## 빠른 시작

### 1. 환경 설정

```bash
# 가상 환경 생성 (권장)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
copy .env.example .env
# .env 파일을 열어 ANTHROPIC_API_KEY 입력
```

### 2. 데모 모드로 실행 (API 키 없이)

```bash
# .env에서 DEMO_MODE=true 설정
python -m backend.app.agents.content_reducer.agent
```

### 3. 실제 모드로 실행

```bash
# .env에서 ANTHROPIC_API_KEY 설정 후
python -m backend.app.agents.content_reducer.agent
```

---

## 테스트 실행

```bash
# 전체 테스트
python -m pytest backend/app/tests/ -v

# 단위 테스트만
python -m pytest backend/app/tests/test_readability.py -v
python -m pytest backend/app/tests/test_chunker.py -v

# E2E 테스트
python -m pytest backend/app/tests/test_content_e2e.py -v
```

---

## 핵심 설계 원칙

| 원칙 | 내용 |
|---|---|
| **Stub First** | 실제 LLM 없이 1번 Orchestrator E2E 흐름을 먼저 지원 |
| **RAG 범위 제한** | RAG는 용어풀이에만 적용. 요약/재구성에 미적용 |
| **환각 차단** | 모든 용어풀이는 신뢰 출처 데이터 기반 (faithfulness_score 포함) |
| **Fallback 보장** | 각 서브모듈 실패 시 기본값 반환으로 데모 유지 |
| **chunk_id 안정성** | 같은 문서는 항상 같은 chunk_id 생성 |

---

## 팀원 연결 계약 요약

### 1번 Orchestrator에서 받는 것
```json
{
  "session_id": "s_001",
  "raw_text": "원문 텍스트...",
  "user_literacy_level": 3,
  "profile": { "reading_level": "intermediate" }
}
```

### 1번 Orchestrator에 돌려주는 것
```json
{
  "session_id": "s_001",
  "difficulty_score": 68.5,
  "chunks": [{ "chunk_id": "chunk_doc001_01", "original_text": "...", "restructured_text": "..." }],
  "terms": [{ "term": "레이턴시", "definition": "...", "source": "..." }]
}
```

> 전체 계약 명세: [`docs/CONTENT_AGENT_CONTRACT.md`](docs/CONTENT_AGENT_CONTRACT.md)

---

## Milestone 현황

| Milestone | 날짜 | 상태 |
|---|---|---|
| M0 | 6/22 | ✅ Stub E2E 및 계약 초안 완료 |
| M1 | 6/29 | 🔄 핵심 파이프라인 구현 중 |
| M2 | 7/6  | ⏳ 퀴즈 생성 및 통합 |
| M3 | 7/10 | ⏳ 기능 동결 |
| M4 | 7/14 | ⏳ 제출본 점검 |
