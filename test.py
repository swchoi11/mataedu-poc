import os
import re
from config import config
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

ocr_engine = PaddleOCR(use_angle_cls=True, lang="korean", det_limit_side_len = 6000)

from pdf2image import convert_from_path, pdfinfo_from_path

def pdf_to_image(pdf_path: str): 
    pdf_info = pdfinfo_from_path(pdf_path)
    total_pages = pdf_info["Pages"]

    # pdf를 300 dpi 이미지로 변환
    images = convert_from_path(pdf_path, dpi=300)

    return images

pdf_path = "./data/기출문제/2023-3-고1-수학.pdf"
images = pdf_to_image(pdf_path)

def find_question_anchors(pil_image):
    if not ocr_engine:
        return []

    # 정규식: 공백으로 시작할 수 있고, 숫자(1개 이상)로 시작하며, 점(.)으로 끝남
    # 예: "1.", " 2.", "15."
    question_regex = re.compile(r'^\s*(\d+)\.')

    anchors = []

    try:
        img_np = np.array(pil_image.convert("RGB"))
        result = ocr_engine.predict(img_np)

        if result and result[0]:
            for line in result[0]:
                # line[0] = [ [x1,y1], [x2,y2], [x3,y3], [x4,y4] ] (좌표)
                # line[1] = ('텍스트', 신뢰도)

                text = line[1][0]
                match = question_regex.match(text)
                
                if match :
                    question_num = match.group(1)
                    anchor_point = [int(line[0][0][0]), int(line[0][0][1])] # 왼쪽 상단

                    anchor_info = {
                        "q_num": question_num,
                        "anchor_point": anchor_point
                    }

                    anchors.append(anchor_info)
        return anchors

    except Exception as e:
        print(e)

for img in images: 
    result = find_question_anchors(img)
    print(result)
    print("--------")