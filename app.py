import streamlit as st
from anthropic import Anthropic
import random
import re
import streamlit.components.v1 as components
import json
import time
import sqlite3
from datetime import datetime

CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]
APP_PASSWORD = st.secrets.get("APP_PASSWORD")

st.set_page_config(
    page_title="예약자원고생성",
    layout="wide"
)

def init_db():
    conn = sqlite3.connect("reviews.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            category_group TEXT,
            category TEXT,
            guide TEXT,
            review_count INTEGER,
            reviews_text TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_review_batch(category_group, category, guide, reviews):
    conn = sqlite3.connect("reviews.db")
    cur = conn.cursor()
    reviews_text = "\n".join(reviews)
    cur.execute("""
        INSERT INTO review_batches (
            created_at, category_group, category, guide, review_count, reviews_text
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        category_group,
        category,
        guide,
        len(reviews),
        reviews_text
    ))
    conn.commit()
    conn.close()

init_db()

if not APP_PASSWORD:
    st.error("APP_PASSWORD를 secrets에 추가해주세요.")
    st.stop()

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(124,58,237,0.18), transparent 32%),
            radial-gradient(circle at bottom right, rgba(236,72,153,0.14), transparent 30%),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #ffffff 100%);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 520px;
        padding-top: 10rem;
    }

    .login-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(226,232,240,0.9);
        border-radius: 28px;
        padding: 38px 34px 30px;
        box-shadow: 0 24px 70px rgba(15,23,42,0.10);
        backdrop-filter: blur(18px);
    }

    .login-brand {
        text-align: center;
        margin-bottom: 28px;
    }

    .login-logo {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        margin: 0 auto 16px;
        background: linear-gradient(135deg, #7c3aed, #a855f7, #ec4899);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 950;
        box-shadow: 0 16px 34px rgba(124,58,237,0.28);
    }

    .login-badge {
        display: inline-block;
        padding: 6px 13px;
        border-radius: 999px;
        background: rgba(124,58,237,0.10);
        color: #6d28d9;
        font-size: 12px;
        font-weight: 900;
        margin-bottom: 14px;
        border: 1px solid rgba(124,58,237,0.18);
    }

    .login-title {
        font-size: 34px;
        font-weight: 950;
        letter-spacing: -1px;
        color: #0f172a;
        margin-bottom: 10px;
    }

    .login-desc {
        color: #64748b;
        font-size: 14px;
        line-height: 1.65;
    }

    [data-testid="stTextInput"] {
    width: 100% !important;
}

    [data-testid="stTextInput"] > div {
    width: 100% !important;
}

    [data-testid="stTextInput"] div[data-baseweb="input"] {
    width: 100% !important;
    height: 52px !important;
    border-radius: 0 !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    box-shadow: none !important;
}

    [data-testid="stTextInput"] input {
    height: 52px !important;
    min-height: 52px !important;
    border-radius: 0 !important;
    border: none !important;
    background: #ffffff !important;
    font-size: 15px !important;
    padding-left: 14px !important;
    box-shadow: none !important;
}

    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border: 1px solid #7c3aed !important;
    box-shadow: none !important;
}

    .stButton > button {
        width: 100%;
        height: 56px;
        border-radius: 16px;
        border: none;
        background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899);
        color: white;
        font-size: 16px;
        font-weight: 900;
        box-shadow: 0 18px 36px rgba(124,58,237,0.28);
        transition: all 0.18s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        color: white;
        box-shadow: 0 24px 48px rgba(124,58,237,0.34);
    }

    .login-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        margin-top: 22px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-card">
        <div class="login-brand">
            <div class="login-logo">U</div>
            <div class="login-badge">USCM INTERNAL SYSTEM</div>
            <div class="login-title">AI Review Studio</div>
            <div class="login-desc">
                예약자 원고 생성 시스템입니다.<br>
                관리자 비밀번호를 입력해주세요.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input(
        "비밀번호",
        type="password",
        label_visibility="collapsed",
        placeholder="비밀번호 입력"
    )

    if st.button("로그인"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")

    st.markdown('<div class="login-footer">© USCM AI Review Studio. Private Access Only.</div>', unsafe_allow_html=True)
    st.stop()


check_login()


st.markdown("""
<style>
.top-guide-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.10), rgba(236,72,153,0.08));
    border: 1px solid rgba(221,214,254,0.9);
    border-radius: 24px;
    padding: 28px 30px;
    margin-bottom: 20px;
    box-shadow: 0 14px 36px rgba(124,58,237,0.10);
}

.top-guide-inner {
    display: flex;
    align-items: center;
    gap: 18px;
}

.top-guide-icon {
    width: 62px;
    height: 62px;
    border-radius: 22px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    box-shadow: 0 16px 32px rgba(124,58,237,0.28);
}

.top-guide-title {
    font-size: 28px;
    font-weight: 950;
    color: #111827;
    margin-bottom: 8px;
}

.top-guide-desc {
    color: #374151;
    font-size: 15px;
    line-height: 1.7;
}

.form-section-title {
    font-size: 19px;
    font-weight: 950;
    color: #111827;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.form-section-title span {
    display: inline-flex;
    width: 34px;
    height: 30px;
    border-radius: 10px;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
    font-weight: 950;
}

.badge-purple {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
}

.badge-pink {
    background: linear-gradient(135deg, #ec4899, #f472b6);
}

.badge-mint {
    background: linear-gradient(135deg, #14b8a6, #2dd4bf);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 22px !important;
    border: 1px solid rgba(226,232,240,0.95) !important;
    box-shadow: 0 12px 32px rgba(15,23,42,0.05);
    background: rgba(255,255,255,0.88);
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 22px 22px 18px !important;
}
</style>
""", unsafe_allow_html=True)

.result-header-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(236,72,153,0.10));
    border: 1px solid rgba(221,214,254,0.95);
    border-radius: 24px;
    padding: 26px 28px;
    margin-bottom: 20px;
    box-shadow: 0 14px 36px rgba(124,58,237,0.10);
    display: flex;
    align-items: center;
    gap: 18px;
}

.result-header-icon {
    width: 60px;
    height: 60px;
    border-radius: 22px;
    background: linear-gradient(135deg, #ec4899, #8b5cf6);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    box-shadow: 0 16px 32px rgba(236,72,153,0.24);
    flex-shrink: 0;
}

.result-header-title {
    font-size: 28px;
    font-weight: 950;
    color: #111827;
    margin-bottom: 8px;
}

.result-header-desc {
    color: #374151;
    font-size: 15px;
    line-height: 1.7;
}

menu = st.sidebar.radio("메뉴", ["✍️ 원고 생성", "📚 저장된 원고"])

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
    },
    "아카데미/학원": {
        "상담/등록": ["상담받으러 방문했는데", "수업 알아보다가 방문했어요", "등록 전에 상담 먼저 받아봤는데", "커리큘럼이 궁금해서 방문했어요"],
        "첫수업/체험": ["첫 수업 들어봤는데", "체험 수업 받아보고 결정했어요", "처음이라 긴장했는데", "수업 분위기 궁금해서 참여해봤어요"],
        "강사/수업": ["강사님 설명이 이해하기 쉬워서", "수업 진행이 체계적인 느낌이라", "질문해도 편하게 알려주셔서", "수업 분위기가 딱 부담 없어서 좋았어요"],
        "시설/분위기": ["공부하기 좋은 분위기라", "시설이 깔끔하게 관리돼 있어서", "집중하기 괜찮은 환경이라", "전체적으로 차분한 분위기라 좋았어요"],
        "재등록/추천": ["꾸준히 다녀볼 생각입니다", "주변에도 추천하고 싶네요", "다음 과정도 이어서 들어보고 싶어요", "생각보다 만족도가 높았어요"]
    },
    "횟집/해산물": {
        "회식/모임": ["회식 자리로 방문", "친구들이랑 해산물 먹으러 방문", "가족 외식으로 방문", "오랜만에 모임 있어서 방문"],
        "추천/검색": ["지인 추천으로 방문", "후기 괜찮아서 방문", "근처 횟집 찾다가 방문", "해산물 먹고 싶어서 검색하다 방문"],
        "술자리/저녁": ["술 한잔하려고 방문", "퇴근 후 저녁 먹으러 방문", "가볍게 한잔할 겸 방문", "저녁 메뉴 고민하다 방문"],
        "신선도/구성": ["회 신선하다고 해서 방문", "해산물 구성 괜찮다고 해서 방문", "스끼다시 잘 나온다고 해서 방문", "회 퀄리티 괜찮다는 얘기 듣고 방문"],
        "가족/부모님": ["부모님 모시고 방문", "가족끼리 식사하러 방문", "어른들 모시고 가기 괜찮을 것 같아서 방문", "주말 가족 외식으로 방문"]
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
    "횟집/해산물": "회 신선도, 해산물 구성, 스끼다시, 양, 분위기, 술자리, 가족 외식, 직원 응대, 청결, 가격 만족도, 재방문 의사를 자연스럽게 섞어라. 고객 가이드에 없는 어종, 메뉴명, 원산지, 없는 서비스는 임의로 만들지 마라."
}

PERSONA_PROMPTS = {
    "20대 자연형": "일상 공유하듯 자연스럽게, 꾸미지 않고 솔직하게 작성. ㅎㅎ/😊 가끔만 사용.",
    "20대 밝은형": "리액션 살짝 있는 밝은 말투, !와 ㅎㅎ 적당히 사용.",
    "20대 친구추천형": "친구한테 말하듯 편하게, 추천 느낌 살짝 포함.",
    "20대 혼자방문": "혼자 방문한 느낌, 어색함에서 편해진 흐름 포함.",
    "20대 데이트": "데이트 느낌, 분위기와 감정 중심으로 작성.",
    "20대 학생형": "가격 부담이나 선택 고민을 살짝 언급하며 현실적으로 작성.",
    "20대 즉흥방문형": "계획 없이 들렀다가 괜찮았던 흐름으로 자연스럽게 작성.",
    "20대 수다형": "말이 조금 많은 편처럼 느낀 점을 자연스럽게 풀어 작성.",
    "20~30 남성 담백형": "짧고 간결하게, 감정 과하지 않게 작성.",
    "20~30 남성 현실형": "실제 경험 위주, 장단점 균형 있게 표현.",
    "20~30 남성 무난형": "특별한 과장 없이 무난하게 만족 표현.",
    "20~30 남성 재방문": "이미 몇 번 와본 느낌으로 자연스럽게 작성.",
    "20~30 남성 귀차니즘형": "복잡한 설명보다 빨리 해결돼서 좋았다는 흐름으로 작성.",
    "20~30 남성 비교형": "다른 곳과 비교해본 뒤 괜찮았다는 식으로 담백하게 작성.",
    "20~30 남성 실용형": "분위기보다 결과, 가격, 편리함 같은 실용적인 부분 중심.",
    "30대 여성 꼼꼼형": "과정, 설명, 결과를 꼼꼼하게 풀어서 작성.",
    "30대 여성 현실형": "과장 없이 현실적인 만족 위주.",
    "30대 여성 비교형": "다른 곳과 비교한 느낌 살짝 포함.",
    "30대 여성 재방문": "단골 느낌, 익숙한 분위기 강조.",
    "30대 여성 예민형": "위생, 설명, 응대, 세부 과정 등 디테일을 신경 쓰는 느낌.",
    "30대 여성 추천형": "주변에 조심스럽게 추천할 만하다는 흐름으로 작성.",
    "30대 여성 바쁜직장인형": "시간, 예약, 동선, 빠른 응대 등 편의성을 자연스럽게 언급.",
    "40대 차분형": "차분하고 정리된 말투, 신뢰감 중심.",
    "40대 현실검토형": "가격, 설명, 결과를 따져보고 납득한 느낌으로 작성.",
    "40대 가족동행형": "가족과 함께 이용하거나 가족 입장에서 본 만족감을 포함.",
    "50대 안정형": "편안함, 신뢰, 안정감 위주로 작성.",
    "50대 신뢰중시형": "설명, 응대 태도, 오래 이용할 수 있을 것 같은 믿음 중심.",
    "중장년 가족형": "가족과 함께 이용한 느낌 강조.",
    "가성비형": "가격 대비 만족 강조, 효율 중심.",
    "퀄리티중시형": "서비스나 결과 퀄리티 중심으로 평가.",
    "분위기중시형": "공간, 분위기, 첫인상, 이용 중 느낀 감정 위주.",
    "친절중시형": "직원 응대, 설명, 배려, 서비스 태도 중심.",
    "청결중시형": "정돈된 느낌, 위생, 깔끔함을 자연스럽게 언급.",
    "시간중시형": "대기, 예약 시간, 진행 속도, 일정 맞추기 좋았던 점 중심.",
    "설명중시형": "모르는 부분을 이해하기 쉽게 설명해준 점을 중심으로 작성.",
    "결과중시형": "과정보다 이용 후 만족감이나 체감된 결과 중심.",
    "첫방문 조심형": "처음이라 걱정했던 부분에서 만족으로 이어지는 흐름 포함.",
    "급하게 방문": "급하게 방문했지만 생각보다 괜찮았던 흐름.",
    "추천받고 방문": "지인 추천으로 방문한 느낌 강조하되 같은 문장으로 시작하지 않기.",
    "검색해서 방문": "검색이나 비교 후 선택한 흐름을 언급하되 '리뷰 보고 골랐는데'로 반복 시작하지 않기.",
    "재방문 확정형": "다음에도 다시 이용할 것 같은 느낌을 자연스럽게 작성.",
    "우연히 방문형": "지나가다 또는 근처 일정 중 들른 느낌으로 작성.",
    "고민끝선택형": "여러 곳을 고민하다 선택한 흐름으로 작성.",
    "기대낮음만족형": "처음 기대가 크지 않았지만 이용 후 괜찮았던 흐름.",
    "짧은 후기형": "길게 설명하지 않고 핵심만 간단히 작성.",
    "감정절제형": "감정 표현을 줄이고 사실 중심으로 담백하게 작성.",
    "살짝 감탄형": "짧은 감탄 후 좋았던 이유를 자연스럽게 설명.",
    "스토리형": "방문 상황, 이용 경험, 느낀 점 순서로 자연스럽게 작성.",
    "혼잣말형": "혼자 생각하듯 자연스럽게, 딱딱하지 않게 작성.",
    "대화체형": "친구에게 말하듯 가볍게 풀어 작성.",
    "관찰형": "공간, 응대, 과정 등을 차분히 관찰한 느낌으로 작성.",
    "후기잘안씀형": "원래 후기 잘 안 쓰지만 남긴다는 느낌을 과하지 않게 포함.",
    "가벼운 리액션": "ㅋㅋ, ㅎㅎ를 가볍게 섞어 자연스럽게 작성.",
    "이모티콘 약간": "😊, 👍 같은 이모티콘을 일부만 자연스럽게 사용.",
    "친근한 말투": "친구에게 말하듯 편하게, 너무 딱딱하지 않게 작성.",
    "담백한 말투": "감탄사 없이 차분하고 짧게 작성.",
    "조금 긴 말투": "한 가지 경험을 조금 길게 풀어 쓰는 방식.",
    "문장짧게끊기형": "문장을 짧게 끊어서 실제 후기처럼 작성.",
    "부드러운 존댓말형": "전체적으로 부드러운 존댓말로 안정감 있게 작성.",
    "단골 느낌": "여러 번 방문한 사람처럼 익숙한 만족감을 자연스럽게 포함.",
    "초보 경험": "처음이라 몰랐던 부분이나 걱정했던 점을 자연스럽게 언급.",
    "기대이하→만족": "처음엔 기대가 크지 않았지만 이용 후 만족한 흐름.",
    "무난 만족형": "크게 튀지 않지만 괜찮고 만족스러웠던 후기 느낌.",
    "불편개선형": "기존에 불편했던 점이 해결된 흐름으로 작성.",
    "선택도움형": "혼자 결정하기 어려웠는데 도움을 받아 선택한 흐름.",
    "재이용고민형": "재이용할 만하다는 정도로 자연스럽게 마무리.",
    "소소한만족형": "큰 감탄보다는 소소하게 만족한 느낌으로 작성."
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
def count_chars(text):
    return len(text.strip())

def is_valid_review(review, min_len, max_len):
    length = count_chars(review)
    return min_len <= length <= max_len

def is_duplicate_review(review, existing_reviews):
    review_start = review[:20]
    for old in existing_reviews:
        if review == old:
            return True
        if old[:20] == review_start:
            return True
    return False
    
if "generated_results" not in st.session_state:
    st.session_state.generated_results = []

    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(124,58,237,0.12), transparent 32%),
            radial-gradient(circle at top right, rgba(236,72,153,0.10), transparent 30%),
            linear-gradient(135deg, #f8fafc 0%, #f5f3ff 48%, #ffffff 100%);
        color: #0f172a;
}

    [data-testid="stHeader"] {
        background: transparent;
}

    .block-container {
        max-width: 1320px;
        padding-top: 2.4rem;
        padding-bottom: 4rem;
}

    section[data-testid="stSidebar"] {
        width: 235px !important;
        min-width: 235px !important;
        background: rgba(255,255,255,0.86);
        backdrop-filter: blur(18px);
        border-right: 1px solid rgba(226,232,240,0.9);
}

    section[data-testid="stSidebar"] * {
        font-weight: 750;
}

    .hero-card {
        background: linear-gradient(135deg, #6d28d9, #8b5cf6, #ec4899);
        border-radius: 28px;
        padding: 34px 34px;
        color: white;
        box-shadow: 0 24px 70px rgba(124,58,237,0.28);
        margin-bottom: 26px;
        position: relative;
        overflow: hidden;
}

    .hero-card::after {
        content: "";
        position: absolute;
        right: -70px;
        top: -80px;
        width: 220px;
        height: 220px;
        background: rgba(255,255,255,0.14);
        border-radius: 999px;
}

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.20);
        padding: 7px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 900;
        margin-bottom: 14px;
}

    .hero-title {
        font-size: 36px;
        font-weight: 950;
        margin-bottom: 10px;
        letter-spacing: -0.8px;
}

    .hero-desc {
        font-size: 15px;
        line-height: 1.7;
        opacity: 0.96;
}

    .panel-title {
        font-size: 21px;
        font-weight: 950;
        color: #111827;
        margin: 4px 0 8px;
}

    .section-caption {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 18px;
}

    [data-testid="column"] {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(226,232,240,0.94);
        border-radius: 24px;
        padding: 24px 24px 18px;
        box-shadow: 0 18px 48px rgba(15,23,42,0.07);
}

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
        font-size: 15px !important;
}

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 4px rgba(139,92,246,0.13) !important;
}

    .stSelectbox div[data-baseweb="select"] > div {
         border-radius: 14px !important;
        border-color: #e2e8f0 !important;
}

    .stButton > button {
        height: 50px;
        border-radius: 15px;
        font-weight: 900;
        border: none;
        background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899);
        color: white;
        box-shadow: 0 14px 26px rgba(124,58,237,0.25);
        transition: all 0.18s ease;
}

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 18px 34px rgba(124,58,237,0.32);
        color: white;
}

    .stButton > button:active {
        transform: scale(0.97);
}

    .loading-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid #ddd6fe;
        border-radius: 18px;
        padding: 18px 20px;
        color: #6d28d9;
        font-weight: 900;
        box-shadow: 0 14px 32px rgba(124,58,237,0.12);
        display: flex;
        align-items: center;
        gap: 12px;
}

    .loader {
        width: 18px;
        height: 18px;
        border: 3px solid #ddd6fe;
        border-top: 3px solid #8b5cf6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
}

    @keyframes spin {
        to { transform: rotate(360deg); }
}

    .result-box {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 14px 16px;
          margin-bottom: 10px;
        line-height: 1.65;
        font-size: 15px;
        color: #1f2937;
        box-shadow: 0 8px 20px rgba(15,23,42,0.04);
}

    .info-box {
        background: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 18px;
        padding: 26px 20px;
        text-align: center;
        color: #64748b;
        line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)



if menu == "✍️ 원고 생성":
    st.markdown("""
<div class="hero-card">
    <div class="hero-badge">✨ AI 자동 생성</div>
    <div class="hero-title">네이버 예약자 리뷰 원고 생성기</div>
    <div class="hero-desc">업종, 고객 가이드, 말투를 선택하면<br>자연스러운 예약자 리뷰를 한 번에 생성합니다.</div>
</div>
""", unsafe_allow_html=True)
    
    left, right = st.columns([1, 1.25], gap="large")

with left:
    st.markdown("""
    <div class="top-guide-card">
        <div class="top-guide-inner">
            <div class="top-guide-icon">✨</div>
            <div>
                <div class="top-guide-title">AI 자동 생성</div>
                <div class="top-guide-desc">
                    업종, 고객 가이드, 말투를 선택하면<br>
                    자연스러운 예약자 리뷰를 한 번에 생성합니다.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            '<div class="form-section-title"><span class="badge-purple">01</span>업체 정보</div>',
            unsafe_allow_html=True
        )

        category_group = st.selectbox(
            "업종 대분류 선택",
            list(CATEGORY_PATTERNS.keys())
        )

        category = st.text_input(
            "상세 업종",
            value="",
            placeholder="예) 브런치 카페, 이탈리안 레스토랑, 베이커리 등"
        )

    with st.container(border=True):
        st.markdown(
            '<div class="form-section-title"><span class="badge-pink">02</span>리뷰 설정</div>',
            unsafe_allow_html=True
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

    with st.container(border=True):
        st.markdown(
            '<div class="form-section-title"><span class="badge-mint">03</span>가이드 설정</div>',
            unsafe_allow_html=True
        )

        guide = st.text_area(
            "고객 가이드 / 업체 특장점",
            value="",
            height=220,
            placeholder="예시)\n- 직원이 직접 구워줌\n- 매장이 깔끔하고 분위기가 좋음\n- 재료가 신선하고 맛이 좋음\n- ㅎㅎ, 이모지 섞어서 리얼 후기 느낌으로 작성"
        )

        must_include = st.text_input(
            "필수 포함 키워드",
            value="",
            placeholder="예) 맛있어요, 친절해요, 재방문 의사 있어요"
        )

        forbidden = st.text_input(
            "금지 키워드(,로 구분)",
            value="",
            placeholder="예) 별로, 최악, 과장 표현"
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
            mid_len = int((min_len + max_len) / 2)
            all_reviews = []
            batch_size = 10  # 균등한 분배와 정교한 제어를 위해 배치 단위 조정

            with right:
                status_text = st.empty()
                status_text.markdown(
                    f"""
                    <div class="loading-card">
                        <div class="loader"></div>
                        <div>리뷰 {target_count}개 생성 중입니다. 잠시만 기다려주세요...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            try:
                selected_styles = random.choices(WRITING_STYLES, k=target_count)
                all_situations = list(CATEGORY_PATTERNS[category_group].keys())
                situation_cycle = (all_situations * ((target_count // len(all_situations)) + 1))[:target_count]
                random.shuffle(situation_cycle)

                persona_keys = list(PERSONA_PROMPTS.keys())
                persona_cycle = (persona_keys * ((target_count // len(persona_keys)) + 1))[:target_count]
                random.shuffle(persona_cycle)

                total_count = target_count

                for start in range(0, total_count, batch_size):
                    current_batch_size = min(batch_size, total_count - start)
                    end = start + current_batch_size

                    # 구간에 따라 강제로 하한선과 상한선을 배분하여 골고루 섞이게 유도
                    if start < total_count * 0.33:
                        b_min, b_max = min_len, mid_len
                    elif start < total_count * 0.66:
                        b_min, b_max = int(mid_len * 0.9), int(mid_len * 1.1)
                    else:
                        b_min, b_max = mid_len, max_len

                    final_prompt = f"""
너는 실제 방문자가 작성한 것처럼 자연스러운 네이버 예약자 리뷰 원고를 작성한다.

[페르소나 순서]
각 리뷰는 아래 순서의 페르소나를 하나씩 적용해서 작성한다.
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(persona_cycle[start:end])])}

[업종 대분류] {category_group}  |  [상세 업종] {category}

[방문 상황 분배]
{chr(10).join([f"{i+1}. {s}" for i, s in enumerate(situation_cycle[start:end])])}

[기본 업종별 작성 방향]
{CATEGORY_RULES.get(category_group, CATEGORY_RULES["일반/범용"])}

[고객 가이드]
{guide}

[고객 가이드 반영 규칙]
- 고객 가이드에 말투, 이모티콘, ㅎㅎ, ㅋㅋ, 문장 길이, 문체 관련 요청이 있으면 반드시 우선 반영한다.
- 예: "ㅎㅎ 섞어줘", "이모지 넣어줘", "리얼 후기 느낌", "20대 말투", "말투 다양하게" 같은 요청은 업체 특장점보다 우선 적용한다.
- 단, 모든 리뷰에 과하게 반복하지 말고 자연스럽게 일부 리뷰에만 섞는다.

[필수 포함 키워드]
{must_include if must_include else "없음"}

[금지 키워드 / 금지 표현]
{forbidden if forbidden else "없음"}

[작성 요청]
리뷰를 총 {current_batch_size}개 작성한다.

[글자 수 제한 규정 - 최우선 지시사항]
- 이번에 생성하는 모든 리뷰는 공백을 포함하여 반드시 ** {b_min}자 이상, {b_max}자 이하 ** 범위 내로 작성해야 합니다.
- 단 한 줄도 {b_min}자 미만으로 짧게 작성하거나 {b_max}자를 초과해서는 안 됩니다.

[작성 규칙]
1. 번호 없이 리뷰 문장만 작성한다.
2. 각 리뷰는 반드시 줄바꿈으로 구분한다.
3. 한 줄에 리뷰 1개만 작성한다.
4. 광고 문구처럼 보이는 표현은 피하고 실제 방문 후기처럼 작성한다.
5. 문장 끝맺음을 매번 다르게 작성한다.
6. 고객 가이드에 말투나 문체 요청이 있으면 반드시 반영한다.
7. 모든 리뷰의 첫 문장을 서로 다르게 시작한다. 같은 첫 문장을 반복하지 않는다.
8. 같은 표현이나 단어를 여러 리뷰에서 반복하지 않는다.
9. 모든 리뷰는 실제 방문자가 자신의 경험을 이야기하는 흐름으로 작성한다.
10. 장점만 나열하지 말고 방문 계기 → 이용 경험 → 느낀 점 순서가 자연스럽게 이어지도록 작성한다.
11. 일부 리뷰에는 ㅎㅎ, ㅋㅋ, 😊, 👍 같은 표현을 자연스럽게 섞되 과하게 사용하지 않는다.
12. 말투는 존댓말, 반말 느낌, 담백한 말투, 수다스러운 말투 등을 자연스럽게 섞는다.
13. 문장 길이도 다양하게 작성한다. 짧은 문장과 긴 문장을 적절히 섞는다.
14. 사람마다 중요하게 생각하는 포인트가 다르도록 작성한다. (친절, 분위기, 가격, 청결, 편의성, 결과 등)
15. 모든 리뷰가 너무 칭찬만 하지 않도록, "생각보다", "의외로", "처음엔 걱정했는데" 같은 자연스러운 흐름을 일부 포함한다.
16. 후기마다 표현 방식이 서로 다른 사람이 작성한 것처럼 느껴지도록 작성한다.
17. AI가 작성한 느낌이 들지 않도록 일정한 문장 패턴이나 표현을 반복하지 않는다.
18. 고객 가이드에 없는 메뉴명, 시설, 서비스, 이벤트, 혜택은 절대 임의로 만들어 작성하지 않는다.
19. 리뷰마다 방문 목적과 상황을 자연스럽게 다르게 표현한다. (혼자 방문, 가족, 친구, 데이트, 퇴근 후, 주말 방문 등)
20. 실제 네이버 플레이스 후기를 읽는 것처럼 자연스럽고 생활감 있는 표현을 사용한다.
21. 모든 리뷰는 '방문 계기 → 이용 과정 → 만족했던 점 → 마무리'의 흐름을 자연스럽게 갖도록 작성한다.

[반복 방지 규칙]
아래 표현은 그대로 사용하지 않는다.
{BANNED_PHRASES}
"""

                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=12000,
                        temperature=1.0,
                        system=(
                            "당신은 자연스러운 네이버 예약자 리뷰 원고를 작성하는 전문가입니다. "
                            "글자 수 하한선 규정을 엄격하게 준수하여 절대 짧은 문장을 생성하지 마십시오."
                        ),
                        messages=[{"role": "user", "content": final_prompt}]
                    )

                    raw_text = message.content[0].text.strip()
                    batch_reviews = clean_reviews(raw_text)

                    # 가드레일: 글자수 범위와 중복 여부를 검사한 뒤 누적
                    for r in batch_reviews:
                        r = r.strip()

                        if not is_valid_review(r, min_len, max_len):
                            continue

                        if is_duplicate_review(r, all_reviews):
                            continue

                        all_reviews.append(r)

                        if len(all_reviews) >= target_count:
                            break

                    time.sleep(1)

                st.session_state.generated_results = all_reviews[:target_count]

                save_review_batch(
                    category_group,
                    category,
                    guide,
                    st.session_state.generated_results
                )

                with right:
                    status_text.success("✅ 생성 완료")

                if len(st.session_state.generated_results) < target_count:
                    st.warning(
                        f"요청한 {target_count}개 중 규격을 만족하는 {len(st.session_state.generated_results)}개만 생성됐습니다. 부족할 경우 다시 시도해 주세요."
                    )

            except Exception as e:
                st.error(f"오류: {str(e)}")

    with right:
    st.markdown("""
    <div class="result-header-card">
        <div class="result-header-icon">📝</div>
        <div>
            <div class="result-header-title">생성 결과</div>
            <div class="result-header-desc">
                생성된 리뷰가 아래에 표시됩니다.<br>
                생성 후 바로 복사하여 사용할 수 있습니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
        if st.session_state.generated_results:
            excel_ready = "\n".join(st.session_state.generated_results)
            copy_text = json.dumps(excel_ready)

            components.html(f"""
            <button onclick='navigator.clipboard.writeText({copy_text}); this.innerText="✅ 복사 완료";'
                style="width:100%; height:48px; border:none; border-radius:15px; background:linear-gradient(90deg,#2563eb,#7c3aed,#db2777); color:white; font-size:15px; font-weight:900; cursor:pointer; margin-bottom:12px; box-shadow:0 12px 24px rgba(37,99,235,0.22);">
                📋 전체 원고 복사하기
            </button>
            """, height=64)

            st.text_area("📋 엑셀 붙여넣기용 전체 복사", value=excel_ready, height=260)
            st.markdown("#### 미리보기")
            for idx, text in enumerate(st.session_state.generated_results):
                st.markdown(f'<div class="result-box"><b>{idx + 1}.</b> {text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">아직 생성된 리뷰가 없습니다.<br>왼쪽에서 업종과 고객 가이드를 입력한 뒤 <b>리뷰 생성 시작</b> 버튼을 눌러주세요.</div>', unsafe_allow_html=True)

if menu == "📚 저장된 원고":
    st.markdown("""
    <div class="hero-card">
        <div class="hero-badge">💾 Saved History</div>
        <div class="hero-title">저장된 원고</div>
        <div class="hero-desc">최근 생성된 리뷰 원고를 확인하고 다시 복사할 수 있습니다.</div>
    </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect("reviews.db")
    saved_batches = conn.execute("""
        SELECT id, created_at, category_group, category, review_count, reviews_text
        FROM review_batches ORDER BY id DESC LIMIT 100
    """).fetchall()
    conn.close()

    if not saved_batches:
        st.markdown("""
        <div class="info-box">
            아직 저장된 원고가 없습니다.<br>
            원고 생성 메뉴에서 리뷰를 생성하면 이곳에 자동 저장됩니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        for row in saved_batches:
            batch_id, created_at, category_group, category, review_count, reviews_text = row

            with st.expander(f"🗂 {created_at} | {category_group} | {category} | {review_count}개"):
                st.text_area(
                    "전체 원고",
                    value=reviews_text,
                    height=300,
                    key=f"batch_{batch_id}"
                )
