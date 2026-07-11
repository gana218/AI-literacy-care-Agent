# Evaluation Metrics

현재 프로젝트는 생성 결과의 품질을 평가하기 위해
Faithfulness와 Answer Relevance 지표를 사용한다.

현재 구현은 RAGAS 또는 LLM Judge 기반 평가가 아니라,
단어 중첩(Token Overlap) 기반 Local Heuristic 평가를 사용한다.

따라서 점수는 절대적인 품질 점수라기보다,
Golden Dataset 내 상대 비교와 Regression(회귀) 감지를 위한 지표로 사용한다.

---

## Faithfulness

생성된 답변이 원문의 핵심 내용을 얼마나 잘 유지하는지를 평가한다.

### Range

0.0 ~ 1.0

### Pass

0.30 이상

### Evaluation Method

- 원문과 생성 결과의 핵심 단어 중첩 정도를 계산한다.
- 점수가 높을수록 원문의 내용을 더 잘 유지한 것으로 판단한다.

---

## Answer Relevance

생성된 답변이 질문과 얼마나 관련성이 있는지를 평가한다.

### Range

0.0 ~ 1.0

### Pass

0.30 이상

### Evaluation Method

- 질문과 답변 사이의 핵심 단어 중첩 정도를 계산한다.
- 점수가 높을수록 질문에 적절한 답변으로 판단한다.

---

## Overall Score

(Faithfulness + Answer Relevance) / 2

### Pass

0.30 이상

---

## Threshold Policy

현재 프로젝트의 통과 기준은 다음과 같다.

```
PASS_THRESHOLD = 0.30
```

이 기준은 현재 구현된 Local Heuristic 평가 방식에 맞춰 설정하였다.

향후 RAGAS 또는 LLM Judge 기반 평가로 교체될 경우,
실측 결과를 기반으로 Threshold를 재설정할 수 있다.

---

## Current Implementation

| Metric | Implementation | Status |
|---------|---------------|--------|
| Faithfulness | Local Heuristic (Token Overlap) | Implemented |
| Answer Relevance | Local Heuristic (Token Overlap) | Implemented |
| Overall Score | Average Score | Implemented |
| Pass / Fail | Threshold Comparison | Implemented |

---

## Limitations

현재 평가는 단어 중첩 기반 휴리스틱 방식으로 수행된다.

따라서 다음과 같은 한계가 존재한다.

- 의미는 같지만 표현이 다른 문장은 낮은 점수를 받을 수 있다.
- 문맥(Context)을 이해하지 못한다.
- 의미적 유사성(Semantic Similarity)은 평가하지 않는다.

향후에는 RAGAS 또는 LLM Judge 기반 평가를 적용하여
의미 기반(Faithfulness / Relevance) 평가로 확장할 예정이다.