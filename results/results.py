import json
import argparse


def calculate_accuracy(
    results_file,
    key="predicted_answer",
):
    with open(results_file, "r") as file:
        data = json.load(file)

    total_items = 0
    correct_predictions = 0

    for item in data:
        total_items += 1
        if item.get("answer") == item.get(key):
            correct_predictions += 1

    if total_items == 0:
        accuracy = 0
    else:
        accuracy = (correct_predictions / total_items) * 100

    return accuracy, total_items, f"{correct_predictions}/{total_items}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate accuracy from results file."
    )
    parser.add_argument(
        "--file", type=str, required=True, help="Path to the results file."
    )
    parser.add_argument(
        "--key",
        type=str,
        default="predicted_answer",
        help="Key to identify the predicted answer.",
    )
    args = parser.parse_args()

    results_file = args.file
    accuracy, total_items, correct_total_str = calculate_accuracy(
        results_file,
        args.key,
    )
    print(f"File processed: {results_file}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Total items: {total_items}")
    print(f"Correct/Total: {correct_total_str}")
