import json
import os

# Define the path to the input and output files
input_file_path = os.path.join(os.path.dirname(__file__), "geometry_3k.json")
output_file_path = os.path.join(
    os.path.dirname(__file__), "geometry_3k_finetuning.json"
)

# Load the input data
with open(input_file_path, "r") as input_file:
    data = json.load(input_file)

# Transform the data
transformed_data = []
for entry in data:
    transformed_entry = {
        "id": entry["image_id"],
        "image": entry["image_id"],
        "conversations": [
            {
                "from": "human",
                "value": f"Solve this problem, and return the answer at the end of your response, e.g. Answer: A, B, C or D\nProblem:<image>\n{entry['problem_text']}\nChoices: {', '.join([f'{chr(65+i)}. {choice}' for i, choice in enumerate(entry['choices'])])}",
            },
            {"from": "gpt", "value": entry["reasoning"]},
        ],
    }
    transformed_data.append(transformed_entry)

# Save the transformed data to the output file
with open(output_file_path, "w") as output_file:
    json.dump(transformed_data, output_file, indent=4)
