# 📁 app.py
import streamlit as st
import tempfile
import os
from utils.pdf_parser import extract_text_from_pdf
from utils.gpt_helper import summarize_text_to_slides, parse_structured_slides
from utils.ppt_generator import insert_structured_content

st.set_page_config(page_title="📊 PDF → PPT 슬라이드 생성기")
st.title("🧠 GPT 기반 ppt 슬라이드 자동 생성")

pdf_file = st.file_uploader("📄PDF 파일 업로드", type="pdf")
template_path = "templates/atd_template.pptx"
prompt_input = st.text_area("✍️ GPT 프롬프트", """
당신은 교육 및 연구 내용을 한국어로 요약하고 시각화하는 슬라이드 전문가입니다.
지금부터 제공하는 영어 논문 PDF의 내용을 기반으로 다음 기준에 따라 PPT 콘텐츠를 구성해주세요:
---
-첫 슬라이드는 논문의 개요를 담습니다. 논문의 주제, 목적, 연구 방법, 주요 키워드를 요약해 주세요.
-이후 슬라이드에는 각 장(예: Introduction, Methods, Results, Discussion)의 핵심 내용을 간단한 제목(키워드)과 함께 요약해 주세요.
-모든 텍스트는 한국어로 번역하여 작성합니다.
-'영문 제목'과 그에 대응하는 '국문 제목'을 논문 제목 기준으로 작성해주세요.
-마지막 슬라이드는 이 논문이 국내 연구자나 실무자에게 줄 수 있는 시사점을 간결하게 정리해 주세요.
---

출력 형식 예시:

[슬라이드 1]
영문제목: A Study on XYZ for Learning Analytics
국문제목: 학습 분석을 위한 XYZ 연구
키워드: 연구 개요
내용: 본 논문은 XYZ 접근법을 활용한 학습 분석 기법을 제안한다. 목적은 데이터 기반의 학습 개선 전략을 수립하는 데 있으며, 실험을 통해 그 효과를 검증하였다.

[슬라이드 3]
영문 제목: A Study on XYZ for Learning Analytics
국문 제목: 학습 분석을 위한 XYZ 연구
키워드: 주요 결과
내용: 실험 결과 XYZ 기법은 학습자의 참여도 예측에 있어 기존 방법보다 정확도가 높았다. 특히 학습 초기 단계에서의 실시간 피드백 제공 가능성도 확인되었다.

""")

if st.button("🔄 슬라이드 생성") and pdf_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(pdf_file.read())
        pdf_text = extract_text_from_pdf(tmp.name)

    with st.spinner("🤖 GPT가 내용을 요약하고 있습니다..."):
        gpt_response = summarize_text_to_slides(pdf_text, prompt_input)
        st.session_state["gpt_response"] = gpt_response
        slides_data = parse_structured_slides(gpt_response)

    with st.spinner("🧩 슬라이드에 내용 삽입 중..."):
        prs = insert_structured_content(template_path, slides_data)
        output_path = "generated_slides.pptx"
        prs.save(output_path)

    st.success("✅ 슬라이드 생성 완료!")
    with open(output_path, "rb") as f:
        st.download_button("📥 PPTX 파일 다운로드", f, file_name="ATD_Debriefing.pptx")

if "gpt_response" in st.session_state:
    st.text_area("📋 GPT 응답 미리보기", st.session_state["gpt_response"], height=400)
