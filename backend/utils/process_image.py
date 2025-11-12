import os
import base64
import mimetypes
import pandas as pd
from enum import Enum
from PIL import Image

def encode_image(file_path: str) -> str | None:
    
    if not os.path.isfile(file_path):
        print(f"오류: 파일을 찾을 수 없습니다. (경로: {file_path})")
        return None
        
    mimetype, _ = mimetypes.guess_type(file_path)

    if not mimetype:
        print("파일의 mime 타입을 알 수 없습니다.")
        return None
    if "image" not in mimetype:
        print("이미지 파일이 아닙니다.")
        return None

    try:
        with open(file_path, "rb") as f:
            encode_string = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mimetype};base64,{encode_string}"

    except Exception as e:
        print(e)

        return None

def encode_pil_image_to_base64(pil_image: Image.Image) -> str:
    """
    메모리 상의 PIL 이미지를 Gemini가 인식할 수 있는
    Base64 Data URL 문자열로 변환합니다.
    """
    buffered = io.BytesIO()
    # 이미지를 PNG 형식으로 메모리 버퍼에 저장
    pil_image.save(buffered, format="PNG") 
    # Base64로 인코딩
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    # Data URL 형식으로 반환
    return f"data:image/png;base64,{img_str}"


def dataframe_to_str(file_path: str) -> str | None:
    if not os.path.isfile(file_path):
        print(f"오류: 커리큘럼 파일을 찾을 수 없습니다. (경로: {file_path})")
        return None
        
    try:
        data_frame = pd.read_csv(file_path)
        data_str = data_frame.to_string(index=False, max_rows=100) # 데이터가 너무 길어지는 것을 방지
        return data_str
    except Exception as e:
        print(f"커리큘럼 파일 로드 또는 변환 중 오류: {e}")
        return None



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

import io

def encode_pil_image_to_base64(pil_image: Image.Image) -> str:
    """
    메모리 상의 PIL 이미지를 Gemini가 인식할 수 있는
    Base64 Data URL 문자열로 변환합니다.
    """
    buffered = io.BytesIO()
    # 이미지를 PNG 형식으로 메모리 버퍼에 저장
    pil_image.save(buffered, format="PNG") 
    # Base64로 인코딩
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    # Data URL 형식으로 반환
    return f"data:image/png;base64,{img_str}"

def encode_image_from_bytes(image_bytes: bytes):
    content_type = "image/png"
    base64_string = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{base64_string}"