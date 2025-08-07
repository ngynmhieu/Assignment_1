import time

from back_end.google_service.google_service import GoogleService
from back_end.automation_workflow.steps.load_input_source_data import main_load_input_source_data
from back_end.automation_workflow.steps.store_output_data import main_store_output_data
from back_end.automation_workflow.steps.send_email_notification import main_send_email_notifications

class AutomationWorkflow:
    def __init__(self) -> None:
        """
        Initialize the Automation Workflow
        """
        # Initialize attributes
        self.steps = []
        self.status = "Not Started"
        self.status_callback = None # Callback for status updates
        self.google_service = GoogleService()

        # Query dictionary for storing results
        self.query_dict = {}

    def _load_input_source_data(self) -> None:
        # Run task
        task_result = main_load_input_source_data(self.query_dict, self.google_service)
        
        # Result
        if task_result:
            self.query_dict["input_source_data"] = task_result
            self._run_next_step("generate_content")
        else:
            self._run_error_step("Failed to load data from Google Sheets")
            
    def _generate_content(self) -> None:
        time.sleep(3)
        self._run_next_step("store_output_data")

    def _store_output_data(self) -> None:
        """
        Store output data to Google Drive
        """
        # Run task
        self.query_dict["file_path"] = "C:\\Users\\Minh Hieu\\OneDrive\\Desktop\\Assignment_1\\test.txt"
        task_result = main_store_output_data(self.query_dict, self.google_service)

        # Result
        if task_result:
            self.query_dict["uploaded_file"] = task_result
            self._run_next_step("send_email_notifications")
        else:
            self._run_error_step("Failed to store data to Google Drive")
            
    def _send_email_notifications(self) -> None:
        """
        Send email notifications if enabled
        """
        # Run task
        if self.query_dict.get("send_email_notifications") and self.query_dict.get("email_address"):
            sent_message = main_send_email_notifications(self.query_dict, self.google_service)
            
        # Result
        if sent_message:
            self.query_dict["sent_message"] = sent_message
            self._run_final_step("Success")
        else:
            self._run_error_step("Failed to send email notifications")

    def load_input_data(self, input_fields: dict, status_callback) -> None:
        """
        Load input data from Google Sheets
        """
        # Prepare input fields
        input_fields = {
            "google_sheets_url": input_fields.get("google_sheets_url", ""),
            "google_drive_folder_url": input_fields.get("google_drive_folder_url", ""),
            "send_email_notifications": input_fields.get("send_email_notifications", False),
            "email_address": input_fields.get("email_address", None)
        }
        
        # Result
        self.query_dict.update(input_fields)
        self.status_callback = status_callback

    def process(self) -> dict:
        """
        Process the automation workflow
        """
        # Initialize steps
        self.status = "In Progress"
        self.steps = {
            "load_input_source_data": {"function": self._load_input_source_data, "description": "Load input source data from Google Sheets"},
            "generate_content": {"function": self._generate_content, "description": "Generate content by AI models"},
            "store_output_data": {"function": self._store_output_data, "description": "Store output data in Google Drive"},
            "send_email_notifications": {"function": self._send_email_notifications, "description": "Send email notifications if enabled"},
        }
        
        # Start with the first step
        self._run_next_step("store_output_data")

    def _run_next_step(self, next_step_name: str) -> None:
        """
        Run the next step in the workflow
        """
        print(f"Running step: {self.steps[next_step_name]['description']}")
        if self.status_callback:
            self.status_callback(f"Running step: {self.steps[next_step_name]['description']}")
        return self.steps[next_step_name]["function"]()

    def _run_final_step(self, status: str) -> dict:
        """
        Finalize the workflow and return the result
        """
        self.status = status
        self.query_dict = {}

    def _run_error_step(self, error_message: str) -> None:
        """
        Stop execution and notify via callback
        """
        self.status = "Error"
        if self.status_callback:
            self.status_callback(f"Error: {error_message}")
        return self._run_final_step("Error")