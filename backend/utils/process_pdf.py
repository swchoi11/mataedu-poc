import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import os
import base64
import io
from typing import List, Generator

# LangChain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from utils.process_image import correct_box_with_analysis
import boto3
from config import config

storage_client = boto3.client(
    's3',
    endpoint_url = config.minio_connection_string,
    aws_access_key_id = config.MINIO_ROOT_USER,
    aws_secret_access_key = config.MINIO_ROOT_PASSWORD,
    config = boto3.session.Config(signature_version='s3v4')
)

try: 
    storage_client.head_bucket(Bucket=config.MINIO_BUCKET)
except Exception:
    storage_client.create_bucket(Bucket=config.MINIO_BUCKET)

from utils.process_image import encode_pil_image_to_base64
from custom_langchain.chains import poly_extraction

from config import config

def page_to_image_generator(pdf_path: str, dpi: int = 300) -> Generator[Image.Image, None, None]: 
    pages = None # finally 블록에서 참조하기 위해 외부에 선언
    try: 
        pages = fitz.open(pdf_path)

        for page_num in range(pages.page_count):
            page = pages.load_page(page_num)

            pix = page.get_pixmap(dpi=dpi, alpha=False)

            # pil 이미지로 변환
            try:
                # 'RGB' 모드와 pix맵 형식이 일치하게 됨
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                yield img
            except Exception as e:
                print(f"페이지 {page_num} PIL 변환 오류: {e}")
                raise
    except Exception as e:
        print(f"PDF 파일 열기 오류: {e}")
        raise
    finally:
        # 리소스 해제
        if pages:
            pages.close()

def image_generator(pdf_file_path: str, original_file_name: str) -> Generator[dict, None, None]:
        
    page_generator = page_to_image_generator(pdf_file_path, dpi=300)
    
    cropped_images = []
    total_crops_saved = 0
    
    print(f"--- PDF 처리 시작: {pdf_file_path} ---")

    for page_index, pil_img in enumerate(page_generator):
        page_num = page_index + 1
        print(f"\n--- 페이지 {page_num} 처리 시작 ---")
        
        try:
            file_data_str = encode_pil_image_to_base64(pil_img)
            input_dict = {"file_data": file_data_str}
            
            print(f"페이지 {page_num}: Gemini 호출 중...")
            result = poly_extraction.invoke(input_dict) # QuestionList 객체
            
            if not result or not result.questions:
                print(f"페이지 {page_num}: 감지된 문제 영역이 없습니다.")
                continue

            print(f"페이지 {page_num}: {len(result.questions)}개 영역 감지. 보정 및 크롭 시작...")
            
            image_width, image_height = pil_img.size
            gemini_pixel_boxes = []
            for q_box in result.questions:
                coords = (
                    int(q_box.x_min * image_width),
                    int(q_box.y_min * image_height),
                    int(q_box.x_max * image_width),
                    int(q_box.y_max * image_height)
                )
                gemini_pixel_boxes.append({"box": q_box, "coords": coords})

            # 공백 분석을 위해 이미지를 Grayscale로 변환 (한 번만)
            pil_img_l = pil_img.convert("L")

            for i in range(len(gemini_pixel_boxes)):
                
                current_item = gemini_pixel_boxes[i]
                current_q_box = current_item["box"]
                initial_coords = current_item["coords"]

                # '나'를 제외한 '다른 모든 박스'의 원본 좌표 리스트
                other_boxes_coords = [
                    item["coords"] for j, item in enumerate(gemini_pixel_boxes) if i != j
                ]
                
                final_crop_box = correct_box_with_analysis(
                    pil_img_l,          # Grayscale 이미지
                    initial_coords,     # 보정할 현재 박스
                    other_boxes_coords  # 침범하면 안 되는 다른 박스들
                )
                
                try:
                    cropped_q_image = pil_img.crop(final_crop_box)

                    # base64 문자열 생성
                    cropped_image_base64 = encode_pil_image_to_base64(cropped_q_image)

                    # minio
                    in_mem_file = io.BytesIO()
                    cropped_q_image.save(in_mem_file, format="PNG")
                    in_mem_file.seek(0)
                    base_pdf_name = os.path.basename(original_file_name)[0]
                    s3_key = f"crops/{base_pdf_name}/page_{page_num}_q_{current_q_box.question_number}.png"

                    storage_client.put_object(
                        Bucket=config.MINIO_BUCKET,
                        Key=s3_key,
                        Body=in_mem_file,
                        ContentLength=in_mem_file.getbuffer().nbytes,
                        ContentType="image/png"
                    )

                    yield {
                        "base64_data": cropped_image_base64,
                        "s3_key": s3_key,
                        "question_number": current_q_box.question_number,
                        "page_number": page_num
                    }

                except Exception as e:
                    print(f"  문제 {current_q_box.question_number} 크롭 중 오류: {e}")
                    print(f"  - 사용된 크롭 박스: {final_crop_box}")

        except Exception as e:
            print(f"페이지 {page_num} 처리 중 심각한 오류 발생: {e}")
            pass

    print(f"\n--- PDF 처리 완료 ---")
