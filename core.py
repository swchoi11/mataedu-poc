

from components import encode_image, dataframe_to_str
from app.custom_langchain.chains import process_item_chain

# pdf_file_path = "./data-old/기출문제/2023-3-고1-수학.pdf"
# items = process_pdf_document(pdf_file_path)


# curriculum_data = dataframe_to_str("./data/curriculum.csv")
# common_data = {
#     "curriculum_data":curriculum_data
# }
# for item in items:
#     file_data = encode_image(item)

#     input_dict = {
#         "file_data": file_data
#     }

#     result = final_chain.invoke(
#         input_dict,
#         config={"configurable": common_data}
#     )

file_data = encode_image("./data-old/개별문항/test.png")

curriculum_data = dataframe_to_str("./data/curriculum.csv")
common_data = {
    "curriculum_data": curriculum_data
}
criteria_data = dataframe_to_str('./교육과정성취기준.csv')
initial_input = {
    "file_data": file_data,
    "criteria": criteria_data
}
output = process_item_chain(initial_input, config={"configurable": common_data})
print(output)