

from components import encode_image, dataframe_to_str
from chains import final_chain

from test import pdf_to_image_generator, process_pdf_document

pdf_file_path = "./data-old/기출문제/2023-3-고1-수학.pdf"
items = process_pdf_document(pdf_file_path)


curriculum_data = dataframe_to_str("./data/curriculum.csv")
common_data = {
    "curriculum_data":curriculum_data
}
for item in items:
    file_data = encode_image(item)

    input_dict = {
        "file_data": file_data
    }

    result = final_chain.invoke(
        input_dict,
        config={"configurable": common_data}
    )
