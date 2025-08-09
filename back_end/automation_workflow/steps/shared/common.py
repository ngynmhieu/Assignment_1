ACCEPTABLE_COLUMNS = {
    "File Name": str,
    "Description": str,
    "Assets": str,
    "Output Format": ["PNG", "JPG", "GIF", "MP3"],
    "Model Specification": ["OpenAI", "Claude"]
}

MAPPING_COLUMNS = {
    "File Name": "file_name",
    "Description": "file_description",
    "Assets": "example_assets",
    "Output Format": "desired_output_format",
    "Model Specification": "model_spec",
    "validation": "validation",
    "invalid_message": "invalid_message",
    "generation_status": "generation_status",
    "created_data": "created_data",
    "updated_data": "updated_data",
}