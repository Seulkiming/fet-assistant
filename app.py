import streamlit as st
import google.generativeai as genai

# API 키 설정 (Secrets에서 가져오기)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key="AIzaSyD3HYCDN58Aet5q0PlgoxmzyP8yigeRFXk")
else:
    st.error("API 키가 없습니다.")
    st.stop()

st.title("🔍 모델 진단 도구")

try:
    st.write("내 API 키로 사용할 수 있는 모델 목록:")
    
    # 사용 가능한 모델 리스트 조회
    models = genai.list_models()
    
    found_flash = False
    for m in models:
        # 생성(generateContent) 기능이 있는 모델만 출력
        if 'generateContent' in m.supported_generation_methods:
            st.code(f"이름: {m.name}")
            if "flash" in m.name:
                found_flash = True

    if found_flash:
        st.success("✅ 'flash' 모델이 목록에 있습니다! 라이브러리 문제는 해결된 듯합니다.")
    else:
        st.error("❌ 'flash' 모델이 안 보입니다. requirements.txt 버전을 더 높이거나 'gemini-pro'를 써야 합니다.")

except Exception as e:
    st.error(f"에러 발생: {e}")
