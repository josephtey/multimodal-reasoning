import json


def calculate_accuracy(results_file):
    with open(results_file, "r") as file:
        data = json.load(file)

    total_items = 0
    correct_predictions = 0

    for item in data:
        if item.get("question_type") == "multi-choice":
            total_items += 1
            if item.get("answer") == item.get("predicted_answer"):
                correct_predictions += 1

    if total_items == 0:
        accuracy = 0
    else:
        accuracy = (correct_predictions / total_items) * 100

    return accuracy, total_items


# Example usage
results_file = "results.json"
accuracy, total_items = calculate_accuracy(results_file)
print(f"Accuracy: {accuracy:.2f}%")
print(f"Total items: {total_items}")
