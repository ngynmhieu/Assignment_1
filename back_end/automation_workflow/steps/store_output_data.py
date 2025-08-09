import logging

from back_end.automation_workflow.steps.shared.common import MAPPING_COLUMNS
from back_end.services.mongodb_service.mongodb_service import MongoDBService

def main_store_output_data(query_dict: dict, mongodb_service: MongoDBService) -> dict:
    try:
        # Extract relevant information from the query_dict
        input_source_data = query_dict.get("data", [])
        updating_input_source_data = []

        # Validate the data
        if not input_source_data:
            return {}

        # Store data into MongoDB
        for row in input_source_data:
            stored_data = _prepare_stored_data(row)
            result = mongodb_service.insert_document(stored_data)
            if result:
                row["mongodb_id"] = result
            else:
                row["mongodb_id"] = ""
            updating_input_source_data.append(row)

        return updating_input_source_data

    except Exception as e:
        logging.error(f"Error storing output data: {e}")
        return {}

def _prepare_stored_data(data: dict) -> dict:
    """
    Prepare the data for storage in MongoDB
    """
    from datetime import datetime
    mapped_data = {MAPPING_COLUMNS[k]: data[k] for k in MAPPING_COLUMNS if k in data}
    mapped_data["created_date"] = datetime.now()  # Use local time for consistency
    return mapped_data