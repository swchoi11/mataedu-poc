import os
import re
from config import config
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
import fitz
from typing import Generator, List
import cv2
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field, model_validator
from typing import List, Tuple

def pdf_to_image_generator(pdf_path: str, dpi: int =300) -> Generator[Image.Image, None, None]: 
    try: 
        pages = fitz.open(pdf_path)

        for page_num in range(pages.page_count):
            page = pages.load_page(page_num)

            # pix맵 생성
            pix = page.get_pixmap(dpi=dpi)

            # pil 이미지로 변환
            try:
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                yield img
            except Exception as e:
                print(e)
                raise
    except Exception as e:
        print(e)
        raise
    finally:
        if pages:
            pages.close()


# ocr_engine = PaddleOCR(lang="korean",
#                         use_textline_orientation=True,
#                         text_det_limit_side_len=6000)
# def find_question_anchors(pil_image):
#     if not ocr_engine:
#         print("ocr 엔진이 초기화되지 않았습니다")
#         return []

#     # 정규식: 공백으로 시작할 수 있고, 숫자(1개 이상)로 시작하며, 점(.)으로 끝남
#     # 예: "1.", " 2.", "15."
#     question_regex = re.compile(r'^\s*(\d+)[.,]')

#     anchors = []

#     try:
#         img_np = np.array(pil_image.convert("RGB"))
#         img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#         result = ocr_engine.predict(img_np)

#         # print(result)

#         if not result and not result[0]:
#             print("ocr 결과가 비어있습니다. ")
#             return []

#         result = result[0]

#         texts = result.get("rec_texts", [])
#         polys = result.get("rec_polys", [])

#         print("\n" + "="*30)
#         print(f"[DEBUG] OCR이 현재 페이지에서 찾은 텍스트 목록:")
#         print(texts) # 모든 텍스트를 리스트로 통째로 출력
#         print("="*30 + "\n")


#         for poly, text in zip(polys, texts):
#             match = question_regex.match(text)
#             print(f"[DEBUG] 검사 중인 텍스트: '{text}'")

#             if match:
#                 question_num = match.group(1)

#                 anchor_point = [int(poly[0][1]), int(poly[0][1])] # 왼쪽 상단

#                 anchor_info = {
#                     "q_num": question_num,
#                     "anchor_point": anchor_point
#                 }

#                 anchors.append(anchor_info)
#         if not anchors and texts:
#             print('텍스트는 있는데 정규식이랑 일치하는게 없음')
#         return anchors

#     except Exception as e:
#         print(e)


# from PIL import Image, ImageDraw # ImageDraw가 필요합니다
# import cv2
# import numpy as np
# import os
# import re

# # (ocr_engine는 이미 정의되었다고 가정)
# # (pdf_to_pil_generator 함수도 이미 정의되었다고 가정)

# pdf_path = "./data/기출문제/2023-3-고1-수학.pdf"
# 
# image_generator = pdf_to_image_generator(pdf_path)
# for i, pil_image in enumerate(image_generator):
    # result = find_question_anchors(pil_image)
    # print(i)
    # print(result)
    # print("------")


# image_generator = pdf_to_image_generator(pdf_path, dpi=300) # 고해상도 유지
# output_dir = "debug"
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
# for i, pil_image in enumerate(image_generator):
#     page_num = i + 1
#     print(f"\n--- 페이지 {page_num} 처리 시작 ---")

#     # 1. find_question_anchors 대신 새 디버깅 함수 호출
#     image_with_boxes = draw_all_ocr_boxes(pil_image)

#     # 2. 박스가 그려진 최종 이미지를 파일로 저장
#     output_filename = os.path.join(output_dir, f"ocr_all_boxes_page_{page_num}.png")
#     image_with_boxes.save(output_filename)
#     print(f"--- 페이지 {page_num} -> '{output_filename}' 저장 완료 ---")

# print(f"\n디버깅 이미지가 '{output_dir}' 폴더에 저장되었습니다.")

#===================


class QuestionBox(BaseModel):
    """
    개별 문항의 정보와 위치를 담는 스키마.
    좌표는 (0.0 ~ 1.0) 사이의 상대 좌표입니다.
    """
    question_number: str = Field(
        description="문제 번호 (예: '1', '9번', '서술형 2')"
    )
    y_min: float = Field(
        description="영역의 상단(Top) Y 상대 좌표 (0.0~1.0)"
    )
    x_min: float = Field(
        description="영역의 좌측(Left) X 상대 좌표 (0.0~1.0)"
    )
    y_max: float = Field(
        description="영역의 하단(Bottom) Y 상대 좌표 (0.0~1.0)"
    )
    x_max: float = Field(
        description="영역의 우측(Right) X 상대 좌표 (0.0~1.0)"
    )
class QuestionList(BaseModel):
    questions: List[QuestionBox] = Field(
        description = "페이지에서 감지된 모든 개별 문항의 리스트"
    )

    @model_validator(mode='before')
    @classmethod
    def wrap_list_in_dict(cls, values):
        """
        llm이 리스트를 반환한 경우 딕셔너리로 변환
        """
        if isinstance(values, list):
            return {"questions": values}
        return values


from langchain_core.output_parsers import PydanticOutputParser
output_parser = PydanticOutputParser(pydantic_object=QuestionList)


def get_poly(input: dict) -> List[HumanMessage]:
    format_instructions = output_parser.get_format_instructions()
    system_prompt = f"""
    당신은 전문적인 문서 레이아웃 분석가입니다.
    첨부된 이미지는 2단(two-column)으로 구성될 수 있는 시험문제지입니다.
    시험문제지에는 분석해야하는 개별 문항과 함께, 시험 과목, 과정과 관련된 다른 정보들, 페이지 번호 등이 함께 존재합니다. 

    당신의 임무는 페이지에 있는 **모든 개별 문항**만을 식별하는 것입니다.
    다른 텍스트나 설명 없이, 반드시 다음 JSON 스키마를 주수하는 단일 JSON 객체만을 반환해야합니다.
    {format_instructions}
    """

    message = HumanMessage(
        content = [
            {"type": "text",
            "text":"이 이미지에서 모든 문제 영역을 분석하고, 요청한 포맷 지침({format_instructions})에 정확히 맞춰 JSON을 반환해주세요."},
            {
                "type": "image_url",
                "image_url": {"url": file_data}

            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]


llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)

from components import encode_image
file_data = encode_image(file_path)

poly_extraction  = (
    RunnableLambda(get_poly)
    | llm
    | output_parser
)
input_dict = {
    "file_data": file_data
}
result = poly_extraction.invoke(input_dict)


pil_img = Image.open(file_path)

image_width, image_height = pil_img.size
buffer_w = image_width * 0.01
buffer_h = image_height * 0.01

output_crop_dir = "debug"

cropped_images = []

for q_box in result.questions:
    x_min_pixel = max(0, int(q_box.x_min * image_width) - buffer_w)
    x_max_pixel = min(image_width, int(q_box.x_max * image_width) + buffer_w)
    y_min_pixel = max(0, int(q_box.y_min * image_height) - buffer_h)
    y_max_pixel = min(image_height, int(q_box.y_max * image_height) + buffer_h)

    crop_box = (x_min_pixel, y_min_pixel, x_max_pixel, y_max_pixel)

    try:
        cropped_q_image = pil_img.crop(crop_box)
        
        # 2-4. 크롭된 이미지 저장 (디버깅 및 사용 목적)
        # 파일명에 문제 번호 포함
        output_filename = os.path.join(output_crop_dir, f"q_{q_box.question_number}_crop.png")
        cropped_q_image.save(output_filename)
        
        print(f"문제 {q_box.question_number} 크롭 및 저장 완료: {output_filename}")
        cropped_images.append({
            "question_number": q_box.question_number,
            "image": cropped_q_image,
            "path": output_filename
        })

    except Exception as e:
        print(f"문제 {q_box.question_number} 크롭 중 오류 발생: {e}")
        print(f"  - 사용된 크롭 박스: {crop_box}")
