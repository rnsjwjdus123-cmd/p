import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = "c:/Users/user/Desktop/santokki/quiz/index.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. 태그 안의 깨진 이모티콘(주로 옵션 앞) 제거
# 예: <span class="option-letter">A</span>? Living room -> <span class="option-letter">A</span>Living room
# 우리는 </span> 뒤에 있는 옵션 텍스트 시작 전에 있는 불필요한 이모티콘 기호를 날린다.
# </span> 과 실제 영어/알파벳 사이의 기호 제거
html = re.sub(r'(<span class="option-letter">[^<]+</span>)\s*[^a-zA-Z0-9<]+(?=[A-Za-z0-9])', r'\1', html)

# 2. 결과 페이지 한국어 이름 제거 (CSS로 숨김 처리)
# <div class="result-title-en korean-text" id="resultTitleKo" style="font-style: italic;">--</div>
html = html.replace(
    'id="resultTitleKo" style="font-style: italic;"',
    'id="resultTitleKo" style="display: none;"'
)

# 3. 자바스크립트에서 한국어 이름 주입하는 곳 제거 (선택사항, 위에서 display none 했으니 안전)
# document.getElementById('resultTitleKo').textContent = product.name;

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print("index.html UI 수정 완료")
