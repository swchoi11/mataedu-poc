from components import encode_image, dataframe_to_str
from chains import final_chain

curriculum_data = dataframe_to_str("./data/curriculum.csv")
file_data = encode_image("./data/개별문항/test2.png")

common_data = {
    "curriculum_data":curriculum_data
}

input_dict = {
    "file_data": file_data
}

result = final_chain.invoke(
    input_dict,
    config={"configurable": common_data}
)

print(result)