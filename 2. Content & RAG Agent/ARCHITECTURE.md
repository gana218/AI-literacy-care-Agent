# ARCHITECTURE.md (Role 2: Content & RAG Agent)

[cite_start]본 문서는 **2026 AI SW중심대학 디지털 경진대회**에 출품하는 *AI 리터러시 케어 에이전트* 시스템 내 **2번 역할(Content & RAG Agent)**의 아키텍처 및 상세 메커니즘을 정의합니다[cite: 240, 241, 461]. 

[cite_start]2번 역할은 원본 텍스트를 사용자의 가독성 수준에 맞춰 재구성하고, RAG(검색 증강 생성) 기반의 신뢰성 높은 용어 풀이를 제공하며, 문맥 맞춤형 인터랙티브 퀴즈를 생성하여 사용자의 스스로 읽기와 이해를 돕는 핵심 엔진입니다[cite: 296, 392, 395, 397].

---

## 1. 에이전트 개요 & 책임 (System Boundary)

[cite_start]2번 역할은 `Content Reducer Agent`를 메인으로 하며, 완독 및 이해도 측정을 위한 `Reward Agent`용 메시지 생성 일부를 분담합니다[cite: 391, 405, 461].

### 1.1 주요 책무 (Responsibilities)
1. [cite_start]**가독성 분석 및 텍스트 재구성 (Readability & Restructure):** 원문의 가독성 지수를 측정하고 의미 단위 분할(Semantic Chunking) 및 쉬운 문장 변환을 수행합니다[cite: 392, 394].
2. [cite_start]**환각 없는 용어 풀이 (RAG Grounding):** 전문 용어나 어려운 어휘를 신뢰할 수 있는 외부 출처 데이터베이스 기반으로 풀이하여 환각(Hallucination)을 원천 차단합니다[cite: 424, 426].
3. [cite_start]**인지적 재집중 유도 (Interactive Quiz):** `Cognitive Care Agent`(3번)의 인터랙션 트리거를 받아 해당 문맥에 완벽히 부합하는 퀴즈를 동적으로 생성합니다[cite: 397, 404].

### 1.2 서브 모듈 구성
* [cite_start]**`Readability Analyzer`**: 한국어 가독성 지수(Flesch-Kincaid 유사 알고리즘) 기반 난이도 산출[cite: 340, 394].
* [cite_start]**`Semantic Chunker`**: `LangChain SemanticChunker` 기반 의미론적 문단 분할 수행[cite: 394, 428].
* [cite_start]**`RAG Grounding Engine`**: 용어풀이 한정 벡터 DB 조회 및 `Faithfulness` 보증 생성[cite: 287, 425].
* [cite_start]**`Contextual Quiz Generator`**: LLM 기반 문맥 맞춤형 퀴즈 선별 및 템플릿화[cite: 397, 400].

---

## 2. 기술 스택 (Tech Stack)

[cite_start]기획서에 확정된 하이브리드 LLM 라우팅 전략 및 공유 인프라를 준수합니다[cite: 428, 429].

| 계층 (Layer) | 오픈소스 및 프레임워크 / 서비스 | 비고 |
| :--- | :--- | :--- |
| **LLM Runtime** | Claude 3.5 Sonnet / Opus (High-end)<br>경량 모델 (Light-weight) | [cite_start]고난도 추론 및 재구성은 Claude 1순위 사용<br>단순 청킹 및 변환은 경량 모델 라우팅 [cite: 430] |
| **Framework** | LangChain (`SemanticChunker`) | [cite_start]의미론적 청킹 파이프라인 구축 [cite: 394, 428] |
| **Vector DB** | PostgreSQL (pgvector) 또는 전용 Vector DB | [cite_start]용어집 및 사전 데이터 저장 및 유사도 검색 [cite: 421, 428] |
| **Evaluation** | Ragas (`Faithfulness`, `Answer Relevance`) | [cite_start]텍스트 품질 및 RAG 신뢰성 정량 평가 [cite: 287, 433] |

---

## 3. 핵심 데이터 흐름 및 파이프라인

### 3.1 텍스트 재구성 파이프라인 (Text Restructuring Process)
[cite_start]사용자가 웹 페이지나 문서(뉴스, 논문 등)의 읽기를 시작하면, `Main Orchestrator`로부터 원문(Raw Text)이 유입됩니다[cite: 354, 355, 388, 396].


```

[원문 수신]
│
▼
[Readability Analyzer] ───> 한국어 가독성 지수 분석 및 기본 난이도 스코어링 
│
▼
[Semantic Chunker] ──────> 의미론적 경계선 파악 및 청크(Chunk) 단위 분할 
│
▼
[LLM Restructuring] ─────> 사용자 프로필 수준에 맞춘 쉬운 문장 변환 (Claude) 
│
▼
[RAG Injection] ─────────> 고난도 전문 용어 매핑 및 툴팁용 풀이 데이터 결합 
│
▼
[Orchestrator 반환] ─────> Shared State 업데이트 및 프론트엔드 전달 

```

### 3.2 RAG 기반 용어풀이 아키텍처 (Strict RAG Flow)
[cite_start]시스템의 신뢰성을 확보하기 위해 RAG는 **오직 용어풀이 및 쉬운 설명 한 곳에만 제한적으로 적용**합니다[cite: 287, 424, 425].

* [cite_start]**Grounding Sources:** 표준국어대사전, 도메인 전문 용어집, 검증된 위키 데이터[cite: 426].
* **프로세스:**
  1. [cite_start]재구성 중 변환이 필요한 타깃 용어 추출[cite: 396].
  2. [cite_start]Vector DB에서 해당 용어의 신뢰 출처 컨텍스트(Context) 검색[cite: 421, 426].
  3. [cite_start]LLM Prompt에 검색된 사전식 정의만을 컨텍스트로 바인딩하여 툴팁 텍스트 생성[cite: 395, 436].
  4. [cite_start]QA Agent(5번 역할)가 해당 추출물의 `Faithfulness`를 실시간/배치 평가하여 지어낸 답변이 없는지 검증[cite: 287, 415, 426].

---

## 4. 인터페이스 및 API 계약 (Interface & Payload)

[cite_start]`Main Orchestrator` 및 타 서브 에이전트와 주고받는 데이터 스키마 규칙입니다[cite: 352, 388].

### 4.1 Content Reducer Request (From Orchestrator)
```json
{
  "session_id": "usr_ssn_2026_01",
  "raw_text": "인공지능의 LLM 레이턴시 최적화 기법 중 하나인 하이브리드 라우팅은...",
  "user_literacy_level": 2, 
  "target_domain": "IT/Software"
}

```

### 4.2 Content Reducer Response (To Orchestrator)

```json
{
  "session_id": "usr_ssn_2026_01",
  "readability_score": 68.5,
  "chunks": [
    {
      "chunk_id": 1,
      "original_chunk": "인공지능의 LLM 레이턴시 최적화 기법 중 하나인 하이브리드 라우팅은...",
      "restructured_chunk": "AI 모델이 답변하는 속도를 빠르게 만들기 위해, 가벼운 작업과 어려운 작업을 나누어 처리하는 '하이브리드 라우팅' 방식은...",
      "terms": [
        {
          "term": "레이턴시",
          "definition": "시스템이 요청을 받은 후 응답을 보낼 때까지 걸리는 대기 시간 또는 지연 시간.",
          "source": "도메인 용어집 IT 편"
        }
      ]
    }
  ]
}

```

### 4.3 Contextual Quiz Generation Payload (For Cognitive Care Nudge)

```json
{
  "chunk_id": 1,
  "context": "AI 모델이 답변하는 속도를 빠르게 만들기 위해, 가벼운 작업과 어려운 작업을 나누어 처리하는 '하이브리드 라우팅' 방식은...",
  "quiz": {
    "question": "하이브리드 라우팅 방식의 주요 목적은 무엇인가요?",
    "options": ["1. 생성 비용 절감", "2. 답변 속도(레이턴시) 최적화", "3. 보안 강화", "4. 데이터 수집"],
    "correct_option": 2,
    "explanation": "문맥에서 하이브리드 라우팅은 AI 모델이 답변하는 속도(레이턴시)를 빠르게 만들기 위한 최적화 기법으로 설명되어 있습니다."
  }
}

```

---

## 5. 품질 보증 및 방어 전략 (QA & Defense)

* 
**환각 방지 및 평가 (Faithfulness Metric):** 본 에이전트가 생성한 용어 정의 및 문장 요약은 전적으로 제공된 데이터 원본과 사전 데이터에 기반합니다. 이는 개발 파이프라인 빌드 시 `Ragas`의 `Faithfulness` 지표를 활용해 정량 증명됩니다.


* 
**가독성 지표의 객관성:** 한국어 환경에 특화된 Flesch-Kincaid 유사 가독성 알고리즘을 코드로 내재화하여, 심사위원이 제기할 수 있는 "문해력 향상 측정 점수의 신뢰성" 질문에 대한 객관적 보정 데이터(Normalization)를 제공합니다.
