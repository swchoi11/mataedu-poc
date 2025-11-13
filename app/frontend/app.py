import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO # PDF 처리용

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 문제 분석 서비스",
    page_icon="🤖",
    layout="wide"
)

# --- 세션 상태 초기화 ---
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "current_view" not in st.session_state:
    st.session_state.current_view = "upload"

def display_problem_results(item):
    """개별 문제 분석 결과를 화면에 표시하는 함수"""
    st.header(f"🧩 개별 문제 분석 결과")
    st.markdown(f"**파일명:** {item['file_name']}")

    # 1. 업로드한 이미지 표시
    if item.get("uploaded_image"):
        st.image(item["uploaded_image"], caption="업로드된 문제 이미지", width=400)

    # 2. API 응답 결과 표시
    result_data = item.get("result", {})
    metadata = result_data.get("metadata", {})
    print(result_data)
    print(metadata)

    st.subheader(f"분석 ID: {result_data.get('problem_id')}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("학년", metadata.get('grade', 'N/A'))
    col2.metric("과목", metadata.get('subject', 'N/A'))
    col3.metric("문항 유형", metadata.get('item_type', 'N/A'))
    
    diff_data = metadata.get('difficulty', {})
    col1.metric("난이도", diff_data.get('difficulty', 'N/A'))
    col2.metric("배점", metadata.get('points', 'N/A'))
    st.caption(f"난이도 근거: {diff_data.get('difficulty_reason', 'N/A')}")
    
    st.text_area(
        "문제 내용 (인식 결과)", 
        metadata.get('content', '인식된 내용 없음'), 
        height=150
    )
    st.write(f"**키워드:** {metadata.get('keywords','')}")
    st.markdown("---")
    
    # 교육과정 및 출제 의도
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 추천 교육과정")
        cur1 = metadata.get('suggested_curriculum_1', {})
        if cur1: 
            st.info(f"추천 1: {cur1.get('main_chapter', '')}>{cur1.get('sub_chapter', '')}>{cur1.get('lesson_chapter', '')}")
            st.info(f"추천 1의 근거: {cur1.get('reason','N/A')}")
        cur2 = metadata.get('suggested_curriculum_2', {})
        if cur2: 
            st.info(f"추천 2: {cur2.get('main_chapter', '')}>{cur2.get('sub_chapter', '')}>{cur2.get('lesson_chapter', '')}")
            st.info(f"추천 2의 근거: {cur2.get('reason','N/A')}")


    with col2:
        st.subheader("🎯 출제 의도")
        # (표시 로직은 이전 코드와 동일 - 간결성을 위해 일부 생략)
        int1 = metadata.get('intent_1', {})
        if int1: st.markdown(f"**1. 영역:** {int1.get('sector', 'N/A')}")
        int2 = metadata.get('intent_2', {})
        if int2: st.markdown(f"**2. 영역:** {int2.get('sector', 'N/A')}")

    with st.expander("전체 응답 JSON 보기"):
        st.json(result_data)

def display_exam_results(item):
    """시험지 분석 결과를 화면에 표시하는 함수"""
    st.header(f"📄 시험지 분석 결과")
    st.markdown(f"**파일명:** {item['file_name']}")
    
    # 두 개의 단으로 나누기
    col_image, col_analysis = st.columns([1, 2]) # 이미지 컬럼을 1, 분석 결과 컬럼을 2 비율로 설정

    with col_image:
        st.subheader("원본 시험지")
        uploaded_image_data = item.get("uploaded_image")
        file_name = item.get("file_name", "exam_file")
        file_extension = os.path.splitext(file_name)[1].lower()

        if uploaded_image_data:
            if file_extension in ['.png', '.jpg', '.jpeg']:
                st.image(uploaded_image_data, caption="업로드된 시험지 이미지", use_column_width=True)
            elif file_extension == '.pdf':
                st.info("PDF 파일은 직접 표시하기 어렵습니다. 다운로드하여 확인하세요.")
                st.download_button(
                    label=f"⬇️ '{file_name}' 다운로드",
                    data=uploaded_image_data,
                    file_name=file_name,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("지원하지 않는 파일 형식입니다. 원본 파일을 표시할 수 없습니다.")
        else:
            st.info("업로드된 원본 파일이 없습니다.")

    with col_analysis:
        exam_id = item.get("result", {}).get("exam_id")
        if not exam_id:
            st.error("시험지 ID를 찾을 수 없습니다.")
            return

        st.info(f"요청된 시험지 ID: **{exam_id}**")

        with st.spinner(f"'{exam_id}' 시험지의 상세 분석 데이터를 조회 중입니다..."):
            try:
                params = {"exam_id": exam_id}
                response = requests.get(f"{BACKEND_URL}/exam", params=params)
                
                if response.status_code == 200:
                    st.success("상세 분석 데이터 조회 성공!")
                    exam_data = response.json()
                    
                    st.subheader("📊 기초 통계 데이터")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("총 문항 수", f"{exam_data.get('total_problems', 'N/A')} 문제")
                    col2.metric("총 배점", f"{exam_data.get('total_points', 'N/A')} 점")
                    
                    avg_points = exam_data.get('average_points', 0)
                    col3.metric("평균 배점", f"{avg_points:.2f} 점")
                    
                    st.markdown("---")

                    st.subheader("📈 문항 특성 분포")
                    chart_col1, chart_col2, chart_col3 = st.columns(3)

                    with chart_col1:
                        st.markdown("##### 과목별 문항 수")
                        if "problems_by_subject" in exam_data and exam_data["problems_by_subject"]:
                            st.bar_chart(exam_data["problems_by_subject"])
                        else:
                            st.caption("데이터 없음")

                    with chart_col2:
                        st.markdown("##### 난이도별 문항 수")
                        if "problems_by_difficulty" in exam_data and exam_data["problems_by_difficulty"]:
                            st.bar_chart(exam_data["problems_by_difficulty"])
                        else:
                            st.caption("데이터 없음")
                            
                    with chart_col3:
                        st.markdown("##### 유형별 문항 수")
                        if "problems_by_type" in exam_data and exam_data["problems_by_type"]:
                            st.bar_chart(exam_data["problems_by_type"])
                        else:
                            st.caption("데이터 없음")

                    st.markdown("---")

                    if "problem_list" in exam_data:
                        st.subheader("📋 개별 문항 상세")
                        
                        df_problems = pd.DataFrame(exam_data["problem_list"])
                        
                        display_columns = [
                            'problem_id', 
                            'grade', 
                            'subject', 
                            'difficulty', 
                            'points', 
                            'item_type', 
                            'main_chapter_1', 
                            'keywords'
                        ]
                        
                        existing_columns = [col for col in display_columns if col in df_problems.columns]
                        
                        st.dataframe(df_problems[existing_columns], use_container_width=True)

                    with st.expander("전체 응답 JSON 보기 (GET /exam)"):
                        st.json(exam_data)
                        
                else:
                    st.error(f"GET /exam 조회 실패 (Status {response.status_code})")
                    st.json(response.json())
            except requests.ConnectionError:
                st.error(f"백엔드 서버({BACKEND_URL})에 연결할 수 없습니다.")
            except Exception as e:
                st.error(f"데이터 처리 중 오류 발생: {e}")
# =================================================================
# 헬퍼 함수 (업로드 페이지)
# =================================================================
def show_upload_page():
    """메인 화면의 파일 업로드 페이지를 렌더링"""
    st.header("🚀 새 분석 파일 업로드")

    analysis_type = st.radio(
        "분석 유형을 선택하세요:",
        ("개별 문제 분석", "시험지(기출) 분석"),
        horizontal=True
    )

    if analysis_type == "개별 문제 분석":
        file_type = ["png", "jpg", "jpeg"]
        endpoint = "/problem"
    else: # 시험지(기출) 분석
        file_type = ["pdf", "png", "jpg", "jpeg"] # PDF 추가
        endpoint = "/exam"

    uploaded_file = st.file_uploader(
        f"분석할 {analysis_type} 파일을 업로드하세요.",
        type=file_type
    )

    if st.button("분석 요청하기"):
        if uploaded_file:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            item_id = datetime.now().isoformat()
            
            new_item = {
                "id": item_id,
                "file_name": uploaded_file.name,
                "type": analysis_type,
                "status": "processing",
                "result": None,
                "uploaded_image": uploaded_file.getvalue() # 시험지 분석일 때도 원본 저장
            }
            
            # 히스토리 목록의 맨 앞에 추가 (최신순)
            st.session_state.analysis_history.insert(0, new_item)
            
            # API 요청
            with st.spinner(f"{uploaded_file.name} 파일 분석 요청 중..."):
                try:
                    response = requests.post(f"{BACKEND_URL}{endpoint}", files=files)
                    
                    target_item = next(item for item in st.session_state.analysis_history if item["id"] == item_id)
                    
                    if response.status_code == 200:
                        target_item["status"] = "completed"
                        target_item["result"] = response.json() # 개별/시험지 모두 응답 저장 방식 통일
                        
                        st.success(f"'{uploaded_file.name}' 분석 요청 성공!")
                        st.session_state.current_view = item_id
                        st.rerun()
                        
                    else:
                        target_item["status"] = "failed"
                        target_item["result"] = response.json()
                        st.error(f"분석 실패 (Status {response.status_code})")
                        st.json(response.json())

                except requests.ConnectionError:
                    st.error("백엔드 서버에 연결할 수 없습니다.")
                    target_item = next(item for item in st.session_state.analysis_history if item["id"] == item_id)
                    target_item["status"] = "failed"
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    target_item = next(item for item in st.session_state.analysis_history if item["id"] == item_id)
                    target_item["status"] = "failed"
            
            st.rerun()
            
        else:
            st.warning("먼저 파일을 업로드해주세요.")

# =================================================================
# 사이드바 렌더링
# =================================================================
st.sidebar.title("🗂️ 분석 내역")
st.sidebar.markdown("---")

# "새로 업로드하기" 버튼
if st.sidebar.button("➕ 새로 업로드하기", use_container_width=True):
    st.session_state.current_view = "upload"
    st.rerun()

st.sidebar.markdown("---")

# 분석 내역 리스트 표시
if not st.session_state.analysis_history:
    st.sidebar.info("아직 분석 내역이 없습니다.")
else:
    for item in st.session_state.analysis_history:
        item_id = item["id"]
        file_name = item["file_name"]
        item_type = item["type"]
        status = item["status"]

        # 상태 아이콘
        if status == "completed":
            icon = "✅"
        elif status == "processing":
            icon = "⏳"
        else: # failed
            icon = "❌"
            
        # 사이드바에 버튼으로 표시
        if st.sidebar.button(
            f"{icon} {file_name} [{item_type.split(' ')[0]}]", 
            key=f"btn_{item_id}",
            use_container_width=True
        ):
            if status == "completed":
                st.session_state.current_view = item_id
                st.rerun()
            elif status == "processing":
                st.sidebar.warning("아직 분석 중입니다...")
            else:
                st.sidebar.error("분석에 실패한 항목입니다.")
                st.session_state.current_view = item_id 
                st.rerun()

# =================================================================
# 메인 콘텐츠 렌더링 (동적 변경)
# =================================================================
if st.session_state.current_view == "upload":
    show_upload_page()
else:
    item_to_display = next((item for item in st.session_state.analysis_history if item["id"] == st.session_state.current_view), None)
    
    if item_to_display:
        if item_to_display["status"] == "failed":
            st.error("분석에 실패했습니다. 백엔드 응답을 확인하세요.")
            st.json(item_to_display.get("result", {}))
        
        elif item_to_display["type"] == "개별 문제 분석":
            display_problem_results(item_to_display)
            
        elif item_to_display["type"] == "시험지(기출) 분석":
            display_exam_results(item_to_display)
    else:
        st.warning("선택된 내역을 찾을 수 없습니다. 업로드 화면으로 돌아갑니다.")
        st.session_state.current_view = "upload"
        st.rerun()