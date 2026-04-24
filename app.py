import streamlit as st
from anthropic import Anthropic
import random
import os
import re

# =========================
# API 키 설정
# =========================
CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]
# 배포용 권장 방식
# CLAUDE_API_KEY = st.secrets.get("CLAUDE_API_KEY", os.getenv("CLAUDE_API_KEY"))


# =========================
# 업종별 도입부
# =========================
CATEGORY_PATTERNS = {
    "음식점/카페": {
        "예약/방문": [
            "예약하고 방문했는데",
            "주말이라 미리 예약하고 오길 잘했네요",
            "예약 시간 맞춰 갔더니 바로 안내받았어요",
            "미리 예약해두고 방문했는데"
        ],
        "추천/검색": [
            "지인 추천으로 왔는데",
            "평이 좋아서 궁금했는데",
            "리뷰 보고 골랐는데",
            "검색하다가 괜찮아 보여서 방문했어요"
        ],
        "가족/모임": [
            "가족들이랑 같이 왔는데",
            "부모님 모시고 방문했는데",
            "모임 장소로 골랐는데",
            "친구들이랑 식사하러 왔어요"
        ],
        "일상방문": [
            "근처 올 일 있어서 들렀는데",
            "퇴근하고 친구랑 들렀는데",
            "가볍게 밥 먹으러 들어왔는데",
            "오랜만에 외식하고 싶어서 방문했어요"
        ]
    },
    "뷰티/관리": {
        "예약/첫방문": [
            "네이버 예약으로 편하게 방문했어요",
            "처음 방문해봤는데",
            "리뷰 보고 골랐는데",
            "예약하고 시간 맞춰 방문했어요"
        ],
        "상담/친절": [
            "상담부터 친절하게 해주셔서",
            "처음이라 긴장했는데 편하게 안내해주셨어요",
            "하나하나 설명해주시는 점이 좋았어요",
            "방문 전부터 궁금한 게 많았는데"
        ],
        "관리만족": [
            "관리받는 내내 편안했어요",
            "꼼꼼하게 봐주시는 게 느껴졌어요",
            "위생적으로 관리되는 느낌이라 믿음이 갔어요",
            "생각보다 편하게 받고 왔어요"
        ],
        "재방문": [
            "항상 믿고 방문하는 곳인데",
            "다시 오고 싶다는 생각이 들었어요",
            "이번 방문도 만족스러웠어요",
            "주변에도 추천하고 싶은 곳이에요"
        ]
    },
    "요양/장례": {
        "상담/안내": [
            "상담부터 차분하게 안내해주셔서",
            "처음이라 걱정이 많았는데",
            "문의했을 때부터 친절하게 설명해주셨어요",
            "방문 전 걱정이 있었는데"
        ],
        "시설/신뢰": [
            "시설이 깔끔하게 관리되어 있어서",
            "전체적으로 차분한 분위기라",
            "직원분들이 세심하게 챙겨주셔서",
            "안내가 자세해서 믿음이 갔어요"
        ]
    },
    "휴대폰/전자기기": {
        "상담": [
            "상담받으러 방문했는데",
            "휴대폰 바꾸려고 알아보다가 방문했어요",
            "요금제 때문에 고민이 많았는데",
            "처음 상담받아봤는데"
        ],
        "구매/만족": [
            "설명을 자세히 해주셔서",
            "데이터 이동까지 도와주셔서",
            "가족 폰 바꿀 때도 다시 오고 싶어요",
            "생각보다 절차가 편해서 좋았어요"
        ]
    },

    "운동/PT/헬스": {
        "첫방문": [
            "처음 상담받으러 갔는데",
            "운동 시작하려고 알아보다가 방문했어요",
            "시설이 궁금해서 방문해봤는데",
            "운동을 다시 시작하려고 들렀어요"
        ],
        "수업/시설": [
            "기구가 잘 갖춰져 있어서",
            "트레이너님이 자세를 꼼꼼히 봐주셔서",
            "운동 분위기가 좋아서 꾸준히 다니기 좋겠어요",
            "시설이 깔끔해서 첫인상이 좋았어요"
        ]
    },

   "펜션/숙박": {
        "주변추천": [
            "지인이 추천해줬는데 ",
            "리뷰 보고 골랐는데",
            "후기가 좋은 이유가 있었네요",
            "아시는분이 강력추천해줬습니다."
        ],
        "검색": [
            "이곳저곳에 검색을 해보다가",
            "후기가 항상 좋았어서",
            "앞으로 단골 될 것 같아요",
            "이번에도 만족스럽게 이용했어요"
        ],
        "만족": [
            "간만에 진짜 기분 좋은 방문이었어요",
            "가격 대비 만족도가 좋았어요",
            "친절한 응대 덕분에 기분 좋게 이용했습니다",
            "전체적으로 편하게 이용하기 좋았어요"
        ]
    },


    "일반/범용": {
        "첫방문": [
            "처음 방문해봤는데",
            "리뷰 보고 골랐는데",
            "후기가 좋은 이유가 있었네요",
            "궁금해서 방문해봤는데"
        ],
        "재방문": [
            "오랜만에 재방문했는데",
            "항상 믿고 방문하는 곳인데",
            "앞으로 단골 될 것 같아요",
            "이번에도 만족스럽게 이용했어요"
        ],
        "만족": [
            "간만에 진짜 기분 좋은 방문이었어요",
            "가격 대비 만족도가 좋았어요",
            "친절한 응대 덕분에 기분 좋게 이용했습니다",
            "전체적으로 편하게 이용하기 좋았어요"
        ]
    }
}


# =========================
# 업종별 기본 작성 방향
# =========================
CATEGORY_RULES = {
    "음식점/카페": "음식 맛, 분위기, 친절함, 청결, 양, 가격 만족도, 재방문 의사, 모임/데이트/가족 외식 상황을 자연스럽게 섞어라. 고객 가이드에 없는 메뉴명은 임의로 만들지 마라.",
    "뷰티/관리": "상담, 위생, 친절함, 꼼꼼함, 시술/관리 만족도, 편안한 분위기, 재방문 의사를 자연스럽게 섞어라. 효과를 과장하지 말고 실제 만족감 위주로 작성하라.",
    "병원/요양/장례": "신뢰감, 친절한 상담, 시설 청결, 세심한 안내, 보호자 입장에서의 안심, 차분한 분위기를 중심으로 작성하라. 치료 효과나 결과를 확정적으로 말하지 마라.",
    "휴대폰/전자기기": "친절한 상담, 요금제 설명, 데이터 이동, 사은품, 가격 만족도, 가족 재방문 의사를 자연스럽게 반영하라. 무조건 최저가 같은 과장 표현은 피하라.",
    "운동/PT/헬스": "시설 청결, 기구 상태, 트레이너 상담, 운동 루틴, 맞춤 관리, 분위기, 재방문 의사를 섞어라. 몸 변화는 과장하지 말고 만족감 위주로 작성하라.",
    "일반/범용": "친절함, 청결, 분위기, 가격 만족도, 접근성, 재방문 의사를 업종에 맞게 자연스럽게 조합하라."
}


# =========================
# 말투
# =========================
PERSONA_PROMPTS = {
    "자연스러운 20대 여성": "~했어요, ~좋았어요, ㅎㅎ, 😊 등을 가끔 섞되 과하지 않게 작성.",
    "담백한 20~30대 남성": "짧고 담백하게, ~했네요, ~괜찮았습니다, ~만족합니다 식으로 작성.",
    "40~50대 차분한 말투": "차분하고 신뢰감 있게, ~했습니다, ~좋았습니다, ~만족스러웠습니다 위주로 작성.",
    "발랄한 후기": "밝고 가볍게, ㅎㅎ/ㅋㅋ/이모티콘을 일부만 자연스럽게 섞어 작성.",
    "간결하고 명확하게": "군더더기 없이 핵심 장점만 자연스럽게 작성."
}


# =========================
# 반복 방지
# =========================
BANNED_PHRASES = """
편하게 먹을 수 있었어요
기분 좋게 식사했네요
다음에 또 방문하고 싶어요
기대 이상이었어요
전체적으로 만족스러웠어요
다음에 또 방문할 것 같아요
친절하시고 깔끔해서 좋았어요
만족스럽게 이용했습니다
재방문 의사 있습니다
"""

WRITING_STYLES = [
    "방문 계기부터 자연스럽게 시작",
    "첫인상이나 분위기부터 시작",
    "직원 응대 느낌부터 시작",
    "이용하면서 좋았던 점부터 시작",
    "마지막 만족감부터 담백하게 마무리",
    "짧은 감탄 후 이유 설명",
    "친구에게 말하듯 자연스럽게 작성",
    "차분한 후기처럼 작성",
    "구체적인 상황 하나를 먼저 말하고 후기 작성",
    "장점 하나를 중심으로 자연스럽게 풀어쓰기",
    "불편할 줄 알았는데 괜찮았던 점 중심으로 작성",
    "가볍게 들렀다가 만족한 흐름으로 작성"
]


# =========================
# 결과 정리 함수
# =========================
def clean_reviews(text):
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        line = re.sub(r"^-+\s*", "", line)
        line = line.strip().strip('"').strip("'").strip()

        if line:
            cleaned.append(line)

    return cleaned


# =========================
# Streamlit 설정
# =========================
st.set_page_config(page_title="예약자원고생성", layout="centered")

if "generated_results" not in st.session_state:
    st.session_state.generated_results = []

st.markdown('<div class="main-title">✅ 네이버 예약자 리뷰 원고 생성기</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">자연스러운 예약자 리뷰 원고를 한 번에 생성합니다.</div>',
    unsafe_allow_html=True
)


# =========================
# UI
# =========================
col_cat1, col_cat2 = st.columns(2)

with col_cat1:
    category_group = st.selectbox("업종 대분류 선택", list(CATEGORY_PATTERNS.keys()))

with col_cat2:
    category = st.text_input("상세 업종", value="고기집")

situation = st.selectbox(
    "방문 상황 선택",
    list(CATEGORY_PATTERNS[category_group].keys())
)

count = st.number_input(
    "생성할 리뷰 수",
    min_value=1,
    max_value=200,
    value=10
)

col1, col2 = st.columns(2)

with col1:
    min_len = st.number_input("최소 글자수", value=100)

with col2:
    max_len = st.number_input("최대 글자수", value=200)

guide = st.text_area(
    "고객 가이드 / 업체 특장점",
    value="알바생이 고기 직접 구워줌, 직원 친절, 화장실 깔끔, 재방문 의사, 가족 방문 좋음"
)

must_include = st.text_input(
    "필수 포함 키워드",
    value=""
)

forbidden = st.text_input(
    "금지 키워드 / 금지 표현",
    value="과장된 표현, 없는 메뉴명, 없는 서비스, 무조건 최고"
)

selected_persona = st.selectbox(
    "말투 선택",
    list(PERSONA_PROMPTS.keys())
)

col_run, col_clear = st.columns(2)

run_btn = col_run.button("🚀 리뷰 생성 시작", use_container_width=True)
clear_btn = col_clear.button("🗑 결과 초기화", use_container_width=True)


# =========================
# 초기화
# =========================
if clear_btn:
    st.session_state.generated_results = []
    st.rerun()


# =========================
# 생성 로직 - API 1회 호출
# =========================
if run_btn:

    if not CLAUDE_API_KEY or CLAUDE_API_KEY == "여기에_CLAUDE_API_KEY_입력":
        st.error("CLAUDE_API_KEY를 입력해주세요.")

    elif not guide.strip():
        st.error("고객 가이드 또는 업체 장점을 입력해주세요.")

    elif min_len > max_len:
        st.error("최소 글자수가 최대 글자수보다 클 수 없습니다.")

    else:
        client = Anthropic(api_key=CLAUDE_API_KEY)
        target_count = int(count)

        status_text = st.empty()
        status_text.text(f"⏳ 리뷰 {target_count}개 생성 중...")

        try:
            selected_starts = random.choices(
                CATEGORY_PATTERNS[category_group][situation],
                k=target_count
            )

            selected_styles = random.choices(
                WRITING_STYLES,
                k=target_count
            )

            final_prompt = f"""
너는 실제 방문자가 작성한 것처럼 자연스러운 네이버 예약자 리뷰 원고를 작성한다.

[업종 대분류]
{category_group}

[상세 업종]
{category}

[방문 상황]
{situation}

[기본 업종별 작성 방향]
{CATEGORY_RULES.get(category_group, CATEGORY_RULES["일반/범용"])}

[고객 가이드]
{guide}

[필수 포함 키워드]
{must_include if must_include else "없음"}

[금지 키워드 / 금지 표현]
{forbidden if forbidden else "없음"}

[말투]
{PERSONA_PROMPTS[selected_persona]}

[도입부 후보 리스트]
{chr(10).join([f"- {s}" for s in selected_starts])}

[작성 방식 리스트]
{chr(10).join([f"- {s}" for s in selected_styles])}

[작성 요청]
리뷰를 총 {target_count}개 작성한다.

[작성 규칙]
1. 번호 없이 리뷰 문장만 작성한다.
2. 각 리뷰는 반드시 줄바꿈으로 구분한다.
3. 한 줄에 리뷰 1개만 작성한다.
4. 각 리뷰는 반드시 {min_len}자 이상 {max_len}자 이하로 작성한다.
5. 고객 가이드는 통째로 복붙하지 말고, 각 리뷰마다 일부 내용만 자연스럽게 반영한다.
6. 모든 리뷰에 같은 장점을 전부 넣지 않는다.
7. 리뷰마다 도입부, 문장 구조, 말투, 반영 요소를 다르게 한다.
8. 고객 가이드에 없는 메뉴명, 시술명, 장비명, 효과는 임의로 만들지 않는다.
9. 사진과 맞지 않는 음식명, 시술명, 서비스명은 억지로 넣지 않는다.
10. 광고 문구처럼 보이는 표현은 피하고 실제 방문 후기처럼 작성한다.
11. ㅎㅎ, ㅋㅋ, 이모티콘은 일부 리뷰에만 자연스럽게 사용한다.
12. 너무 완벽하게 정리된 문장보다 실제 사람이 쓴 것처럼 자연스럽게 작성한다.
13. 만족 표현 강도를 다양하게 사용한다. 예: 무난함, 괜찮음, 꽤 좋음, 만족, 다시 갈 듯
14. 문장 끝맺음을 매번 다르게 작성한다.
15. 리뷰 1개 안에서 같은 단어를 과하게 반복하지 않는다.

[반복 방지 규칙]
아래 표현은 그대로 사용하지 않는다.
{BANNED_PHRASES}

- “친절 + 청결 + 재방문” 순서로만 쓰지 않는다.
- 매번 같은 끝맺음으로 마무리하지 않는다.
- 장점 3개를 단순 나열하는 방식은 피한다.
- 같은 도입부라도 뒤 문장 전개는 다르게 작성한다.
- 전체 리뷰가 한 사람이 쓴 것처럼 보이지 않게 말투와 흐름을 섞는다.
"""

            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=12000,
                system="당신은 자연스러운 네이버 예약자 리뷰 원고를 작성하는 전문가입니다. 과장 없이 실제 방문 후기처럼 작성합니다.",
                messages=[
                    {
                        "role": "user",
                        "content": final_prompt
                    }
                ]
            )

            raw_text = message.content[0].text.strip()
            new_reviews = clean_reviews(raw_text)

            st.session_state.generated_results = new_reviews[:target_count]

            status_text.text("✅ 생성 완료")

            if len(st.session_state.generated_results) < target_count:
                st.warning(
                    f"요청한 {target_count}개 중 {len(st.session_state.generated_results)}개만 생성됐습니다. "
                    "리뷰 수를 줄이거나 max_tokens를 늘려보세요."
                )

        except Exception as e:
            st.error(f"오류: {str(e)}")


# =========================
# 결과 출력
# =========================
st.markdown("---")

if st.session_state.generated_results:
    excel_ready = "\n".join(st.session_state.generated_results)

    st.subheader("📋 엑셀 붙여넣기용")
    st.text_area(
        "아래 내용을 전체 복사해서 시트에 붙여넣으세요.",
        value=excel_ready,
        height=320
    )

    st.subheader("📝 생성된 리뷰 미리보기")

    for idx, text in enumerate(st.session_state.generated_results):
        st.markdown(
            f"""
            <div class="result-box">
                <b>{idx + 1}.</b> {text}
            </div>
            """,
            unsafe_allow_html=True
        )
