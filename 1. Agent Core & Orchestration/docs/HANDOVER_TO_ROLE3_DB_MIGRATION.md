# [1번→3번] 인수 메모: dev DB 재생성 필요 (스키마 컬럼 추가)

작성 2026-07-13 · 대상: 3번(Cognitive Care Backend) · 소요: 30초

## 한 줄
최신 main을 받은 뒤 **`POST /api/session/reset` 한 번만 호출**하면 됩니다. (테이블 drop+recreate → 새 컬럼 반영)

---

## 왜 필요한가
리터러시 v2·5대 지표·개인화 baseline 작업으로 **모델에 컬럼 3개가 추가**됐습니다.
SQLAlchemy `Base.metadata.create_all`은 **없는 테이블만 만들고, 기존 테이블에 컬럼을 ALTER하지 않습니다.**
→ 기존 DB 그대로면 아래 컬럼이 없어서 `/start`·`/result`·`/growth`에서 **에러 또는 값 누락**이 납니다.

| 테이블 | 새 컬럼 | 용도 |
|---|---|---|
| `users` | `scroll_baseline` (JSON) | 개인화 스크롤 baseline(rolling) |
| `reading_sessions` | `readability_score` (Float) | 2번 이독성 |
| `reading_sessions` | `literacy_domains` (JSON) | 문해 5대 지표(레이더) |

---

## 방법 (택1)

### ✅ 권장: reset 엔드포인트 (데이터 초기화 OK인 dev/데모)
이미 `endpoints.py`에 drop_all+create_all 하는 게 있습니다("스키마 변경 강제 적용" 주석). 서버 켠 상태에서:
```bash
curl -X POST http://localhost:8000/api/session/reset
# → {"status":"success", ...} 나오면 완료
```

### 대안 A: SQLite 폴백 쓰는 경우 (Postgres 없이 로컬)
DB 파일만 지우고 재시작하면 `create_all`이 새 스키마로 다시 만듭니다.
```bash
rm ./literacy_care.db   # backend 실행 디렉터리 기준
# 서버 재시작 → 자동 재생성
```

### 대안 B: 데이터 보존이 필요한 Postgres (ALTER)
```sql
ALTER TABLE users            ADD COLUMN IF NOT EXISTS scroll_baseline   JSONB;
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS readability_score DOUBLE PRECISION DEFAULT 50.0;
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS literacy_domains  JSONB;
```

---

## 확인
- 세션을 하나 끝까지(완독) 진행 → `/api/user/{userId}/growth` 호출 → **레이더 5축(이해도/집중 유지/정독 충실도/난이도 도전력/읽기 안정성)이 0이 아닌 값**으로 뜨면 OK.
- 온보딩 후 읽기 → 세션 반복 시 `users.scroll_baseline.n_sessions`가 증가하면 rolling 갱신 정상.

## 언제
**다음 데모/테스트 실행 전, 최신 main pull 직후 1회.** 그 뒤엔 불필요(같은 스키마 유지되는 한).

> 참고 문서: `docs/PERSONALIZED_FOCUS_CALIBRATION.md`(개인화), `docs/FEEDBACK_TO_ROLE3_QUIZ_GROWTH_REVIEW.md`(퀴즈/Growth).
막히면 바로 물어봐줘! 🙌
