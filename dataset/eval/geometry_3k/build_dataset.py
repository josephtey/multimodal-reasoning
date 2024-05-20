import os
import json
from openai import OpenAI
import base64
import shortuuid
import tqdm

# Define the path to the raw_data directory
raw_data_path = os.path.join(os.path.dirname(__file__), "raw_data")

# Define the path to the output file
output_file_path = os.path.join(os.path.dirname(__file__), "geometry_3k.json")

# Add '[' at the start of the file
if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
    with open(output_file_path, "w") as output_file:
        output_file.write("[")

# Initialize running cost
running_cost = 0

# Loop through each folder from 2401 to 3001 with tqdm for progress bar
for folder_num in tqdm.tqdm(range(2401, 3002), desc="Processing folders"):
    folder_path = os.path.join(raw_data_path, str(folder_num))
    data_file_path = os.path.join(folder_path, "data.json")
    image_file_path = os.path.join(folder_path, "img_diagram.png")

    if os.path.exists(data_file_path) and os.path.exists(image_file_path):
        with open(data_file_path, "r") as data_file:
            data = json.load(data_file)
            problem_text = data.get("problem_text")
            choices = data.get("choices")
            answer = data.get("answer")
            problem_type_graph = data.get("problem_type_graph")
            problem_type_goal = data.get("problem_type_goal")

            # Encode the image to base64
            with open(image_file_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode("utf-8")

            # Generate a unique UUID for the image
            image_uuid = shortuuid.uuid()
            new_image_path = os.path.join(
                os.path.dirname(__file__), "images", f"{image_uuid}.png"
            )

            # Save the image with the new UUID
            with open(new_image_path, "wb") as new_image_file:
                new_image_file.write(image_data)

            # Create the data structure
            data_entry = {
                "problem_text": problem_text,
                "choices": choices,
                "answer": answer,
                "problem_type_graph": problem_type_graph,
                "problem_type_goal": problem_type_goal,
                "image_id": image_uuid,
            }

            # Append the data entry to the dataset file
            with open(output_file_path, "a") as output_file:
                output_file.write(json.dumps(data_entry, indent=4) + ",\n")

# Add ']' at the end of the file
with open(output_file_path, "a") as output_file:
    output_file.write("]")
