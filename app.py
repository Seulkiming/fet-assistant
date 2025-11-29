import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. 페이지 설정
st.set_page_config(page_title="FET 내부 업무 어시스턴트", page_icon="💬💕")
st.title("팀 FET 를 위한 업무 도우미")
st.caption("문제가 발생하면 슭쌤에게 문의하세요.")

# 2. 사이드바에 API 키 입력 (보안을 위해 비밀번호처럼 처리)
# 실제 배포시에는 Streamlit Secrets 기능을 사용하는 것이 좋으나, 
# 편의상 코드 내 혹은 환경변수로 처리하거나, 지금은 입력창을 숨기고 Secrets에서 가져오도록 설정합니다.
if "GEMINI_API_KEY" in st.secrets:
    api_key = "AIzaSyD3HYCDN58Aet5q0PlgoxmzyP8yigeRFXk"
    genai.configure(api_key=api_key)
else:
    st.error("설정 파일(Secrets)에 API 키가 없습니다. 배포자에게 문의하세요.")
    st.stop()

genai.configure(api_key=api_key)

# 3. 룰북 PDF 텍스트 추출 함수
@st.cache_resource
def load_rulebook():
    try:
        # PDF 파일명은 업로드할 파일명과 정확히 일치해야 합니다.
        pdf_path = "rulebook.pdf" 
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except FileNotFoundError:
        return None

# 4. 룰북 로드
rulebook_text = load_rulebook()

if not rulebook_text:
    st.error("룰북 PDF 파일을 찾을 수 없습니다. (파일명: rulebook.pdf)")
    st.stop()

# 5. 모델 설정 (지침 주입)
system_instruction = f"""
너는 Far East Throwdown (FET) 국제 대회의 규정을 안내하는 친절하고 단호한 비서다.
아래의 [룰북 내용]을 기반으로 사용자의 질문에 한국어로 답변해라.

[최우선 수정 사항 - 룰북보다 우선함]
1. FEC 팀전 결선 진출 조건: 예선 참가 규모와 상관없이 무조건 '상위 20팀'만 진출한다. (25% 룰 삭제됨)
   - 조건: 팀원 전원 2026 Open 등록 필수, 지부 등록 필수.
2. FEC 개인전 결선 진출 조건: 쿼터파이널(Quarterfinals) 순위 '2,000등' 이내여야 한다. (1,000등 아님)
3. 룰북에 없는 내용은 '규정에 나와있지 않습니다. 운영진에게 문의해주세요.'라고 답해라. 추측하지 마라.

[룰북 내용]
{rulebook_text}
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-002", # 무료 티어에서 빠르고 성능 좋음
    system_instruction=system_instruction
)

# 6. 채팅 인터페이스
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! FET 룰북에 대해 무엇이든 물어보세요. (팀전 조건, 환불 규정 등)"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 답변 생성
    with st.chat_message("assistant"):
        with st.spinner("규정 확인 중..."):
            try:
                # 대화 히스토리 구성
                chat_history = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        chat_history.append({"role": "user", "parts": [msg["content"]]})
                    elif msg["role"] == "assistant":
                        chat_history.append({"role": "model", "parts": [msg["content"]]})
                
                # 마지막 질문만 보내는 것이 아니라 히스토리 기반으로 답변 (Gemini ChatSession 활용도 가능하나, 여기선 1회성 호출로 처리)
                # 단, context window가 크므로 전체 history를 context에 넣어도 무방
                
                response = model.generate_content(chat_history)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
