import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# --- 백엔드 설정 ---
# Docker 환경에서는 서비스명으로 접근, 로컬 개발시에는 localhost 사용
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 문제 분석 서비스",
    page_icon="🤖",
    layout="wide"
)

# --- 세션 상태 초기화 ---
# 'analysis_history' : 사이드바에 표시될 분석 내역 리스트
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

# 'current_view' : 현재 메인 화면에 표시할 내용 (기본값 'upload')
# 'upload' 이면 업로드 화면, 다른 값(timestamp)이면 해당 분석 결과
if "current_view" not in st.session_state:
    st.session_state.current_view = "upload"

# =================================================================
# 헬퍼 함수 (개별 문제 결과 표시)
# =================================================================
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
    st.write(f"**키워드:** `{'`, `'.join(metadata.get('keywords', []))}`")
    st.markdown("---")
    
    # 교육과정 및 출제 의도
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 추천 교육과정")
        # (표시 로직은 이전 코드와 동일 - 간결성을 위해 일부 생략)
        cur1 = metadata.get('suggested_curriculum_1', {})
        if cur1: st.info(f"추천 1: {cur1.get('main_chapter_1', 'N/A')}")
        cur2 = metadata.get('suggested_curriculum_2', {})
        if cur2: st.info(f"추천 2: {cur2.get('main_chapter_2', 'N/A')}")
        
    with col2:
        st.subheader("🎯 출제 의도")
        # (표시 로직은 이전 코드와 동일 - 간결성을 위해 일부 생략)
        int1 = metadata.get('intent_1', {})
        if int1: st.markdown(f"**1. 영역:** {int1.get('sector_1', 'N/A')}")
        int2 = metadata.get('intent_2', {})
        if int2: st.markdown(f"**2. 영역:** {int2.get('sector_2', 'N/A')}")

    with st.expander("전체 응답 JSON 보기"):
        st.json(result_data)

# =================================================================
# 헬퍼 함수 (시험지 결과 표시)
# =================================================================
def display_exam_results(item):
    """시험지 분석 결과를 화면에 표시하는 함수"""
    st.header(f"📄 시험지 분석 결과")
    st.markdown(f"**파일명:** {item['file_name']}")
    
    exam_id = item.get("result", {}).get("exam_id")
    if not exam_id:
        st.error("시험지 ID를 찾을 수 없습니다.")
        return

    st.info(f"요청된 시험지 ID: **{exam_id}**")

    # GET /exam API 호출
    with st.spinner(f"'{exam_id}' 시험지의 상세 분석 데이터를 조회 중입니다..."):
        try:
            params = {"exam_id": exam_id}
            response = requests.get(f"{BACKEND_URL}/exam", params=params)
            
            if response.status_code == 200:
                st.success("상세 분석 데이터 조회 성공!")
                exam_data = response.json()
                
                # --- 데이터 시각화 영역 ---
                st.subheader("📊 기초 통계 데이터 (예시)")
                
                # (백엔드 응답이 확정되면 이 부분을 수정해야 합니다)
                # (예시 데이터 구조)
                # exam_data = {
                #     "total_problems": 25,
                #     "average_difficulty": 3.5,
                #     "problems_by_subject": {"수학I": 10, "수학II": 15},
                #     "problem_list": [
                #         {"id": "p1", "subject": "수학I", "difficulty": 3},
                #         {"id": "p2", "subject": "수학II", "difficulty": 4},
                #     ]
                # }

                col1, col2 = st.columns(2)
                col1.metric("총 문항 수", exam_data.get("total_problems", "N/A"))
                col2.metric("평균 난이도 (예상)", exam_data.get("average_difficulty", "N/A"))
                
                # 예시: 과목별 문항 수 (Bar chart)
                if "problems_by_subject" in exam_data:
                    st.subheader("과목별 문항 수")
                    df_subject = pd.DataFrame(
                        exam_data["problems_by_subject"].items(), 
                        columns=["과목", "문항 수"]
                    )
                    st.bar_chart(df_subject.set_index("과목"))

                # 예시: 문항 리스트 (DataFrame)
                if "problem_list" in exam_data:
                    st.subheader("개별 문항 상세 (DB 조회 결과)")
                    df_problems = pd.DataFrame(exam_data["problem_list"])
                    st.dataframe(df_problems, use_container_width=True)

                with st.expander("전체 응답 JSON 보기 (GET /exam)"):
                    st.json(exam_data)
                    
            else:
                st.error(f"GET /exam 조회 실패 (Status {response.status_code})")
                st.json(response.json())
        except requests.ConnectionError:
            st.error("백엔드 서버에 연결할 수 없습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")

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
    else:
        file_type = ["pdf", "png", "jpg", "jpeg"]
        endpoint = "/exam"

    uploaded_file = st.file_uploader(
        f"분석할 {analysis_type} 파일을 업로드하세요.",
        type=file_type
    )

    if st.button("분석 요청하기"):
        if uploaded_file:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            # 고유 ID로 사용될 타임스탬프
            item_id = datetime.now().isoformat()
            
            # 새 분석 내역 아이템 생성
            new_item = {
                "id": item_id,
                "file_name": uploaded_file.name,
                "type": analysis_type,
                "status": "processing", # 상태: 처리중
                "result": None
            }
            
            # 개별 문제일 경우, 이미지도 저장
            if analysis_type == "개별 문제 분석":
                new_item["uploaded_image"] = uploaded_file.getvalue()

            # 히스토리 목록의 맨 앞에 추가 (최신순)
            st.session_state.analysis_history.insert(0, new_item)
            
            # API 요청
            with st.spinner(f"{uploaded_file.name} 파일 분석 요청 중..."):
                try:
                    response = requests.post(f"{BACKEND_URL}{endpoint}", files=files)
                    
                    # 히스토리에서 방금 추가한 아이템 찾기
                    target_item = next(item for item in st.session_state.analysis_history if item["id"] == item_id)
                    
                    if response.status_code == 200:
                        target_item["status"] = "completed" # 상태: 완료
                        
                        if analysis_type == "개별 문제 분석":
                            target_item["result"] = response.json()
                        else: # 시험지 분석
                            # POST /exam 은 exam_id만 반환함
                            target_item["result"] = {"exam_id": response.json()}
                        
                        st.success(f"'{uploaded_file.name}' 분석 요청 성공!")
                        # 분석 완료 후, 해당 결과 페이지로 바로 이동
                        st.session_state.current_view = item_id
                        st.rerun() # 화면 즉시 새로고침
                        
                    else:
                        target_item["status"] = "failed" # 상태: 실패
                        target_item["result"] = response.json()
                        st.error(f"분석 실패 (Status {response.status_code})")
                        st.json(response.json())

                except requests.ConnectionError:
                    st.error("백엔드 서버에 연결할 수 없습니다.")
                    # 히스토리에서 아이템 상태 '실패'로 변경
                    target_item = next(item for item in st.session_state.analysis_history if item["id"] == item_id)
                    target_item["status"] = "failed"
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    target_item = next(item for item in st.session_state.analysis_history if item["id"] == item_id)
                    target_item["status"] = "failed"
            
            # 사이드바 업데이트를 위해 새로고침
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
                # 버튼 클릭 시, 메인 화면을 해당 아이템의 결과로 변경
                st.session_state.current_view = item_id
                st.rerun()
            elif status == "processing":
                st.sidebar.warning("아직 분석 중입니다...")
            else:
                st.sidebar.error("분석에 실패한 항목입니다.")
                # 실패 시에도 결과 확인을 위해 뷰 변경
                st.session_state.current_view = item_id 
                st.rerun()

# =================================================================
# 메인 콘텐츠 렌더링 (동적 변경)
# =================================================================
if st.session_state.current_view == "upload":
    show_upload_page()
else:
    # 'current_view'에 저장된 ID로 히스토리에서 해당 아이템 찾기
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
        # 혹시 모를 오류 방지
        st.warning("선택된 내역을 찾을 수 없습니다. 업로드 화면으로 돌아갑니다.")
        st.session_state.current_view = "upload"
        st.rerun()