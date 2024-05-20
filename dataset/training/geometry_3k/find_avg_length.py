import json
import tiktoken


def calculate_total_reasoning_length(file_path):
    enc = tiktoken.get_encoding("cl100k_base")
    total_length = 0
    with open(file_path, "r") as file:
        data = json.load(file)
        for item in data:
            if "reasoning" in item:
                total_length += len(enc.encode(item["reasoning"]))
    return total_length


file_path = "geometry_3k.json"
total_reasoning_length = calculate_total_reasoning_length(file_path)
print(f"Total token length of 'reasoning' across all samples: {total_reasoning_length}")
