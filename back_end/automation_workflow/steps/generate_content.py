import os
import json
import logging

from back_end.automation_workflow.steps.shared.common import ACCEPTABLE_COLUMNS

def main_generate_content(query_dict: dict, temp_folder_path: str) -> dict:
    """
    Main function to generate content
    For each element in input_source_data, create a JSON file with its content in temp_folder_path.
    """
    try:
        # Ensure temp folder exists
        os.makedirs(temp_folder_path, exist_ok=True)

        input_source_data = query_dict.get("data", [])
        updating_input_source_data = []

        for idx, element in enumerate(input_source_data):
            # Create JSON file for each valid element
            if element.get("validation", False):
                file_name = element.get("File Name", f"generated_content_{idx}")
                file_path = os.path.join(temp_folder_path, file_name+".json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json_data = {k: element[k] for k in ACCEPTABLE_COLUMNS if k in element}
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                    element["file_path"] = file_path
                    element["generation_status"] = "Success"
            else:
                element["file_path"] = ""
                element["generation_status"] = "Failed"

            updating_input_source_data.append(element)

        return updating_input_source_data

    except Exception as e:
        logging.error(f"Error in main_generate_content: {e}")
        return {}
