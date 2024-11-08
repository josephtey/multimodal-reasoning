import shortuuid
from datasets import load_dataset
from PIL import Image
import random
import json
import tqdm
import os

ds = load_dataset("diffusers/pokemon-gpt4-captions")
pokemon_data = []

pokemon_image_path = "images/"
pokemon_data_path = "pokemon_blip_captions.json"

description_list = [
    "Describe the image concisely.",
    "Provide a brief description of the given image.",
    "Offer a succinct explanation of the picture presented.",
    "Summarize the visual content of the image.",
    "Give a short and clear explanation of the subsequent image.",
    "Share a concise interpretation of the image provided.",
    "Present a compact description of the photo's key features.",
    "Relay a brief, clear account of the picture shown.",
    "Render a clear and concise summary of the photo.",
    "Write a terse but informative summary of the picture.",
    "Create a compact narrative representing the image presented.",
]

for sample in tqdm.tqdm(ds["train"]):
    uuid = shortuuid.uuid()
    sample_dict = dict()
    sample_dict["id"] = uuid
    sample_dict["image"] = "pokemon/image/" + uuid + ".jpg"
    sample["image"].save(os.path.join(pokemon_image_path, uuid + ".jpg"))
    conversations = [
        {"from": "human", "value": "<image>\n" + random.choice(description_list)},
        {"from": "gpt", "value": sample["text"]},
    ]
    sample_dict["conversations"] = conversations
    pokemon_data.append(sample_dict)

with open(pokemon_data_path, "w") as f:
    json.dump(pokemon_data, f, indent=4)
