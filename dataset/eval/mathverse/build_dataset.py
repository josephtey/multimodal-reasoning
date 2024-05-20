import shortuuid
from datasets import load_dataset
from PIL import Image
import json
import tqdm
import os

ds = load_dataset("AI4Math/MathVerse", "testmini")

image_path = "images/"
data_path = "mathverse.json"

# Create the images directory if it doesn't exist
os.makedirs(image_path, exist_ok=True)

# Open the JSON file in append mode
with open(data_path, "a") as f:
    f.write("[\n")  # Start the JSON array

    for sample_index, sample in enumerate(tqdm.tqdm(ds["testmini"])):
        uuid = shortuuid.uuid()
        sample_dict = {
            "sample_index": sample_index,
            "problem_index": sample.get("problem_index", None),
            "problem_version": sample.get("problem_version", None),
            "question": sample.get("question", None),
            "answer": sample.get("answer", None),
            "question_type": sample.get("question_type", None),
            "image": uuid + ".png",  # Change extension to .png
        }
        # Convert image to RGB before saving as PNG
        sample_image = sample["image"].convert("RGB")
        sample_image.save(os.path.join(image_path, uuid + ".png"))

        # Append the sample_dict to the JSON file
        json.dump(sample_dict, f, indent=4)
        if sample_index < len(ds["testmini"]) - 1:
            f.write(",\n")  # Add a comma after each item except the last one

    f.write("\n]")  # End the JSON array

print(f"Length of the output data: {len(ds['testmini'])}")
