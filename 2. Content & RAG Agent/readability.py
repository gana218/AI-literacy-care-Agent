import re

def analyze_korean_features(text: str) -> dict:
    """
    한국어 텍스트의 언어학적 피로도 및 인지 부하 요소를 정밀 추출합니다.
    """
    # 1. 고난도 한자어 꼬리 및 전문 어미 패턴 (함, 음, 이며, 에 따른, 메커니즘 등)
    # 문장 끝이나 중간에 명사형 종결이 많을수록 가독성이 떨어짐
    nominal_endings = len(re.findall(r'([함음됨임]│[역적성화]인│에\s+따른│통한│의한)', text))
    
    # 2. 복합 조사 및 난해한 격조사 결합 패턴 (~에의, ~로의, ~에세의, ~으로써)
    complex_josa = len(re.findall(r'([의로에]의│으로써│로써│에게로)', text))
    
    # 3. 문장 내 쉼표(,) 및 연결어미를 통한 문장 확장성 계측 (문장이 복문으로 꼬이는지 확인)
    clause_connectors = len(re.findall(r'([며고나니아서어서가]\s│,\s)', text))
    
    # 4. 외래어 및 전문 영문 약어 패턴 (LLM, RAG, 인프라 등)
    technical_words = len(re.findall(r'([a-zA-Z]{2,}[0-9]*│[라즘트릭팅션]은│[라즘트릭팅션]의)', text))

    return {
        "nominal_endings_count": nominal_endings,
        "complex_josa_count": complex_josa,
        "clause_connectors_count": clause_connectors,
        "technical_words_count": technical_words
    }

def calculate_readability_score(text: str) -> float:
    """
    한국어 정보 밀도 및 인지 부하 가중치를 결합한 Flesch-Kincaid 확장 보정 수식
    - 점수 범위: 0.0 ~ 100.0
    - 낮을수록 텍스트 구조가 복잡하고 다층적인 논리 구조를 가짐 (논문, 전문 기사)
    - 높을수록 단문 위주이며 직관적인 일상 어휘 중심 (아동서, 쉬운 안내문)
    """
    if not text or not text.strip():
        return 100.0

    # Base 카운팅 정제
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
    sentence_count = len(sentences) if len(sentences) > 0 else 1
    
    words = text.split()
    word_count = len(words) if len(words) > 0 else 1
    
    clean_text = re.sub(r'[^가-힣a-zA-Z0-9]', '', text)
    syllable_count = len(clean_text) if len(clean_text) > 0 else 1

    # 기초 지표 산출
    asl = word_count / sentence_count   # 문장당 평균 단어 수
    asw = syllable_count / word_count  # 단어당 평균 음절 수

    # 언어학적 고난도 가중치 분석 추출
    features = analyze_korean_features(text)
    
    # 청크(텍스트) 크기 대비 고난도 패턴 밀도 계산
    density_factor = (
        (features["nominal_endings_count"] * 1.5) +
        (features["complex_josa_count"] * 2.0) +
        (features["clause_connectors_count"] * 1.2) +
        (features["technical_words_count"] * 1.8)
    ) / sentence_count

    # 고도화된 한국어 전용 가독성 보정 수식 (K-Readability Index)
    # 기본 음절/문장 길이에 '추상성 및 인지 부하 밀도(density_factor)'를 패널티로 차감
    base_score = 220.0 - (1.5 * asl) - (62.0 * asw)
    final_score = base_score - (density_factor * 3.5)

    # 0~100 스케일 가드레일 및 소수점 첫째자리 정제
    return round(max(0.0, min(100.0, final_score)), 1)

def get_literacy_level(score: float) -> int:
    """
    산출된 가독성 점수를 기반으로 5단계 리터러시 타겟 레벨 매핑
    """
    if score >= 82.0: return 5    # 초등 저학년 수준 (매우 쉬움)
    elif score >= 67.0: return 4  # 초등 고학년 ~ 중등 수준 (쉬움)
    elif score >= 52.0: return 3  # 고등 교과서 및 일반 대중 매체 (보통)
    elif score >= 35.0: return 2  # 대학 교재 및 시사 잡지 (어려움)
    else: return 1                # 전문 학술지, 특허, 고난도 기술 논문 (매우 어려움)


# ==========================================
# 프로덕션 레벨 수식 검증 모듈
# ==========================================
if __name__ == "__main__":
    print("==================================================")
    print("  Role 2: 정밀 한국어 인지부하 가독성 엔진 검증  ")
    print("==================================================\n")

    # 대조군 1: 극단적 고난도 비즈니스/IT 전문 콘텍스트
    text_level_1 = (
        "대규모 생성형 언어 모델의 추론 레이턴시 제어를 위한 하이브리드 라우팅 기법은, "
        "컨텍스트의 구조적 복잡도를 동적으로 계량화함으로써 하드웨어 인프라의 처리량을 극대화한다. "
        "이는 정교하게 설계된 분류 알고리즘에 의존하며, 연산 비용 절감과 자원 최적화의 동시 달성을 목적으로 한다."
    )

    # 대조군 2: 중간 수준의 설명문
    text_level_3 = (
        "인공지능 모델이 대답하는 시간을 줄이기 위해 하이브리드 라우팅이라는 기술을 사용합니다. "
        "이 기술은 사용자의 질문이 얼마나 어려운지 미리 파악한 뒤, 알맞은 컴퓨터에 나누어 보내는 방식으로 작동합니다. "
        "이를 통해 비용을 아끼고 시스템 운영 효율을 크게 높일 수 있습니다."
    )

    # 대조군 3: 극단적으로 정제된 아동/초급자용 텍스트
    text_level_5 = (
        "컴퓨터가 질문에 대답하는 속도를 더 빠르게 만들 수 있어요. 바로 두 가지 길로 나누어 보내는 방법입니다. "
        "쉬운 문제는 가벼운 컴퓨터가 풀고, 어려운 문제는 똑똑한 컴퓨터가 풀게 조절합니다. "
        "이렇게 하면 기다리는 시간이 줄어들어서 아주 편리합니다."
    )

    # 스코어링 및 로그 출력
    for i, t in enumerate([text_level_1, text_level_3, text_level_5], start=1):
        score = calculate_readability_score(t)
        level = get_literacy_level(score)
        features = analyze_korean_features(t)
        
        print(f"[테스트 케이스 {i}]")
        print(f"- 가독성 점수 : {score} / 100")
        print(f"- 타겟 레벨   : Level {level}")
        print(f"- 인지 부하 요소 데이터: {features}")
        print("-" * 50)
