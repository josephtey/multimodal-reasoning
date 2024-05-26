import os
import json
import argparse
import base64
import shortuuid
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import backoff

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the path to the raw_data directory
raw_data_path = os.path.join(os.path.dirname(__file__), "raw_data")


def build_dataset(reasoning_type="default", name=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(
        os.path.dirname(__file__), f"geometry_3k_{timestamp}_{name}.json"
    )

    # Add '[' at the start of the file
    if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
        with open(output_file_path, "w") as output_file:
            output_file.write("[")

    # Initialize running cost
    running_cost = 0

    # Loop through each folder from 0 to 1000
    for folder_num in range(0, 1001):
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
                if reasoning_type == "default":
                    prompt = (
                        "Please analyze the question and provide a concise (max. 5 steps), structured step-by-step reasoning that leads to the correct answer. "
                        "Clearly indicate how the visual diagram is used at each step. "
                        "You must end with the definitive answer, e.g. Answer: {A, B, C or D}\n\n"
                        f"Question: {problem_text} \nChoices: {', '.join(choices_with_prefix)} \nAnswer: {answer}"
                    )
                elif reasoning_type == "peano":
                    prompt = (
                        "Please analyze the question and provide a concise (max. 5 steps), structured step-by-step reasoning that leads to the correct answer. "
                        "Clearly indicate how the visual diagram is used at each step. "
                        "You must end with the definitive answer, e.g. Answer: {A, B, C or D}\n\n"
                        f"Question: {problem_text} \nChoices: {', '.join(choices_with_prefix)} \nAnswer: {answer}\n\n"
                        "In your step-by-step reasoning, solve every calculation in a careful, formal manner. The calculation will follow the Peano format: \n"
                        "1- Each sentence in the solution either introduces a new variable or states a new equation. \n"
                        "2- The last sentence gives the goal: which variable will contain the answer to the problem. \n"
                        "3- Each equation only uses previously introduced variables. \n"
                        "4- Each quantity is only named by one variable. \n"
                        "5- Use all the numbers in the question.\n\n"
                        "For example,\n"
                        "Q: Mary had 5 apples. The next morning, she ate 2 apples. Then, in the afternoon, she bought as many apples as she had after eating those apples in the morning. How many apples did she end up with?\n\n"
                        "Peano-style calculation:\n"
                        "Let a be the number of apples Mary started with [[var a]]. We have [[eq a = 5]]. \n"
                        "Let b be how many apples she had in the morning after eating 2 apples [[var b]]. We have [[eq b = a - 2]]. \n"
                        "Let c be the apples she bought in the afternoon [[var c]]. \n"
                        "Since she bought as many as she had after eating, we have [[eq c = b]]. \n"
                        "Let d be how many apples she ended up with [[var d]]. We have [[eq d = b + c]]. \n"
                        "The answer is the value of d [[answer d]]. \n\n"
                        "You will incorporate Peano-style calculation in your step-by-step reasoning:"
                    )
                elif reasoning_type == "code":
                    prompt = (
                        "Write Python code to try and solve the following question using the visual diagram.\n"
                        f"Please analyze the question, writing code that reflects your step-by-step thinking to solving the problem and getting the correct answer: {choices[ord(answer) - 65]}\n"
                        "Do not use any libraries or imports. Write the code in a single file, that should output the answer, and ONLY the answer.\n\n"
                        f"Question: {problem_text} \nChoices: {', '.join(choices_with_prefix)} \nAnswer: {answer}\n\n"
                    )

                print(prompt)

                # Encode the image to base64
                with open(image_file_path, "rb") as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode("utf-8")

                @backoff.on_exception(backoff.expo, Exception, max_tries=5)
                def get_response():
                    return client.chat.completions.create(
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

                try:
                    # Feed the prompt and image to GPT-4 to generate a rationale
                    response = get_response()

                    # Extract token usage from the response
                    total_tokens = response.usage.total_tokens
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                    cost_per_million_input_tokens = 5  # $5 per 1 million input tokens
                    cost_per_million_output_tokens = (
                        15  # $15 per 1 million output tokens
                    )

                    input_cost = (
                        input_tokens / 1_000_000
                    ) * cost_per_million_input_tokens
                    output_cost = (
                        output_tokens / 1_000_000
                    ) * cost_per_million_output_tokens
                    total_cost = input_cost + output_cost

                    # Update running cost
                    running_cost += total_cost

                    print(f"Running total cost: ${running_cost:.4f}")

                    rationale = response.choices[0].message.content
                    print(rationale)

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

                except Exception as e:
                    print(f"Error processing item {folder_num}: {e}")

    # Add ']' at the end of the file
    with open(output_file_path, "a") as output_file:
        output_file.write("]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Geometry 3K Dataset")
    parser.add_argument(
        "--reasoning_type",
        type=str,
        choices=["default", "peano", "code"],
        default="default",
        help="Type of reasoning to use",
    )
    parser.add_argument(
        "--name", type=str, default="", help="Name to append to the output file path"
    )
    args = parser.parse_args()

    build_dataset(reasoning_type=args.reasoning_type, name=args.name)
