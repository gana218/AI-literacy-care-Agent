import urllib.request, urllib.parse
key = 'E42588361C0380D7C034556712EA92CA'
word = '정보'
url = f'https://stdict.korean.go.kr/api/search.do?key={key}&q={urllib.parse.quote(word)}&req_type=json&start=1&num=5'
resp = urllib.request.urlopen(url).read().decode('utf-8')
print("RAW RESP:", resp)
