import os
import json
from openai import OpenAI
import base64
import shortuuid
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# Loop through each folder from 0 to 1000
for folder_num in range(1001):
    print(f"Processing item: {folder_num}")
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

            # Prefix choices with A, B, C, D
            choices_with_prefix = [
                f"{chr(65 + i)}. {choice}" for i, choice in enumerate(choices)
            ]

            # Construct the prompt
            prompt = (
                "Please analyze the question and provide a concise (max. 5 steps), structured step-by-step reasoning that leads to the correct answer. "
                "Clearly indicate how the visual diagram is used at each step. "
                "You must end with the definitive answer, e.g. Answer: {A, B, C or D}\n\n"
                f"Question: {problem_text} \nChoices: {', '.join(choices_with_prefix)} \nAnswer: {answer}"
            )

            # Encode the image to base64
            with open(image_file_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode("utf-8")

            # Feed the prompt and image to GPT-4 to generate a rationale
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{encoded_image}"
                                },
                            },
                        ],
                    },
                ],
            )

            # Extract token usage from the response
            total_tokens = response.usage.total_tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            cost_per_million_input_tokens = 5  # $5 per 1 million input tokens
            cost_per_million_output_tokens = 15  # $15 per 1 million output tokens

            input_cost = (input_tokens / 1_000_000) * cost_per_million_input_tokens
            output_cost = (output_tokens / 1_000_000) * cost_per_million_output_tokens
            total_cost = input_cost + output_cost

            # Update running cost
            running_cost += total_cost

            print(f"Running total cost: ${running_cost:.4f}")

            rationale = response.choices[0].message.content

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
                "reasoning": rationale,
                "image_id": image_uuid,
                "prompt": prompt,
            }

            # Append the data entry to the dataset file
            with open(output_file_path, "a") as output_file:
                output_file.write(json.dumps(data_entry, indent=4) + ",\n")

# Add ']' at the end of the file
with open(output_file_path, "a") as output_file:
    output_file.write("]")
