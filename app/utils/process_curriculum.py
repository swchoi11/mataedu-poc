import fitz
import sys
import os

def process_curriculum(file_path: str, min_heading_size: float = 14.0) -> str:
    total_text = ""
    doc = None

    try:
        doc = fitz.open(file_path)
         
        print(f"{file_path} 여는 중...")

        previous_block_last_span = None # 페이지간 비교를 위한 마지막 스팬 변수

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            page_data = page.get_text("dict", flags=fitz.TEXT_INHIBIT_SPACES) # 불필요한 공백 문자 억제

            blocks = page_data.get("blocks", [])
            if not blocks:
                previous_block_last_span = None
                continue

            # 이전 페이지의 마지막 블록과 현재 페이지의 첫 블록 비교
            if previous_block_last_span and structed_content and blocks:
                first_block_lines = blocks[0].get("lines", [])
                if first_block_lines:
                    first_block_spans = first_block_lines[0].get("spans", [])
                    if first_block_spans:
                        current_block_first_span = first_block_spans[0]

                        # 페이지 간에 동일한 블록인지 파악하는 로직
                        ## 폰트 사이즈와 스타일이 동일한지
                        is_same_style = (
                            abs(previous_block_last_span['size'] - current_block_first_span['size']) < 0.1 and
                            previous_block_last_span['font'] == current_block_first_span['font']
                        )

                        # 이전 블록이 문장 종료 부호로 끝났는지
                        prev_text = previous_block_last_span['text'].strip()
                        ends_with_punctuation = prev_text.endswith(".", "?", "!", ")", "]", "}", ">")

                        if is_same_style and not ends_with_punctuation:

                            block_text = ""
                            for line in blocks[0].get("lines", []):
                                for span in line.get("spans", []):
                                    block_text += span["text"]

                                block_text += ""

                            if structed_content:
                                if structed_content[-1]["text"] and not structed_content[-1]["text"].endswith(" "):
                                    structed_content[-1]["text"] += " "
                                structed_content[-1]["text"] += block_text.strip()

                                last_line_spans = blocks[0].get("lines", [{}])[-1].get("spans",[{}])
                                if last_line_spans:
                                    previous_block_last_span = last_line_spans[-1]

                            blocks = blocks[1:]

                        else: 
                            previous_block_last_span = None
                    else:
                        previous_block_last_span = None
                else:
                    previous_block_last_span = None

            current_page_last_span = None
            for block in blocks:
                block_text = ""
                span_sizes = []
                span_fonts = []

                if not block.get("lines"):
                    continue

                first_span, last_span = None, None
                for line_num, line in enumerate(block.get("lines", [])):
                    for span_num, span in enumerate(line.get("spans", [])):
                        if not first_span:
                            first_span = span

                        block_text += span["text"]

                        span_sizes.append(span["size"])
                        span_fonts.append(span["font"])
                        last_span = span

                    if line_num < len(block["lines"]) -1:
                        block_text += " "

                if not block_text.strip():
                    continue

                current_page_last_span = last_span

                representative_size = first_span["size"] if first_span else 0.0

                block_type = "h1" if representative_size >= min_heading_size else "p"

                structed_content.append({
                    "type": block_type,
                    "text": block_text.strip(),
                    "size": round(representative_size, 1),
                    "font": first_span["font"] if first_span else "N/A"
                })

            previous_block_last_span = current_page_last_span

    except Exception as e:
        print(e)
        raise

    finally:
        if doc:
            doc.close()

    return structed_content


result = process_curriculum("/home/user/dev/mataedu/data-old/교육과정/[별책8]+수학과+교육과정.pdf")
with open("./교육과정.txt", "w") as f:
    f.write(result)


