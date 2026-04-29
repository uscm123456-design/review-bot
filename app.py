import streamlit as st
from anthropic import Anthropic
import random
import re
import streamlit.components.v1 as components
import json

CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]

CATEGORY_PATTERNS = {
    "음식점/카페": {
        "예약/방문": ["예약하고 방문했는데", "주말이라 미리 예약하고 오길 잘했네요", "예약 시간 맞춰 갔더니 바로 안내받았어요", "미리 예약해두고 방문했는데"],
        "추천/검색": ["지인 추천으로 왔는데", "평이 좋아서 궁금했는데", "리뷰 보고 골랐는데", "검색하다가 괜찮아 보여서 방문했어요"],
        "가족/모임": ["가족들이랑 같이 왔는데", "부모님 모시고 방문했는데", "모임 장소로 골랐는데", "친구들이랑 식사하러 왔어요"],
        "일상방문": ["근처 올 일 있어서 들렀는데", "퇴근하고 친구랑 들렀는데", "가볍게 밥 먹으러 들어왔는데", "오랜만에 외식하고 싶어서 방문했어요"]
    },
    "뷰티/관리": {
        "예약/첫방문": ["네이버 예약으로 편하게 방문했어요", "처음 방문해봤는데", "리뷰 보고 골랐는데", "예약하고 시간 맞춰 방문했어요"],
        "상담/친절": ["상담부터 친절하게 해주셔서", "처음이라 긴장했는데 편하게 안내해주셨어요", "하나하나 설명해주시는 점이 좋았어요", "방문 전부터 궁금한 게 많았는데"],
        "관리만족": ["관리받는 내내 편안했어요", "꼼꼼하게 봐주시는 게 느껴졌어요", "위생적으로 관리되는 느낌이라 믿음이 갔어요", "생각보다 편하게 받고 왔어요"],
        "재방문": ["항상 믿고 방문하는 곳인데", "다시 오고 싶다는 생각이 들었어요", "이번 방문도 만족스러웠어요", "주변에도 추천하고 싶은 곳이에요"]
    },
    "요양/장례": {
        "상담/안내": ["상담부터 차분하게 안내해주셔서", "처음이라 걱정이 많았는데", "문의했을 때부터 친절하게 설명해주셨어요", "방문 전 걱정이 있었는데"],
        "시설/신뢰": ["시설이 깔끔하게 관리되어 있어서", "전체적으로 차분한 분위기라", "직원분들이 세심하게 챙겨주셔서", "안내가 자세해서 믿음이 갔어요"]
    },
    "휴대폰/전자기기": {
        "상담": ["상담받으러 방문했는데", "휴대폰 바꾸려고 알아보다가 방문했어요", "요금제 때문에 고민이 많았는데", "처음 상담받아봤는데"],
        "구매/만족": ["설명을 자세히 해주셔서", "데이터 이동까지 도와주셔서", "가족 폰 바꿀 때도 다시 오고 싶어요", "생각보다 절차가 편해서 좋았어요"]
    },
    "운동/PT/헬스": {
        "첫방문": ["처음 상담받으러 갔는데", "운동 시작하려고 알아보다가 방문했어요", "시설이 궁금해서 방문해봤는데", "운동을 다시 시작하려고 들렀어요"],
        "수업/시설": ["기구가 잘 갖춰져 있어서", "트레이너님이 자세를 꼼꼼히 봐주셔서", "운동 분위기가 좋아서 꾸준히 다니기 좋겠어요", "시설이 깔끔해서 첫인상이 좋았어요"]
    },
    "펜션/숙박": {
        "주변추천": ["지인이 추천해줬는데", "리뷰 보고 골랐는데", "후기가 좋은 이유가 있었네요", "아시는 분이 추천해줘서 방문했어요"],
        "검색": ["이곳저곳 검색해보다가", "후기가 좋아서 궁금했는데", "숙소 찾다가 괜찮아 보여서 예약했어요", "여행 준비하면서 알아보다가 선택했어요"],
        "만족": ["간만에 기분 좋은 숙박이었어요", "가격 대비 만족도가 좋았어요", "친절한 응대 덕분에 편하게 쉬다 왔습니다", "전체적으로 쉬기 좋은 분위기였어요"]
    },
    "일반/범용": {
        "첫방문": ["처음 방문해봤는데", "리뷰 보고 골랐는데", "후기가 좋은 이유가 있었네요", "궁금해서 방문해봤는데"],
        "재방문": ["오랜만에 재방문했는데", "항상 믿고 방문하는 곳인데", "앞으로 단골 될 것 같아요", "이번에도 만족스럽게 이용했어요"],
        "만족": ["간만에 진짜 기분 좋은 방문이었어요", "가격 대비 만족도가 좋았어요", "친절한 응대 덕분에 기분 좋게 이용했습니다", "전체적으로 편하게 이용하기 좋았어요"]
    },
    "미용실": {
        "예약/첫방문": ["네이버 예약하고 방문했는데", "처음 가보는 미용실이라 살짝 걱정했는데", "리뷰 보고 예약했는데", "머리 고민하다가 방문했어요"],
        "상담/시술": ["상담부터 꼼꼼하게 해주셔서", "원하는 스타일을 설명드렸더니", "머리 상태를 먼저 봐주셔서", "시술 전에 자세히 설명해주셨어요"],
        "만족/재방문": ["결과가 생각보다 자연스러워서", "머리 손질이 편해져서", "분위기도 편하고 결과도 좋아서", "다음에도 여기로 올 것 같아요"],
        "손상/관리": ["머릿결 손상이 걱정됐는데", "손상 덜 가게 신경 써주셔서", "관리 방법까지 알려주셔서", "시술 후에도 머리가 차분해서 좋았어요"]
    },

    "점집": {
        "상담/첫방문": ["처음 방문이라 긴장했는데", "지인 추천으로 상담받아봤는데", "요즘 고민이 많아서 찾아갔는데", "후기 보고 예약했는데"],
        "고민상담": ["말 못 했던 고민까지 차분히 들어주셔서", "현재 상황을 잘 짚어주셔서", "답답했던 부분이 조금 정리됐어요", "이야기 나누는 동안 마음이 편해졌어요"],
        "분위기/신뢰": ["분위기가 부담스럽지 않아서", "편하게 말할 수 있게 해주셔서", "억지로 겁주는 느낌이 아니라 좋았어요", "차분하게 설명해주셔서 믿음이 갔어요"],
        "재상담": ["다음에 또 고민 생기면 오고 싶어요", "상담받고 나니 마음이 한결 가벼웠어요", "생각 정리하는 데 도움이 됐어요", "주변에도 조심스럽게 추천하고 싶네요"]
    },

    "고기집": {
        "예약/방문": ["예약하고 방문했는데", "주말이라 미리 예약하고 갔는데", "가족들이랑 고기 먹으러 갔는데", "퇴근하고 고기 생각나서 들렀어요"],
        "맛/구성": ["고기 질이 좋아서 첫입부터 만족했어요", "반찬 구성이 깔끔해서 좋았어요", "고기랑 곁들여 먹기 좋은 구성이었어요", "양도 괜찮고 맛도 만족스러웠어요"],
        "직원/서비스": ["직원분들이 친절하게 응대해주셔서", "고기 굽는 타이밍을 잘 봐주셔서", "바쁜 시간대인데도 응대가 좋았어요", "설명도 친절하게 해주셔서 편했어요"],
        "모임/외식": ["가족 외식 장소로 괜찮았어요", "친구들이랑 오기 좋은 분위기였어요", "회식 장소로도 무난해 보였어요", "부모님 모시고 와도 좋을 것 같아요"]
    },

    "왁싱/제모": {
        "예약/첫방문": ["처음 왁싱 받아보는 거라 긴장했는데", "예약하고 시간 맞춰 방문했어요", "리뷰 보고 조심스럽게 예약했는데", "제모 관리 알아보다가 방문했어요"],
        "상담/안내": ["상담부터 자세히 해주셔서", "관리 전 설명을 꼼꼼히 해주셔서", "처음이라 모르는 게 많았는데", "주의사항까지 친절하게 알려주셨어요"],
        "위생/분위기": ["공간이 깔끔하게 관리되어 있어서", "위생적으로 진행되는 느낌이라", "프라이빗한 분위기라 부담이 덜했어요", "편하게 받을 수 있게 배려해주셨어요"],
        "관리만족": ["생각보다 편하게 받고 왔어요", "꼼꼼하게 관리해주셔서 만족했어요", "민망할까 걱정했는데 편안했어요", "다음 관리도 여기서 받을 생각이에요"]
    },

    "출장업종": {
        "예약/문의": ["문의드렸을 때부터 친절하게 안내해주셔서", "급하게 필요해서 연락드렸는데", "예약 시간 맞춰 방문해주셔서", "상담부터 설명이 자세해서 좋았어요"],
        "방문/편리함": ["직접 방문해주시니 정말 편했어요", "따로 나가지 않아도 돼서 좋았어요", "시간 맞춰 와주셔서 편하게 이용했어요", "집에서 바로 해결할 수 있어서 만족했어요"],
        "작업/꼼꼼함": ["작업을 꼼꼼하게 해주시는 게 느껴졌어요", "전후 설명을 잘해주셔서 믿음이 갔어요", "필요한 부분만 정확히 봐주셔서 좋았어요", "마무리까지 깔끔하게 해주셨어요"],
        "청소/설비": ["청소 후 확실히 깔끔해진 게 보였어요", "설비 문제도 차분하게 점검해주셨어요", "작업 과정이 전문적으로 느껴졌어요", "관리 방법까지 알려주셔서 도움이 됐어요"]
    }
}

    

CATEGORY_RULES = {
    "음식점/카페": "음식 맛, 분위기, 친절함, 청결, 양, 가격 만족도, 재방문 의사, 모임/데이트/가족 외식 상황을 자연스럽게 섞어라. 고객 가이드에 없는 메뉴명은 임의로 만들지 마라.",
    "뷰티/관리": "상담, 위생, 친절함, 꼼꼼함, 시술/관리 만족도, 편안한 분위기, 재방문 의사를 자연스럽게 섞어라. 효과를 과장하지 말고 실제 만족감 위주로 작성하라.",
    "요양/장례": "신뢰감, 친절한 상담, 시설 청결, 세심한 안내, 보호자 입장에서의 안심, 차분한 분위기를 중심으로 작성하라. 치료 효과나 결과를 확정적으로 말하지 마라.",
    "휴대폰/전자기기": "친절한 상담, 요금제 설명, 데이터 이동, 사은품, 가격 만족도, 가족 재방문 의사를 자연스럽게 반영하라. 무조건 최저가 같은 과장 표현은 피하라.",
    "운동/PT/헬스": "시설 청결, 기구 상태, 트레이너 상담, 운동 루틴, 맞춤 관리, 분위기, 재방문 의사를 섞어라. 몸 변화는 과장하지 말고 만족감 위주로 작성하라.",
    "펜션/숙박": "숙소 청결, 객실 컨디션, 친절한 안내, 편안한 휴식, 위치, 주차, 가족/커플/친구 여행 상황을 자연스럽게 섞어라. 없는 시설이나 부대서비스는 임의로 만들지 마라.",
    "미용실": "상담, 스타일 제안, 손상도 체크, 시술 만족도, 손질 편함, 친절함, 매장 분위기, 재방문 의사를 자연스럽게 섞어라. 고객 가이드에 없는 시술명이나 효과는 임의로 만들지 마라.",
    "점집": "고민 상담, 편안한 분위기, 차분한 설명, 공감, 신뢰감, 마음 정리, 재상담 의사를 중심으로 작성하라. 미래를 확정하거나 불안감을 조장하는 표현은 피하라.",
    "고기집": "고기 맛, 고기 질, 반찬 구성, 직원 응대, 청결, 가족 외식, 회식, 모임, 가격 만족도, 재방문 의사를 자연스럽게 섞어라. 고객 가이드에 없는 메뉴명은 임의로 만들지 마라.",
    "왁싱/제모": "상담, 위생, 프라이빗한 분위기, 꼼꼼한 관리, 민망함을 줄여주는 응대, 주의사항 안내, 재방문 의사를 자연스럽게 섞어라. 통증 없음이나 효과를 과장해서 단정하지 마라.",
    "출장업종": "방문 편리함, 시간 약속, 친절한 상담, 꼼꼼한 작업, 전후 설명, 깔끔한 마무리, 전문성, 재이용 의사를 자연스럽게 섞어라. 고객 가이드에 없는 작업 범위나 장비는 임의로 만들지 마라.",
    "일반/범용": "친절함, 청결, 분위기, 가격 만족도, 접근성, 재방문 의사를 업종에 맞게 자연스럽게 조합하라.",
}


PERSONA_PROMPTS = {
    "20대 자연형": "일상 공유하듯 자연스럽게, 꾸미지 않고 솔직하게 작성. ㅎㅎ/😊 가끔만 사용.",
    "20대 밝은형": "리액션 살짝 있는 밝은 말투, !와 ㅎㅎ 적당히 사용.",
    "20대 친구추천형": "친구한테 말하듯 편하게, 추천 느낌 살짝 포함.",
    "20대 혼자방문": "혼자 방문한 느낌, 어색함에서 편해진 흐름 포함.",
    "20대 데이트": "데이트 느낌, 분위기와 감정 중심으로 작성.",

    "20~30 남성 담백형": "짧고 간결하게, 감정 과하지 않게 작성.",
    "20~30 남성 현실형": "실제 경험 위주, 장단점 균형 있게 표현.",
    "20~30 남성 무난형": "특별한 과장 없이 무난하게 만족 표현.",
    "20~30 남성 재방문": "이미 몇 번 와본 느낌으로 자연스럽게 작성.",

    "30대 여성 꼼꼼형": "과정, 설명, 결과를 꼼꼼하게 풀어서 작성.",
    "30대 여성 현실형": "과장 없이 현실적인 만족 위주.",
    "30대 여성 비교형": "다른 곳과 비교한 느낌 살짝 포함.",
    "30대 여성 재방문": "단골 느낌, 익숙한 분위기 강조.",

    "40대 차분형": "차분하고 정리된 말투, 신뢰감 중심.",
    "50대 안정형": "편안함, 신뢰, 안정감 위주로 작성.",
    "중장년 가족형": "가족과 함께 이용한 느낌 강조.",

    "가성비형": "가격 대비 만족 강조, 효율 중심.",
    "퀄리티중시형": "서비스나 결과 퀄리티 중심으로 평가.",
    "분위기중시형": "공간, 분위기, 첫인상, 이용 중 느낀 감정 위주.",
    "친절중시형": "직원 응대, 설명, 배려, 서비스 태도 중심.",

    "첫방문 조심형": "처음이라 걱정했던 부분에서 만족으로 이어지는 흐름 포함.",
    "급하게 방문": "급하게 방문했지만 생각보다 괜찮았던 흐름.",
    "추천받고 방문": "지인 추천으로 방문한 느낌 강조.",
    "검색해서 방문": "리뷰나 검색을 통해 방문한 흐름.",
    "재방문 확정형": "다음에도 다시 이용할 것 같은 느낌을 자연스럽게 작성.",

    "짧은 후기형": "길게 설명하지 않고 핵심만 간단히 작성.",
    "감정절제형": "감정 표현을 줄이고 사실 중심으로 담백하게 작성.",
    "살짝 감탄형": "짧은 감탄 후 좋았던 이유를 자연스럽게 설명.",
    "스토리형": "방문 상황, 이용 경험, 느낀 점 순서로 자연스럽게 작성.",

    "가벼운 리액션": "ㅋㅋ, ㅎㅎ를 가볍게 섞어 자연스럽게 작성.",
    "이모티콘 약간": "😊, 👍 같은 이모티콘을 일부만 자연스럽게 사용.",
    "친근한 말투": "친구에게 말하듯 편하게, 너무 딱딱하지 않게 작성.",

    "단골 느낌": "여러 번 방문한 사람처럼 익숙한 만족감을 자연스럽게 포함.",
    "초보 경험": "처음이라 몰랐던 부분이나 걱정했던 점을 자연스럽게 언급.",
    "기대이하→만족": "처음엔 기대가 크지 않았지만 이용 후 만족한 흐름.",
    "무난 만족형": "크게 튀지 않지만 괜찮고 만족스러웠던 후기 느낌."
}

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


st.set_page_config(page_title="예약자원고생성", layout="wide")

if "generated_results" not in st.session_state:
    st.session_state.generated_results = []

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(99,102,241,0.16), transparent 32%),
        radial-gradient(circle at top right, rgba(14,165,233,0.14), transparent 30%),
        linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #ffffff 100%);
}

.block-container {
    max-width: 1320px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 38px;
    font-weight: 950;
    margin-bottom: 8px;
    letter-spacing: -0.8px;
    background: linear-gradient(90deg, #2563eb, #7c3aed, #db2777);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    font-size: 15px;
    color: #64748b;
    margin-bottom: 24px;
}

.top-card {
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 24px;
    padding: 24px 26px;
    box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
    margin-bottom: 22px;
}

.panel-title {
    font-size: 21px;
    font-weight: 900;
    margin-bottom: 16px;
    letter-spacing: -0.3px;
}

.section-caption {
    color: #64748b;
    font-size: 13px;
    margin-top: -8px;
    margin-bottom: 16px;
}

.result-box {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 17px;
    padding: 15px 17px;
    margin-bottom: 11px;
    line-height: 1.65;
    font-size: 15px;
    box-shadow: 0 10px 22px rgba(15, 23, 42, 0.045);
}

.info-box {
    background: rgba(255,255,255,0.78);
    border: 1px dashed #94a3b8;
    border-radius: 18px;
    padding: 22px;
    color: #64748b;
    line-height: 1.7;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.04);
}

.stButton > button {
    height: 50px;
    border-radius: 15px;
    font-weight: 900;
    border: none;
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.14);
}

.stButton > button:hover {
    transform: translateY(-1px);
    transition: 0.15s ease;
}

input, textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
}

[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
}

[data-testid="stTextArea"] textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    min-height: 140px;
}

/* selectbox 전체 박스 */
[data-testid="stSelectbox"] [data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
}

/* 선택된 값 영역 테두리 제거 */
[data-testid="stSelectbox"] [data-baseweb="tag"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* 선택된 값 안쪽 텍스트 */
[data-testid="stSelectbox"] [data-baseweb="tag"] span {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* 내부 input 테두리/밑줄 제거 */
[data-testid="stSelectbox"] input {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
    text-decoration: none !important;
}

/* 이상한 빨간 밑줄 제거 */
[data-testid="stSelectbox"] * {
    text-decoration: none !important;
}


hr {
    margin-top: 10px;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="top-card">
        <div class="main-title">✅ 네이버 예약자 리뷰 원고 생성기</div>
        <div class="sub-title">업종, 고객 가이드, 말투를 선택하면 자연스러운 예약자 리뷰 원고를 한 번에 생성합니다.</div>
    </div>
    """,
    unsafe_allow_html=True
)

left, right = st.columns([1, 1.25], gap="large")

with left:
    st.markdown('<div class="panel-title">⚙️ 생성 설정</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">필요한 조건을 입력한 뒤 리뷰 생성 버튼을 눌러주세요.</div>', unsafe_allow_html=True)

    category_group = st.selectbox("업종 대분류 선택", list(CATEGORY_PATTERNS.keys()))
    category = st.text_input("상세 업종", value="")

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

    must_include = st.text_input("필수 포함 키워드", value="")

    forbidden = st.text_input(
        "금지 키워드 / 금지 표현",
        value="과장된 표현, 없는 메뉴명, 없는 서비스, 무조건 최고"
    )

    col_run, col_clear = st.columns(2)

    run_btn = col_run.button("🚀 리뷰 생성 시작", use_container_width=True)
    clear_btn = col_clear.button("🗑 결과 초기화", use_container_width=True)

if clear_btn:
    st.session_state.generated_results = []
    st.rerun()

if run_btn:
    if not CLAUDE_API_KEY:
        st.error("CLAUDE_API_KEY를 입력해주세요.")

    elif not guide.strip():
        st.error("고객 가이드 또는 업체 장점을 입력해주세요.")

    elif min_len > max_len:
        st.error("최소 글자수가 최대 글자수보다 클 수 없습니다.")

    else:
        client = Anthropic(api_key=CLAUDE_API_KEY)
        target_count = int(count)

        with right:
            status_text = st.empty()
            status_text.info(f"⏳ 리뷰 {target_count}개 생성 중입니다. 잠시만 기다려주세요...")

        try:
            selected_starts = random.choices(
                CATEGORY_PATTERNS[category_group][situation],
                k=target_count
            )

            selected_styles = random.choices(
                WRITING_STYLES,
                k=target_count
            )
            persona_keys = list(PERSONA_PROMPTS.keys())
            persona_cycle = (persona_keys * ((target_count // len(persona_keys)) + 1))[:target_count]
            random.shuffle(persona_cycle)

            
            final_prompt = f"""
너는 실제 방문자가 작성한 것처럼 자연스러운 네이버 예약자 리뷰 원고를 작성한다.

[페르소나 순서]
각 리뷰는 아래 순서의 페르소나를 하나씩 적용해서 작성한다.
각 리뷰는 서로 다른 사람이 쓴 것처럼 말투와 표현을 다르게 한다.
각 리뷰는 반드시 서로 다른 페르소나 스타일을 명확하게 반영한다.

{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(persona_cycle)])}

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

[페르소나 리스트]
각 리뷰는 아래 페르소나 중 하나를 사용하여 작성한다.
리뷰마다 서로 다른 사람이 작성한 것처럼 말투, 표현, 감정이 다르게 나오도록 한다.
페르소나는 최대한 골고루 분배해서 사용한다.

{chr(10).join([f"- {k}: {v}" for k, v in PERSONA_PROMPTS.items()])}

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

[중요 규칙 추가]
- 모든 리뷰는 서로 다른 사람이 작성한 것처럼 자연스럽게 작성한다.
- 같은 말투, 같은 표현이 반복되지 않도록 한다.
- 동일한 페르소나가 연속으로 나오지 않도록 한다.

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

            with right:
                status_text.success("✅ 생성 완료")

            if len(st.session_state.generated_results) < target_count:
                st.warning(
                    f"요청한 {target_count}개 중 {len(st.session_state.generated_results)}개만 생성됐습니다. "
                    "리뷰 수를 줄이거나 max_tokens를 늘려보세요."
                )

        except Exception as e:
            st.error(f"오류: {str(e)}")

with right:
    st.markdown('<div class="panel-title">📝 생성 결과</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">생성된 결과를 바로 복사해서 시트에 붙여넣을 수 있습니다.</div>', unsafe_allow_html=True)

    if st.session_state.generated_results:
        excel_ready = "\n".join(st.session_state.generated_results)
        copy_text = json.dumps(excel_ready)

        components.html(
            f"""
            <button onclick='navigator.clipboard.writeText({copy_text}); this.innerText="✅ 복사 완료";'
                style="
                    width:100%;
                    height:48px;
                    border:none;
                    border-radius:15px;
                    background:linear-gradient(90deg,#2563eb,#7c3aed,#db2777);
                    color:white;
                    font-size:15px;
                    font-weight:900;
                    cursor:pointer;
                    margin-bottom:12px;
                    box-shadow:0 12px 24px rgba(37,99,235,0.22);
                ">
                📋 전체 원고 복사하기
            </button>
            """,
            height=64
        )

        st.text_area(
            "📋 엑셀 붙여넣기용 전체 복사",
            value=excel_ready,
            height=260
        )

        st.markdown("#### 미리보기")

        for idx, text in enumerate(st.session_state.generated_results):
            st.markdown(
                f"""
                <div class="result-box">
                    <b>{idx + 1}.</b> {text}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.markdown(
            """
            <div class="info-box">
                아직 생성된 리뷰가 없습니다.<br>
                왼쪽에서 업종과 고객 가이드를 입력한 뒤 <b>리뷰 생성 시작</b> 버튼을 눌러주세요.
            </div>
            """,
            unsafe_allow_html=True
        )
