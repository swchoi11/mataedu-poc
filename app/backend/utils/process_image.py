import os
import base64
import mimetypes
import pandas as pd
from enum import Enum
from PIL import Image
import io
from typing import Union

def to_base64_data_url(image_source: Union[str, bytes, Image.Image]) -> str:
    """
    다양한 소스(파일 경로, 바이트, PIL 이미지)를 Base64 데이터 URL로 변환합니다.

    Args:
        image_source: 변환할 이미지 소스. 
                      - str: 이미지 파일 경로
                      - bytes: 이미지의 바이트 데이터
                      - Image.Image: PIL 이미지 객체

    Returns:
        Base64 데이터 URL 문자열 (예: "data:image/png;base64,...")

    Raises:
        ValueError: 지원하지 않는 입력 타입일 경우
        FileNotFoundError: 파일 경로가 유효하지 않을 경우
    """
    if isinstance(image_source, Image.Image):
        # PIL 이미지를 PNG 형식으로 메모리 버퍼에 저장
        buffered = io.BytesIO()
        image_source.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        mimetype = "image/png"
    elif isinstance(image_source, bytes):
        # 바이트 데이터 직접 사용
        img_bytes = image_source
        # 바이트만으로는 정확한 mimetype을 알기 어려우므로 일반적인 타입 사용
        mimetype = "image/png" # 혹은 "image/jpeg" 등 상황에 맞게 가정
    elif isinstance(image_source, str):
        # 파일 경로에서 읽기
        if not os.path.isfile(image_source):
            raise FileNotFoundError(f"오류: 파일을 찾을 수 없습니다. (경로: {image_source})")
        
        mimetype, _ = mimetypes.guess_type(image_source)
        if not mimetype or "image" not in mimetype:
            # mimetype을 신뢰할 수 없을 때를 대비한 fallback
            mimetype = "image/png" 

        with open(image_source, "rb") as f:
            img_bytes = f.read()
    else:
        raise ValueError("지원하지 않는 이미지 소스 타입입니다. 파일 경로(str), bytes, 또는 PIL.Image.Image를 사용하세요.")

    # Base64 인코딩 및 데이터 URL 형식으로 반환
    encoded_string = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:{mimetype};base64,{encoded_string}"


def is_line_white(pixel_data, x_start, x_end, y, threshold, width):
    """가로 한 줄이 '흰색'인지 (어두운 픽셀이 없는지) 검사"""
    x_start = max(0, x_start)
    x_end = min(width - 1, x_end)
    
    for x in range(x_start, x_end + 1):
        if pixel_data[x, y] < threshold: # 0=black, 255=white
            return False # 어두운 픽셀 발견
    return True # 모두 흰색

def is_col_white(pixel_data, y_start, y_end, x, threshold, height):
    """세로 한 줄이 '흰색'인지 검사"""
    y_start = max(0, y_start)
    y_end = min(height - 1, y_end)
    
    for y in range(y_start, y_end + 1):
        if pixel_data[x, y] < threshold:
            return False
    return True

def correct_box_with_analysis(pil_img_l, current_box_coords, other_boxes_coords):
    """공백 분석. 문제가 잘리게 크롭되지 않도록 공백을 만날때까지 영역 확장"""
    WHITE_THRESHOLD = 245 # 이 값보다 밝으면 '흰색'으로 간주 (노이즈 보정)
    STEP_SIZE = 5         # 한 번에 확장할 픽셀 수
    
    pixel_data = pil_img_l.load() # 픽셀 데이터에 빠르게 접근
    page_width, page_height = pil_img_l.size
    
    x_min, y_min, x_max, y_max = current_box_coords

    # --- 2. 아래쪽(y_max)으로 확장 ---
    # (x_min, x_max는 좌/우 확장이 완료되기 전의 값)
    current_x_min, current_x_max = x_min, x_max
    while y_max < page_height - 1:
        new_y_max = min(page_height - 1, y_max + STEP_SIZE)
        if is_line_white(pixel_data, current_x_min, current_x_max, new_y_max, WHITE_THRESHOLD, page_width):
            break # 공백이므로 중지
        
        hit_box = False
        for ox_min, oy_min, ox_max, oy_max in other_boxes_coords:
            if new_y_max >= oy_min and new_y_max <= oy_max: # Y 범위 내
                if current_x_max >= ox_min and current_x_min <= ox_max: # X 겹침
                    hit_box = True
                    break
        if hit_box:
            break # 다른 박스 영역이므로 중지
            
        y_max = new_y_max # 확장

    # --- 3. 왼쪽(x_min)으로 확장 ---
    # (y_min은 고정값, y_max는 위에서 보정된 값 사용)
    while x_min > 0:
        new_x_min = max(0, x_min - STEP_SIZE)
        if is_col_white(pixel_data, y_min, y_max, new_x_min, WHITE_THRESHOLD, page_height):
            break # 공백이므로 중지

        hit_box = False
        for ox_min, oy_min, ox_max, oy_max in other_boxes_coords:
            if new_x_min <= ox_max and new_x_min >= ox_min: # X 범위 내
                if y_max >= oy_min and y_min <= oy_max: # Y 겹침
                    hit_box = True
                    break
        if hit_box:
            break # 다른 박스 영역이므로 중지

        x_min = new_x_min # 확장

    # --- 4. 오른쪽(x_max)으로 확장 ---
    # (y_min은 고정값, y_max는 위에서 보정된 값 사용)
    while x_max < page_width - 1:
        new_x_max = min(page_width - 1, x_max + STEP_SIZE)
        if is_col_white(pixel_data, y_min, y_max, new_x_max, WHITE_THRESHOLD, page_height):
            break # 공백이므로 중지
            
        hit_box = False
        for ox_min, oy_min, ox_max, oy_max in other_boxes_coords:
            if new_x_max >= ox_min and new_x_max <= ox_max: # X 범위 내
                if y_max >= oy_min and y_min <= oy_max: # Y 겹침
                    hit_box = True
                    break
        if hit_box:
            break # 다른 박스 영역이므로 중지
            
        x_max = new_x_max # 확장

    return (x_min, y_min, x_max, y_max)
