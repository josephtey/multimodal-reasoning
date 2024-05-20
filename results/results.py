import json
import argparse


def calculate_accuracy(
    results_file,
    multi_choice=False,
    vision_only=False,
    text_lite=False,
    free_form=False,
    key="predicted_answer",
):
    with open(results_file, "r") as file:
        data = json.load(file)

    total_items = 0
    correct_predictions = 0

    for item in data:
        if (
            (not multi_choice or item.get("question_type") == "multi-choice")
            and (not vision_only or item.get("problem_version") == "Vision Only")
            and (not text_lite or item.get("problem_version") == "Text Lite")
            and (not free_form or item.get("question_type") == "free-form")
        ):
            total_items += 1
            if item.get("answer") == item.get(key):
                correct_predictions += 1

    if total_items == 0:
        accuracy = 0
    else:
        accuracy = (correct_predictions / total_items) * 100

    return accuracy, total_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate accuracy from results file."
    )
    parser.add_argument(
        "--file", type=str, required=True, help="Path to the results file."
    )
    parser.add_argument(
        "--multi-choice", action="store_true", help="Filter for multi-choice questions."
    )
    parser.add_argument(
        "--vision-only", action="store_true", help="Filter for Vision Only problems."
    )
    parser.add_argument(
        "--text-lite", action="store_true", help="Filter for Text Lite problems."
    )
    parser.add_argument(
        "--key",
        type=str,
        default="predicted_answer",
        help="Key to identify the predicted answer.",
    )
    parser.add_argument(
        "--free-form", action="store_true", help="Include free-form answers."
    )
    args = parser.parse_args()

    results_file = args.file
    accuracy, total_items = calculate_accuracy(
        results_file,
        args.multi_choice,
        args.vision_only,
        args.text_lite,
        args.free_form,
        args.key,
    )
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Total items: {total_items}")
