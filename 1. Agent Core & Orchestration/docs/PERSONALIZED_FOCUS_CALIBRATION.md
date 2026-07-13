# 난이도-인지 개인화 집중도 캘리브레이션 (설계·발표 기록)

작성 2026-07-13 · 대상: 발표(PPT) 근거 · 관련 역할: 1(오케스트레이션)·2(난이도)·3(백엔드)·4(온보딩/UI)

> **한 줄 요약**: 스키밍(대충 훑어 읽기) 감지 기준을 **고정 1.5**에서, **"이 사람이 · 이 난이도 글을 · 얼마나 빨리 넘기면 안 읽는 것인가"** 로 개인화했다. 온보딩 캘리브레이션 + 2번의 글 난이도를 결합하고, 읽을수록 자동으로 정교해진다(rolling).

---

## 1. 문제 (Before)

집중도(Focus Score)는 스크롤 속도가 임계값을 넘으면 "스키밍"으로 보고 감점한다. 그런데 임계값이:
- **모든 사용자·모든 글에 고정 1.5 px/ms** 였다. → 원래 빨리 읽는 사람은 억울하게 감점, 느린 사람은 스키밍을 놓침.
- 초기 개선(온보딩 easy/hard 평균 × 2.0)도 **easy·hard를 평균 내 난이도 신호를 버리고**, `×2.0`이 근거 없는 마법 상수였다.
- **확장(크롬) 경로는 baseline을 아예 안 썼다** — 항상 1.5.

핵심 통찰: 사람은 **어려운 글일수록 천천히** 읽는다. "빠른 스크롤 = 스키밍"의 기준은 **글 난이도와 개인 속도**에 함께 달려 있어야 한다. 그리고 우리는 이제 2번이 주는 **글 난이도(`difficulty_score`)** 를 갖고 있다.

---

## 2. 설계 (After)

### 2-1. 개인 "난이도별 편안한 읽기 속도" 직선
온보딩에서 **쉬운 지문**과 **어려운 지문**을 읽게 하고 각각의 편안한 스크롤 속도 `v_easy`, `v_hard`(px/ms)를 측정한다. 두 점 `(d_easy, v_easy)`, `(d_hard, v_hard)`이 그 사람의 속도-난이도 직선을 정의한다(보통 `v_easy > v_hard`).

### 2-2. 지금 글 난이도 D에서의 기준값
```
slope     = (v_hard − v_easy) / (d_hard − d_easy)          # 보통 음수
expected  = clamp(v_easy + slope·(D − d_easy), 0.1, ∞)     # 이 유저가 난이도 D에서 편안한 속도
threshold = max(FLOOR 0.4, expected × K 1.8)               # 스키밍으로 볼 경계
```
- **어려운 글**: expected↓ → threshold↓ → 스키밍을 **더 일찍** 잡음(천천히 읽어야 하니 공정).
- **쉬운 글**: threshold↑ → 원래 빨리 훑는 게 정상 → **과감점 방지**.

### 2-3. 신뢰도 블렌딩 (과적합 방지)
온보딩 2점만으론 불안정 → 인구집단 기본값과 가중 평균:
```
w = min(1.0, 0.5 + 0.1·n_sessions)      # 온보딩만(n=0) → 0.5, 5세션 → 1.0
threshold = w·(개인 threshold) + (1−w)·1.5
```
긴장한 첫 스크롤 한 번에 휘둘리지 않고, 데이터가 쌓일수록 개인값을 신뢰한다.

### 2-4. Rolling 학습 (읽을수록 정교)
세션 종료 시, 그 세션에서 **정상 읽기로 스크롤한 속도의 중앙값** `v_obs`(스키밍/정지 제외)를 관측치로 삼아, 글 난이도 D에 더 가까운 캘리브레이션 점을 EWMA로 당긴다:
```
if |D − d_easy| ≤ |D − d_hard|:  easy ← (1−α)·easy + α·v_obs
else:                            hard ← (1−α)·hard + α·v_obs        # α = 0.3
n_sessions += 1
```
→ 사용자가 읽을수록 개인 기준선이 실제 읽기 습관으로 수렴한다. `User.scroll_baseline`(DB)에 영속(기존은 세션 Redis라 증발).

---

## 3. 예시 (숫자로 체감)

| 사용자 | 글 난이도 | Before(고정) | After(개인화) |
|---|---|---|---|
| 느긋한 독자 (v_easy 0.5, v_hard 0.2) | 80(어려움) | 1.5 | **0.95** |
| 〃 | 20(쉬움) | 1.5 | **1.2** |
| 빠른 독자 (v_easy 1.2, v_hard 0.6, 5세션) | 80 | 1.5 | **0.98** |
| baseline 없음 | — | 1.5 | 1.5(폴백) |

**같은 사람인데 글 난이도에 따라 기준이 달라지고**(0.95 vs 1.2), **사람마다도 다르다.** 고정 1.5 하나로 뭉개던 걸 개인·맥락 2축으로 편 것.

---

## 4. 계약 & 구현 위치 (역할별)

**baseline 계약**: `{ easy, hard, d_easy(기본20), d_hard(기본75), n_sessions }`
프론트 전송: `baselineScrollSpeed = { easy, hard, dEasy, dHard }`

| 역할 | 구현 |
|---|---|
| **1·3 공통** | `cognitive_care(_service).py` `_personalized_scroll_threshold(baseline, difficulty_score)` + `calculate_focus_score(events, baseline, difficulty_score)` |
| **1(확장)** | `cognitive_care_client._cognitive_care_real`이 `state["scroll_baseline"]`·`difficulty_score` 전달. `/start`가 `baselineScrollSpeed` 수신→state 저장(`_normalize_scroll_baseline`). 디버그 모니터도 동일 임계값 |
| **2** | `difficulty_score`(글 난이도) 제공 — 이미 산출(재사용) |
| **3(백엔드)** | `User.scroll_baseline`(JSON) 영속. `/start` 유저 baseline 우선 로드·병합. `/events`가 textmeta 난이도 전달. `/result`에서 `_update_user_scroll_baseline`(EWMA rolling) |
| **4(온보딩)** | easy/hard 측정(기존) + `dEasy/dHard` 전송. 결과 화면에 "난이도별 읽기 속도 기준선" 안내 |

> ⚠️ 3번 런타임: `User`에 `scroll_baseline` 컬럼 추가 → **dev DB 재생성(또는 ALTER)** 필요.

---

## 5. 발표 세일즈 포인트
- **"고정 임계값 → 개인·맥락 2축 개인화"**: 온보딩 캘리브레이션이 실제 점수에 쓰인다(측정→개인화 폐루프).
- **"글이 어려울수록 더 촘촘히 본다"**: 2번 난이도와 결합 — 우리 멀티에이전트 시너지.
- **"읽을수록 정교해진다"(rolling)**: 쓸수록 좋아지는 개인화 스토리.
- **근거 있는 수식**: `×2` 마법값 대신 개인 속도선 × 여유계수 + 신뢰도 블렌딩.
