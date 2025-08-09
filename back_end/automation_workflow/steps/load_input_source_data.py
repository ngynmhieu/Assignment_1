

import logging

def main_load_input_source_data(query_dict: dict, google_service) -> None:
    """
    Main function to load input source data for the automation workflow.
    """
    try:
        # Extract Google Sheets URL
        google_sheets_url = query_dict.get("google_sheets_url", "")

        # Load data from Google Sheets
        if google_sheets_url:
            result = google_service.get_data_from_sheets(google_sheets_url)
            if result.get("data"):
                # Extract rows from Google Sheet data
                result["data"] = [dict(zip(result["data"][0], row)) for row in result["data"][1:]]
                return result

    except Exception as e:
        logging.error(f"Error loading input source data: {e}")
        return {}