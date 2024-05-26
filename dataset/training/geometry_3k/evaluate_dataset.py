import json
import os
import base64
import argparse
from openai import OpenAI
from dotenv import load_dotenv
import backoff
from datetime import datetime
from tqdm import tqdm

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

running_cost = 0.0


def evaluate_model_output(input_file_path):

    # Generate the output file path with "_evaluated" and a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = (
        f"{os.path.splitext(input_file_path)[0]}_evaluated_{timestamp}.json"
    )

    with open(input_file_path, "r") as file:
        data = json.load(file)

    # Open the output file in append mode
    with open(output_file_path, "a") as output_file:
        output_file.write("[\n")  # Start the JSON array
        first_item = True
        for item in tqdm(data, desc="Evaluating items"):
            if not first_item:
                output_file.write(",\n")  # Append a comma before each new item
            first_item = False

            problem_text = item.get("problem_text")
            answer = item.get("answer")
            reasoning = item.get("reasoning")
            image_id = item.get("image_id")

            # Construct the prompt
            prompt = (
                f"I will first give you a visual math problem, including the question, diagram, ground-truth answer, and then give you a model output containing multiple key solution steps.\n\n"
                f"Please think step by step and output the Average score, along with the Final answer score in the end, as described below:\n"
                f"– Average score: Evaluate, based on the given question, answer, diagram, whether each solution step is correct in logical reasoning, visual perception, and numerical computation, with an incorrect score of 0 and a correct score of 1. Then, calculate the average score of multiple steps.\n"
                f"– Final answer score: Match the model’s final answer with the ground truth answer, scoring 1 if it matches and 0 if it doesn’t.\n"
                f"– If the model output only includes a single step or answer, the Average score and Final answer score are the same.\n"
                f"– Question: {problem_text}\n"
                f"– Ground-truth answer: {answer}\n"
                f"– Model output: \n {reasoning}\n\n"
                f"Please return a JSON object with the following fields:\n"
                f"{{\n"
                f'    "average_score": {{average score}},\n'
                f'    "final_answer_score": {{final answer score}}\n'
                f"}}"
            )

            print(prompt)
            # Encode the image to base64
            image_file_path = os.path.join(
                os.path.dirname(__file__), "images", f"{image_id}.png"
            )
            with open(image_file_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode("utf-8")

            # Call the model to get the evaluation
            try:
                evaluation = get_evaluation(prompt, encoded_image)
                print(evaluation)
                evaluation_data = json.loads(evaluation)
                print(evaluation_data)
                item["average_score"] = evaluation_data.get("average_score", None)
                item["final_answer_score"] = evaluation_data.get(
                    "final_answer_score", None
                )

            except Exception as e:
                print(e)
                item["average_score"] = None
                item["final_answer_score"] = None

            # Write the updated item to the output file
            output_file.write(json.dumps(item))
        output_file.write("\n]")  # End the JSON array


@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def get_evaluation(prompt, encoded_image):
    global running_cost
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": json.dumps(
                    [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                    ]
                ),
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

    return response.choices[0].message.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate model output and save results."
    )
    parser.add_argument(
        "--file", type=str, required=True, help="Path to the input file"
    )
    args = parser.parse_args()

    evaluate_model_output(args.file)
