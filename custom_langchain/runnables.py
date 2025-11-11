def fetch_curriculum_data() -> str:
    db: Session = next(get_db())

    try:
        results: List[Curriculum] = db.query(Curriculum).all()

    finally:
        db.close()

    output_lines = ["학년,과목,대단원번호,대단원,중단원번호,중단원,소단원번호,소단원"]

    for item in results:
        line = f"{item.grade},{item.subject},{item.no_main_chapter},{item.main_chapter},{item.no_sub_chapter},{item.sub_chapter},{item.no_lesson_chapter},{item.lesson_chapter}"

        output_lines.append(line)

    return "\n".join(output_lines)

def fetch_subject_intent_data() -> str:
    db: Session = next(get_db())

    try:
        results: List[SubjectUnit] = db.query(SubjectUnit).all()

    finally:
        db.close()

    output_lines  = ["수행과정, 성취기준, 성취기준해설"]
    
    for item in results:
        line = f"{item.sector}, {item.intent}, {item.intent_exp}"

        output_lines.append(line)

    return "\n".join(output_lines)

def get_grade_subject(input: dict) -> List[HumanMessage]:
    file_data = input["file_data"]

    # passthrough로 전달받은 인자
    curriculum_data = input["curriculum_data"]

    system_prompt = """
        당신은 교육 콘텐츠 분석가입니다.
        첨부된 파일의 내용은 분석하여 다음 문제가 어떤 커리큘럼에 대응하는지 json 형식으로 추출해주세요.
    """

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                    ----
                    커리큘럼 정보:
                    {curriculum_data}
                    ----
                """
            }
        ]
    )