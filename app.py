import streamlit as st
import google.generativeai as genai
import os

# -----------------------------------------------------------------
# 1. 페이지 설정 및 제목
# -----------------------------------------------------------------
st.set_page_config(page_title="사내 업무 도우미", page_icon="🤖", layout="wide")
st.title("🤖 사내 업무 도우미 (Powered by Gemini)")

# -----------------------------------------------------------------
# 2. API 키 입력 (가장 중요!)
# -----------------------------------------------------------------
# Streamlit의 'Secrets' 기능을 사용하는 것이 정석입니다.
# (배포 전: st.sidebar.text_input("Gemini API Key", type="password")로 테스트)
try:
    # (배포 시) Streamlit Secrets에서 API 키를 불러옵니다.
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    # (로컬 테스트 시) Secrets에 키가 없으면 사이드바에서 직접 입력받습니다.
    api_key_input = st.sidebar.text_input("🔑 Gemini API Key를 입력하세요.", type="password")
    if api_key_input:
        genai.configure(api_key=api_key_input)
    else:
        st.error("Streamlit Secrets 또는 사이드바에 Gemini API Key를 설정해주세요.")
        st.stop() # API 키가 없으면 앱 실행 중지

# -----------------------------------------------------------------
# 3. AI 모델 선택 (유료 버전 사용)
# -----------------------------------------------------------------
# 모델 설정 (유료 버전을 쓰시니 'pro' 모델을 사용)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# -----------------------------------------------------------------
# 4. 직원별 업무 분리 (탭 UI 사용)
# -----------------------------------------------------------------

tab_A, tab_C, tab_B, tab_D = st.tabs([
    "A: 보고서 검토", 
    "C: 코드 오류 수정", 
    "B: 보고서 작성", 
    "D: 템플릿 제작"
])

# --- C직원: 코드 오류 고치는 사람 ---
with tab_C:
    st.header("C. 코드 오류 수정 👨‍💻")
    st.write("오류를 찾거나 개선할 코드를 아래에 붙여넣으세요.")
    
    code_input = st.text_area("코드 입력창:", height=300, key="code_input")
    
    if st.button("코드 분석 실행", key="code_button"):
        if not code_input:
            st.warning("코드를 입력해주세요.")
        else:
            prompt = f"""
            당신은 15년 차 시니어 개발자입니다. 
            다음 코드를 리뷰하고 3가지 항목으로 나눠서 설명해주세요.
            
            1.  **[버그/오류]**: 코드에 치명적인 오류나 버그가 있는지 찾아내고 수정안을 제시하세요.
            2.  **[개선 제안]**: 더 효율적이거나, 더 'Pythonic'한 코드 개선안을 제안하세요.
            3.  **[코드 설명]**: 이 코드가 어떤 역할을 하는지 주석을 달아서 설명해주세요.
            
            ---
            [입력된 코드]
            {code_input}
            """
            
            with st.spinner("Gemini가 코드를 분석 중입니다..."):
                response = model.generate_content(prompt)
                st.markdown("### 🔍 코드 분석 결과")
                st.markdown(response.text)

# --- A직원: 보고서 검토하는 사람 ---
with tab_A:
    st.header("A. 보고서 검토 📄")
    st.write("검토가 필요한 보고서 파일(.txt 또는 .md)을 업로드하세요.")
    
    uploaded_file = st.file_uploader("파일 선택", type=["txt", "md"], key="file_uploader")
    
    if uploaded_file is not None:
        try:
            # 파일 내용 읽기
            report_text = uploaded_file.getvalue().decode("utf-8")
            st.text_area("업로드된 파일 내용:", report_text, height=200, disabled=True)
            
            if st.button("보고서 검토 실행", key="report_button"):
                prompt = f"""
                당신은 꼼꼼한 기획팀장입니다. 
                아래 보고서 내용을 검토하고, [맞춤법/오탈자], [논리적 오류], [더 나은 표현 제안] 3가지 항목으로 나눠서 피드백을 주세요.
                
                ---
                [보고서 원본]
                {report_text}
                """
                
                with st.spinner("Gemini가 보고서를 검토 중입니다..."):
                    response = model.generate_content(prompt)
                    st.markdown("### 📝 보고서 검토 결과")
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

# --- B직원: 보고서 쓰는 사람 ---
with tab_B:
    st.header("B. 보고서 초안 작성 ✍️")
    st.write("보고서 작성을 위해 필요한 핵심 키워드나 내용을 입력하세요.")
    
    report_topic = st.text_input("보고서 주제:")
    report_keywords = st.text_area("포함될 핵심 키워드/내용 (줄바꿈으로 구분):")
    
    if st.button("보고서 초안 생성", key="write_button"):
        if not report_topic or not report_keywords:
            st.warning("주제와 키워드를 모두 입력해주세요.")
        else:
            # 웹 서칭(G)을 활용하도록 프롬프트에 명시
            prompt = f"""
            당신은 전문 리서처입니다. Google 검색 기능을 활용하여 최신 정보를 찾아주세요.
            
            다음 주제와 키워드를 바탕으로 전문적인 보고서의 [개요/초안]을 작성해주세요.
            
            * 주제: {report_topic}
            * 핵심 키워드: {report_keywords}
            """
            
            with st.spinner("Gemini가 웹을 검색하고 초안을 작성 중입니다..."):
                # Gemini 유료 버전은 Google 검색이 기본 연동되어 있습니다.
                response = model.generate_content(prompt)
                st.markdown("### 📑 보고서 초안")
                st.markdown(response.text)

# --- D직원: 템플릿 양식 제작 ---
with tab_D:
    st.header("D. 템플릿 양식 제작 📋")
    template_request = st.text_input("어떤 템플릿(양식)이 필요하신가요?")
    
    if st.button("템플릿 생성", key="template_button"):
        if not template_request:
            st.warning("템플릿 요청 사항을 입력해주세요. (예: 신규 프로젝트 기획안)")
        else:
            prompt = f"""
            요청받은 {template_request}을 위한 전문적인 문서 템플릿(양식)을 Markdown 형식으로 만들어주세요. 
            [주요 항목]과 [각 항목에 들어가야 할 내용 예시]를 포함해야 합니다.
            """
            with st.spinner("Gemini가 템플릿을 생성 중입니다..."):
                response = model.generate_content(prompt)
                st.markdown(f"### 📄 {template_request} 템플릿")
                st.markdown(response.text)
