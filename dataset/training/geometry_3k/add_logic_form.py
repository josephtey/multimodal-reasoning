import json
import os

# Load geometry_3k.json
with open("geometry_3k.json", "r") as f:
    geometry_data = json.load(f)

# Loop through each item in geometry_3k.json
for i, item in enumerate(geometry_data):
    # Construct the path to the ith folder in raw_data
    raw_data_folder = f"raw_data/{i}"
    logic_form_path = os.path.join(raw_data_folder, "logic_form.json")

    # Check if logic_form.json exists
    if os.path.exists(logic_form_path):
        # Open logic_form.json and extract "diagram_logic_form"
        with open(logic_form_path, "r") as lf:
            logic_form_data = json.load(lf)
            diagram_logic_form_list = logic_form_data.get("diagram_logic_form", [])
            diagram_logic_form_text = "\n".join(diagram_logic_form_list)
            diagram_logic_form = f"Diagram Logic Form:\n{diagram_logic_form_text}"

        # Append "diagram_logic_form" to the start of "reasoning"
        if "reasoning" in item:
            item["reasoning"] = (
                f"{diagram_logic_form}\n\nStep-by-step reasoning:\n{item['reasoning']}"
            )

# Save the modified data to geometry_3k_logic.json
with open("geometry_3k_logic.json", "w") as f:
    json.dump(geometry_data, f, indent=2)
