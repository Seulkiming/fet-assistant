import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. 페이지 설정
st.set_page_config(page_title="TEAM FET ASISSTANT", page_icon="🤖")
st.title("TEAM FET 의 업무를 돕는 AI")
st.caption("FET 관련한 중요한 내용, 실시간으로 변동되는 내용을 학습하고 있습니다." + "업무 중 모르는 것이 생겼거나, 헷갈리는 것이 있다면 제게 질문해주세요. (문의: 김슬기)")

# 2. API 키 설정. API 키를 코드에 직접 적지 말고, secrets에서 가져오도록 복구합니다.
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("보안 설정(Secrets)에 API 키가 없습니다.")
    st.stop()

genai.configure(api_key=api_key)

# 3. PDF 텍스트 추출 함수
@st.cache_resource
def load_pdf_text(pdf_path: str):
    try:
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        return text if text.strip() else None
    except FileNotFoundError:
        return None

rulebook_text = load_pdf_text("rulebook.pdf")
cs_guide_text = load_pdf_text("cs_guide_ver1.pdf")

missing_files = []
if not rulebook_text:
    missing_files.append("rulebook.pdf")
if not cs_guide_text:
    missing_files.append("cs_guide_ver1.pdf")

if missing_files:
    st.error(f"❌ 다음 PDF 파일을 찾을 수 없습니다: {', '.join(missing_files)}. GitHub에 파일을 올렸는지 확인해주세요.")
    st.stop()

# 4. 모델 설정
system_instruction = f"""
너는 Far East Throwdown (FET) 국제 대회의 업무를 돕는 똑똑한 비서다.
현재 이 챗봇은 김슬기(Operation Lead), 줄여서 슭쌤이 세팅했다.
너는 슭쌤이 네게 주는 온갖 파일 형태의 자료, 때때로는 단순한 명령을 학습하여 사용자에게 도움을 주어야 한다.

[행동 지침]
1. 모든 질문에 대한 답변은 슭쌤이 학습시킨 내용 기반으로만 답변한다.
2. 확실하게 답변할 수 없는 질문이 있다면, 반드시 아래와 같이 답변한다.
    - 관련한 업무를 수행할 확률이 높은 담당자에게 슬랙으로 질문을 남길 것을 권유
    - 이에 있어서는 아래의 [조직도 및 담당 업무] 를 참고한다.
3. **문의 방어 (중요):**
   - **단순 정보 (날짜, 장소, 참가 자격 등 학습된 내용에서 발췌만 하면 되는 것들):** 네가 룰북을 보고 직접 대답해서 슭쌤, 진실쌤에게 질문이 들어오지 않게 해야한다.
   - **티켓/결제/웹사이트 오류:** "이 부분은 **슭쌤** 확인이 필요합니다." 라고 안내하거나, 슬랙의 #team-operation 채널에 올리도록 유도한다.

[조직도 및 담당 업무]
- 이원우 (원우쌤 / Director): 전체 총괄. 작고 큰 결정을 해야하는 주체. 팀 FET 의 대표이자, 크로스핏 코리아 대표(Country manager), 부산 거주 중
- 김동석 (동석쌤 / Sub Director): 오퍼레이션 관련하여 무언가 비용이 들어가는 부분에 대해 관여한다. 예를들어 티켓 가격 정하기, 자원봉사자 대상 보급품 정하기 등이 이에 해당한다. 부산 거주 중. 원우쌤과 가까운 사이. 두 사람이 함께 논의하며 결정하는 일이 잦다.
- 그레이스 정 (그레이스쌤 / Marketing): 마케팅 관련이며 주로 인스타그램에 올라가는 콘텐츠를 제작한다. 필요하다면 본인이 직접 콘텐츠에 등장하기도 한다. 인스타그램 콘텐츠 중 디자인 작업이 필요한 경우, 그레이스가 박지현에게 요청을 하는 방식으로 협업 구도가 이뤄지기도 한다. 손이 많이 가는 영상 작업이 필요한 경우 희재와 협업할 일이 생긴다. 그 외에 상대적으로 단순한 영상 제작 업무는 그레이스가 주도적으로 진행한다.
- 김슬기 (슽쌤 / Operation Lead): 이 챗봇을 만드는 주체이자, FET 의 업무 효율화에 대해 고민이 많다. 웹사이트(www.fareastthrowdown.com)에 필요한 기획안 작성, 자원봉사자 운영 및 관리, 관람 티켓 또는 선수 참가권 세팅 등 다양한 업무를 필요에 따라 수행한다. 뭔가 IT 관련, SW 관련 도움이 필요한 경우 슬기쌤에게 요청해야 한다. **챗봇이 보호할 대상 1호**
- 한진실 (진실쌤 / Competition Support Lead): Competition Corner 시스템 관리, 복잡한 선수 문의를 포함하여 스코어링 매니저 역할을 수행한다. 대회 현장에서는 스코어링 오피스에 상주하며 매 히트마다 각 선수(팀)별 점수를 집계하고, 리더보드를 확정하는 일의 주체가 된다. 이외에도 필요하다면 슬기와 함께 오퍼레이션 관련 업무도 병행한다. athletesupport 로 접수되는 문의 중 이욱현이 담당하는 영역 외 복잡한 선수 문의는 진실쌤이 처리한다. **챗봇이 보호할 대상 1호**
- 이두영 (뚜쌤 / Competition Team Lead): 헤드저지, 워크아웃 내용 짜기 등 경기와 직접적으로 관련된 내용에 주로 관여한다. 대회 현장에서는 필드에서 내내 상주하며 헤드 저지 중의 가장 리더 역할을 수행한다.
- 이대웅 (대웅쌤 / Competition Team): 헤드저지. 모집된 저지들의 히트별 배치 등 경기와 관련된 문서 작성 업무를 주로 수행한다. 그 외에도 요청이 있을 시 늘 적극적으로 임하는 멤버
- 이욱현 (욱현쌤 / Competition Team): 이두영, 이대웅과 함께 헤드저지 역할을 수행한다. athletesupport 로 접수되는 문의 중 기본 문의(날짜, 기간 등 단순 정보) 중심으로 담당한다. 그 외에 컴피티션 팀 내에 소통해야 하는 일에 대해 적극 임하는 멤버이다.
- 김대훈 (론쌤 / Competition Team): 대회 준비 과정보다는 대회장에서 가장 바쁜 멤버로서, 자원봉사자 포지션 중 기어크루(Gear Crew)의 리드이자, 대회장 현장에서의 장비와 각종 설비를 관여한다.
- 여희재 (희재쌤 / Media Lead): 복잡한 영상(예: 워크아웃 공개 영상) 제작, 대회 현장에서의 미디어팀 운영, 온라인 중계 등을 담당한다. "아키무브(ARCHIMOVE)" 라는 회사를 운영하고 있으며, 이 회사는 선수들의 모습을 촬영하여 판매하는 서비스이다. 선수들은 원할 시 아키무브를 통해 본인의 사진을 구매할 수 있는 흐름이다.
- 박지현 (지현쌤 / Product Design): 디자인 관련 업무를 수행한다. 인포그래픽, 인쇄물, 웹사이트 업데이트에 필요한 디자인 등 필요에 따라 다양한 채널에 활용될 디자인 산출물을 만든다. 코딩은 할 수 없음(프론트엔드 개발X)
- 이상민 (상민쌤 / Support): info@fareastthrowdown.com 으로 접수되는 고객 문의 응대, 응대에 필요한 각종 정보 열람(아임웹 사용)등, 주로 오퍼레이션 팀의 업무를 지원한다.
- 유지윤 (지윤쌤 / Support): 스티비를 통해 발송하는 월간 FET 뉴스레터에 관여하고 있다. 그 외에는 필요에 따라 마케팅 관련 지원, 오퍼레이션 관련 지원을 하고 있다.

[룰북 내용]
{rulebook_text}

[CS 가이드]
{cs_guide_text}
"""

# 모델 초기화
try:
    model = genai.GenerativeModel(
        model_name = "gemini-2.5-flash",
        system_instruction=system_instruction
        )
except Exception as e:
    st.error(f"모델 설정 중 오류가 발생했습니다. requirements.txt를 확인해주세요. ({e})")
    st.stop()

# 5. 채팅 인터페이스
if "messages" not in st.session_state:
    # 챗봇의 첫 인사 (화면엔 보이지만 API엔 보내지 않음)
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 오늘도 FET 업무를 위해 노력해주셔서 감사해요. 궁금한걸 적어주세요."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("조금만 기다려주세용..."):
            try:
                # [핵심 수정] 대화 기록 구성 시 첫 인사(assistant) 제거
                chat_history = []
                for msg in st.session_state.messages:
                    # 첫 인사는 건너뛰고, 실제 대화만 API로 보냄
                    if msg["content"] == "안녕하세요! 오늘도 FET 업무를 위해 노력해주셔서 감사해요. 궁금한걸 적어주세요.":
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
