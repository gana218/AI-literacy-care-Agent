import json, os

path = r'C:\Users\gana2\.gemini\antigravity\scratch\ai-literacy-care-backend\data\term_dictionary.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

d['terms'].insert(0, {
    'term': '정보',
    'aliases': [],
    'definition': '관찰이나 측정을 통하여 수집한 자료를 실제 문제에 도움이 될 수 있도록 정리한 지식.',
    'source': '표준국어대사전',
    'domain': '일반'
})
d['terms'].insert(0, {
    'term': '디지털',
    'aliases': ['Digital'],
    'definition': '데이터나 정보를 0과 1의 이진수로 변환하여 처리하고 저장하는 기술이나 방식.',
    'source': '표준국어대사전',
    'domain': 'IT'
})
d['terms'].insert(0, {
    'term': '리터러시',
    'aliases': ['문해력', 'Literacy'],
    'definition': '글을 읽고 이해하는 능력을 넘어, 정보를 비판적으로 분석하고 올바르게 활용할 수 있는 종합적 역량.',
    'source': '표준국어대사전',
    'domain': '일반'
})

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
