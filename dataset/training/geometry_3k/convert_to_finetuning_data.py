import json
import os
import argparse


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Convert geometry data to finetuning format."
    )
    parser.add_argument(
        "--file", type=str, required=True, help="The name of the input JSON file"
    )
    args = parser.parse_args()

    # Define the path to the input and output files
    input_file_path = os.path.join(os.path.dirname(__file__), args.file)
    output_file_path = os.path.join(
        os.path.dirname(__file__), f"{os.path.splitext(args.file)[0]}_finetuning.json"
    )

    # Load the input data
    with open(input_file_path, "r") as input_file:
        data = json.load(input_file)

    # Transform the data
    transformed_data = []
    for entry in data:
        transformed_entry = {
            "id": entry["image_id"],
            "image": entry["image_id"] + ".png",
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


if __name__ == "__main__":
    main()
