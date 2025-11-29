import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. 페이지 설정
st.set_page_config(page_title="FET 규정 비서", page_icon="🏋️")
st.title("🏋️ Far East Throwdown 규정 비서")
st.caption("2026 룰북 기반으로 답변합니다. (운영 총괄: 김슬기 / 기본 문의 방어 중)")

# 2. API 키 설정
if "GEMINI_API_KEY" in st.secrets:
    api_key = "AIzaSyD3HYCDN58Aet5q0PlgoxmzyP8yigeRFXk"
else:
    st.error("설정 파일(Secrets)에 API 키가 없습니다.")
    st.stop()

genai.configure(api_key=api_key)

# 3. 룰북 PDF 텍스트 추출 함수
@st.cache_resource
def load_rulebook():
    try:
        # 파일명 'rulebook.pdf'가 맞는지 확인해주세요
        pdf_path = "rulebook.pdf" 
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except FileNotFoundError:
        return None

rulebook_text = load_rulebook()

if not rulebook_text:
    st.error("❌ 룰북 PDF 파일을 찾을 수 없습니다. GitHub에 파일을 올렸는지 확인해주세요.")
    st.stop()

# 4. 모델 설정 (다시 똑똑한 1.5 Flash로 복귀!)
# requirements.txt를 업데이트 했다면 이제 이 모델이 작동합니다.
system_instruction = f"""
너는 Far East Throwdown (FET) 국제 대회의 업무를 돕는 똑똑한 비서다.
현재 이 챗봇은 웹사이트의 '티켓 판매' 및 '운영'을 총괄하는 **김슬기(Operation Lead)** 님이 세팅했다.
아래의 [룰북 내용]과 [조직도]를 기반으로 답변해라.

[행동 지침]
1. 규정 관련 질문: [룰북 내용]을 기반으로 정확히 답변한다.
2. 담당자 문의: 사용자가 특정 업무에 대해 물어보면, [조직도]를 참고하여 적절한 담당자를 안내한다.
3. **문의 방어 (중요):**
   - **단순 정보 (날짜, 장소, 참가 자격 등):** 네가 룰북을 보고 직접 대답해서 **이욱현(Competition Support)** 님에게 메일이 가지 않게 막아라.
   - **티켓/결제/웹사이트 오류:** "이 부분은 운영 총괄이신 **김슬기(Operation Lead)** 님 확인이 필요합니다." 라고 안내하거나, info@fareastthrowdown.com 으로 문의하라고 해라.

[최우선 수정 사항 (룰북보다 우선함)]
1. FEC 팀전: 무조건 '상위 20팀'만 결선 진출. (25% 룰 삭제) - 조건: 팀원 전원 2026 Open 등록 및 지부 등록 필수.
2. FEC 개인전: 쿼터파이널 '2,000등' 이내. (1,000등 아님)

[조직도 및 담당 업무]
- 이원우 (원우쌤 / Director): 전체 총괄
- 김동석 (동석쌤 / Sub Director): 비용/예산 관련
- 그레이스 정 (그레이스쌤 / Marketing): 마케팅
- **김슬기 (슽쌤 / Operation Lead):** 운영 기획, **티켓 판매 세팅**, 웹사이트 관리, 자원봉사자 운영
- 한진실 (진실쌤 / Competition Support Lead): Competition Corner 시스템 관리, 복잡한 선수 문의
- 이두영 (뚜쌤 / Competition Team Lead): 헤드저지, 룰북 최종 확인
- 이욱현 (욱현쌤 / Competition Team Support): 헤드저지, **기본 문의(날짜, 기간 등 단순 정보) 담당** -> *챗봇이 1차로 방어할 대상*
- 김대훈 (론쌤): 장비 및 시설(Rig)
- 여희재 (희재쌤 / Media Lead): 영상/중계
- 박지현 (지현쌤 / Product Design): 디자인
- 이상민 (상민쌤 / Support): CS 일반 (info@ 메일)

[룰북 내용]
{rulebook_text}
"""

# 모델 초기화
try:
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error(f"모델 설정 중 오류가 발생했습니다. requirements.txt를 확인해주세요. ({e})")
    st.stop()

# 5. 채팅 인터페이스
if "messages" not in st.session_state:
    # 챗봇의 첫 인사 (화면엔 보이지만 API엔 보내지 않음)
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! FET 운영팀 챗봇입니다. 무엇을 도와드릴까요? (팀전 규정, 환불, 담당자 문의 등)"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("규정 확인 중..."):
            try:
                # [핵심 수정] 대화 기록 구성 시 첫 인사(assistant) 제거
                chat_history = []
                for msg in st.session_state.messages:
                    # 첫 인사는 건너뛰고, 실제 대화만 API로 보냄
                    if msg["content"] == "안녕하세요! FET 운영팀 챗봇입니다. 무엇을 도와드릴까요? (팀전 규정, 환불, 담당자 문의 등)":
                        continue
                        
                    if msg["role"] == "user":
                        chat_history.append({"role": "user", "parts": [msg["content"]]})
                    elif msg["role"] == "assistant":
                        chat_history.append({"role": "model", "parts": [msg["content"]]})
                
                response = model.generate_content(chat_history)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                # 에러가 나면 빨간 글씨로 확실히 보여줌
                st.error(f"오류가 발생했습니다: {e}")
