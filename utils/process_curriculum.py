import fitz
import sys
# import os

# def parse_pdf_with_headings_and_stitching(pdf_path: str, min_heading_size: float = 14.0) -> list[dict]:
#     """
#     [V2 - 로직 수정됨]
#     PDF에서 텍스트를 추출하되, 제목/소제목을 감지하고,
#     페이지 안팎의 논리적 문단을 병합합니다.

#     :param pdf_path: PDF 파일 경로
#     :param min_heading_size: 이 글꼴 크기 이상을 제목으로 간주 (PDF에 맞게 조절 필요)
#     :return: [{'type': 'h1'/'p', 'text': '...', 'size': 16.0, 'font': 'Arial-Bold'}, ...]
#              와 같은 사전(dict)의 리스트. 'h1'은 제목, 'p'는 본문을 의미.
#     """
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"오류: PDF 파일을 찾을 수 없습니다. 경로: {pdf_path}")

#     doc = None
#     structured_content = []
    
#     # --- [로직 수정] 문단 병합을 위한 버퍼 ---
#     buffered_block = None
#     # 새 문단 시작을 감지하기 위한 리스트 마커 (필요시 추가)
#     LIST_MARKERS = tuple("①②③④⑤⑥⑦⑧⑨⑩") + ("*", "-", "•")
#     # 문장 종료 부호
#     END_PUNCTUATION = tuple(".?!:)]}>”\"") + ("한다", "있음", "없음") # 한국어 특화 추가

#     try:
#         doc = fitz.open(pdf_path)
#         print(f"\n'{pdf_path}' 파일 여는 중... (구조적 파싱 V2)")
#         print(f"총 페이지 수: {len(doc)}")

#         for page_num in range(len(doc)):
#             page = doc.load_page(page_num)
#             page_data = page.get_text("dict", flags=fitz.TEXT_INHIBIT_SPACES)
            
#             blocks = page_data.get("blocks", [])
#             if not blocks and page_num == len(doc) - 1:
#                 # 마지막 페이지가 비어있으면, 루프가 끝나므로 버퍼를 비워야 함
#                 pass
#             elif not blocks:
#                 # (마지막 페이지가 아닌) 빈 페이지면 그냥 건너뜀
#                 continue

#             # --- [로직 수정] 페이지 내/간 블록 병합 로직 ---
#             for i, block in enumerate(blocks):
                
#                 # 1. 블록에서 텍스트와 스타일 정보 추출
#                 block_text = ""
#                 if not block.get("lines"):
#                     continue

#                 first_span = None
#                 last_span = None
#                 for line_num, line in enumerate(block.get("lines", [])):
#                     if not line.get("spans"):
#                         continue  # 빈 줄 건너뛰기
                    
#                     for span_num, span in enumerate(line.get("spans", [])):
#                         if not first_span:
#                             first_span = span
#                         block_text += span["text"]
#                         last_span = span
                    
#                     if line_num < len(block["lines"]) - 1:
#                         block_text += " " # 줄바꿈(하드 리턴)을 공백으로 변환

#                 if not first_span or not last_span or not block_text.strip():
#                     continue # 유효한 텍스트가 없는 블록 건너뛰기

#                 # 2. 블록의 대표 스타일 및 타입 결정
#                 current_text_stripped = block_text.strip()
#                 representative_size = first_span["size"]
#                 representative_font = first_span["font"]
#                 block_type = "h1" if representative_size >= min_heading_size else "p"

#                 # 3. 버퍼와 비교하여 병합 또는 플러시(flush) 결정
#                 if not buffered_block:
#                     # 버퍼가 비어있음: 현재 블록으로 새 버퍼 시작
#                     buffered_block = {
#                         "type": block_type,
#                         "text": current_text_stripped,
#                         "size": round(representative_size, 1),
#                         "font": representative_font,
#                         "last_span_text": last_span["text"].strip()
#                     }
#                     continue

#                 # --- 버퍼가 차 있음: 병합 조건 검사 ---
                
#                 # 1. 스타일이 일치하는가? (타입, 크기, 폰트)
#                 is_same_style = (
#                     buffered_block["type"] == block_type and
#                     abs(buffered_block["size"] - round(representative_size, 1)) < 0.1 and
#                     buffered_block["font"] == representative_font
#                 )
                
#                 # 2. 버퍼의 마지막 텍스트가 문장 종료 부호로 끝나는가?
#                 buffer_ends_punctuation = buffered_block["last_span_text"].endswith(END_PUNCTUATION)
                
#                 # 3. 현재 텍스트가 새 목록 마커로 시작하는가?
#                 current_starts_marker = current_text_stripped.startswith(LIST_MARKERS) or \
#                                         current_text_stripped.startswith("[") # 성취기준 ID
                
#                 # 4. 현재 블록이 헤딩(h1)인가? (헤딩은 항상 새 블록)
#                 is_heading = (block_type == 'h1')

#                 # --- 병합 조건 ---
#                 # 스타일이 같고, 헤딩이 아니며,
#                 # 이전 블록이 문장 끝이 아니었고,
#                 # 현재 블록이 새 목록으로 시작하지 않으면 => 병합!
#                 if is_same_style and not is_heading and \
#                    not buffer_ends_punctuation and \
#                    not current_starts_marker:
                    
#                     # [병합]
#                     buffered_block["text"] += " " + current_text_stripped
#                     buffered_block["last_span_text"] = last_span["text"].strip()
                
#                 else:
#                     # [플러시] (병합 조건 실패)
#                     # 1. 기존 버퍼를 structured_content에 추가
#                     structured_content.append(buffered_block)
                    
#                     # 2. 현재 블록으로 새 버퍼 시작
#                     buffered_block = {
#                         "type": block_type,
#                         "text": current_text_stripped,
#                         "size": round(representative_size, 1),
#                         "font": representative_font,
#                         "last_span_text": last_span["text"].strip()
#                     }
#             # --- [로직 수정] 페이지 루프의 끝 ---
#             # 페이지가 끝나도 버퍼는 유지 (다음 페이지와 연결될 수 있으므로)

#         # --- [로직 수정] 모든 페이지 처리 후 ---
#         # [수정] 아래의 모든 로직(버퍼 플러시, 반환)은 try 블록 내부에 있어야 합니다.
#         #      전체 블록의 들여쓰기를 1단계(4칸) 추가합니다.
#         if buffered_block:
#             structured_content.append(buffered_block)

#         # 최종 정리: 'last_span_text' 헬퍼 키 제거
#         final_content = []
#         for item in structured_content:
#             item.pop("last_span_text", None) # 헬퍼 키 제거
#             final_content.append(item)

#         return final_content

#     except Exception as e:
#         print(f"PDF 구조적 파싱 중 오류 발생: {e}", file=sys.stderr)
#         raise
    
#     finally:
#         if doc:
#             doc.close()
#             print("PDF 파일 닫힘. (구조적 파싱 V2)")


# import re

# def extract_criteria(structured_content: list[dict], file_path: str, id_prefix: str):
#     i = 0
    
#     extracted_data = ""
#     while i < len(structured_content):
        
#         item = structured_content[i]['text'].strip()
#         # print(item)
#         # print("---")
#         if re.search(id_prefix, item):
#             extracted_data+= item
#             if not item.endswith((".")):
#                 next_item = structured_content[i+1]['text'].strip()
#                 extracted_data+= next_item
#             extracted_data += '\n'
#         i += 1

#     with open(file_path,"w") as f:
#         f.write(extracted_data)


# structured_content = parse_pdf_with_headings_and_stitching("/home/user/dev/mataedu/data-old/교육과정/[별책8]+수학과+교육과정.pdf")
# extract_criteria(structured_content, id_prefix=r"^\[\d", file_path="교육과정-성취기준.txt")
# extract_criteria(structured_content, id_prefix=r"^\•\[\d", file_path="교육과정-성취기준해설.txt")
import pandas as pd

def to_csv(file_path1, file_path2):
    header = ["수행과정","성취기준"]
    data_list = []
    with open(file_path1, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            row = line[1:].split("]")
            row[1]=row[1].strip()
            if len(row) == len(header):
                data_list.append(row)
            else:
                print("파싱 개수 불일치------------")
                print(row)

    df1 = pd.DataFrame(data_list, columns=header)

    header = ["수행과정","성취기준해설"]
    data_list = []
    with open(file_path2, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            row = line[2:].split("]")
            row[1]=row[1].strip()
            if len(row) == len(header):
                data_list.append(row)
            else:
                print("파싱 개수 불일치------------")
                print(row)

    df2 = pd.DataFrame(data_list, columns=header)
    
    df = pd.merge(df1, df2, on="수행과정")

    df.to_csv("교육과정성취기준.csv", index=False)
    

to_csv(file_path1="교육과정-성취기준.txt", file_path2="교육과정-성취기준해설.txt")

