# AI 리터러시 케어 에이전트 — 오케스트레이터 코어

2026 AI·SW중심대학 디지털 경진대회 SW부문 · 팀 AllDayHappyDay
**1번 역할(에이전트 코어 / 오케스트레이션, 이소희)** 작업 저장소.

> "GPT는 텍스트를 처리하고, 우리는 사람을 관리한다." — 읽기 행동과 이해도를
> 측정·개입·추적하는 폐루프 멀티 에이전트 시스템.

## 폴더 구조

```
ai-literacy-care-agent/
├─ ARCHITECTURE.md          # 1번 역할 아키텍처 (무엇을/어떤 구조로)
├─ DELIVERY_PLAN.md         # 구현 순서·완료 기준 (언제/어디까지)
├─ requirements.txt
├─ backend/app/
│  ├─ main.py               # FastAPI 진입점 (골격)
│  ├─ api/
│  │  └─ reading_session.py # 프론트 ↔ 오케스트레이터 API 계층
│  ├─ orchestrator/         # ★ 1번 역할 핵심
│  │  ├─ state.py           #   Shared State 스키마 (SSOT)
│  │  ├─ graph.py           #   에이전트 실행 흐름
│  │  ├─ routing.py         #   집중도 기반 개입 라우팅
│  │  ├─ score.py           #   Literacy Score 계산 (순수 함수)
│  │  ├─ contracts.py       #   팀원 입출력 계약 검증
│  │  └─ errors.py          #   에이전트 실패 fallback
│  ├─ agents/stubs/         # 더미 에이전트 (실제 모듈 나오기 전)
│  └─ tests/                # score / routing / state / flow 단위 테스트
└─ docs/
   ├─ API_CONTRACT.md       # ★ 팀원용 입출력 JSON 계약
   ├─ SHARED_STATE.md
   ├─ SCORE_FORMULA.md
   └─ INTEGRATION_CHECKLIST.md
```

## 팀원이 봐야 할 곳

| 역할 | 먼저 볼 파일 |
|---|---|
| 2번 콘텐츠/RAG | `docs/API_CONTRACT.md` §1, `state.py`의 chunks/terms 필드 |
| 3번 백엔드/실시간 | `docs/API_CONTRACT.md` §2·§7, `state.py`의 reading_events |
| 4번 프론트 | `docs/API_CONTRACT.md` §6 (최종 응답·intervention) |
| 5번 QA | `docs/API_CONTRACT.md` §5, `state.py`의 trace |

## 개발

```bash
# 테스트 (프로젝트 루트 = ai-literacy-care-agent 의 상위에서)
python -m pytest ai-literacy-care-agent/backend/app/tests

# 서버 (6/22 이후)
uvicorn backend.app.main:app --reload
```

## 진행 상태 (M0 기준)

- [x] 폴더·패키지 골격 (6/20)
- [x] `ReadingSessionState` 타입 정의 (6/20~21)
- [x] `docs/API_CONTRACT.md` 초안 (6/20)
- [x] stub 에이전트 + orchestrator E2E (6/22, M0)
- [x] 개입 라우팅 (6/24)
- [x] quiz_result 정규화 및 score 반영 (6/25)
- [x] Score v1 (6/26)
- [x] M1 데모 입력 데이터 및 smoke test 고정 (6/27)
- [x] 서브 에이전트 adapter layer 준비 (6/28)
- [ ] M1 핵심 폐루프 데모 (6/29)
