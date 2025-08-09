import logging

from back_end.automation_workflow.steps.shared.common import ACCEPTABLE_COLUMNS

def main_validate_input_data(query_dict: dict) -> dict:
    """
    Main function to validate input data
    """
    try:
        input_source_data = query_dict.get("data", [])
        updating_input_source_data = []

        # Get rows from input source data
        rows = query_dict.get("data", [])

        # Validate each row
        for idx, row in enumerate(input_source_data):
            errors = _validate_row(row)
            if errors:
                row["validation"] = False
                invalid_message = f"\n - Row {idx} has errors: {errors}"
                row["invalid_message"] = invalid_message
            else:
                row["validation"] = True
                row["invalid_message"] = ""
                
            updating_input_source_data.append(row)

        return updating_input_source_data
    except Exception as e:
        logging.error(f"Error in main_validate_input_data: {e}")
        return {}

def _validate_row(row_dict: dict) -> list:
    """
    Validate a single row of input data
    """
    errors = []
    for column, value_constraint in ACCEPTABLE_COLUMNS.items():
        value = row_dict.get(column, "")

        # Empty value check
        if not value:
            errors.append(f"Missing value for '{column}'")
            continue

        # Type and value checks
        if isinstance(value_constraint, type):
            if not isinstance(value, value_constraint):
                errors.append(f"Invalid type for '{column}': expected {value_constraint.__name__}, got {type(value).__name__}")
        elif isinstance(value_constraint, list):
            if value.lower() not in [v.lower() for v in value_constraint]:
                errors.append(f"Invalid value for '{column}': expected one of {value_constraint}, got {value}")

    return errors