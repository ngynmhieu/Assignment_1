
import os
import shutil

from back_end.automation_workflow.steps.store_output_data import main_store_output_data
from back_end.services.google_service.google_service import GoogleService
from back_end.automation_workflow.steps.load_input_source_data import main_load_input_source_data
from back_end.automation_workflow.steps.upload_output_data import  main_upload_output_data
from back_end.automation_workflow.steps.send_email_notification import main_send_email_notifications
from back_end.automation_workflow.steps.validate_input_data import main_validate_input_data
from back_end.automation_workflow.steps.generate_content import main_generate_content
from back_end.services.mongodb_service.mongodb_service import MongoDBService

# Dynamically determine the workspace root and temp folder path
TEMP_FOLDER_PATH = os.path.join(os.getcwd(), 'back_end', 'automation_workflow', 'steps', 'shared', 'temp_folder')

class AutomationWorkflow:
    def generate_report(self, update_status=None):
        """
        Generate a summarized report using the ReportGenerator backend service.
        """
        from back_end.services.report_generator.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        # Use current query_dict as input_fields
        report = report_generator.generate_daily_report(self.query_dict, update_status or (lambda msg: None))
        self.query_dict["summarized_report"] = report
        return report
    def __init__(self) -> None:
        """
        Initialize the Automation Workflow
        """
        # Initialize attributes
        self.steps = []
        self.status = "Not Started" # Not Started, In Progress, (Success or Failed)
        self.error_message = ""
        self.status_callback = None # Callback for status updates
        self.google_service = GoogleService()
        self.mongodb_service = MongoDBService()

        # Query dictionary for storing results
        self.query_dict = {}

    # 1. Load input source data
    def _load_input_source_data(self) -> None:
        # Run task
        task_result = main_load_input_source_data(self.query_dict, self.google_service)
        
        # Result
        if task_result:
            self.query_dict.update(task_result)
            self._run_next_step("validate_input_data")
        else:
            self.stop_process(status="Failed", error_message="Failed to load data from Google Sheets")

    # 2. Validate input data
    def _validate_input_data(self) -> None:
        # Run task
        task_result = main_validate_input_data(self.query_dict)

        # Result
        if task_result:
            self.query_dict["data"] = task_result
            self._run_next_step("generate_content")
        else:
            self.stop_process(status="Failed", error_message="Failed to validate input data")

    # 3. Generate content
    def _generate_content(self) -> None:
        # Run task
        task_result = main_generate_content(self.query_dict, TEMP_FOLDER_PATH)

        # Result
        if task_result:
            self.query_dict["data"] = task_result
            self._run_next_step("store_output_data")
        else:
            self.stop_process(status="Failed", error_message="Failed to generate content")

    # 4. Store output data
    def _store_output_data(self) -> None:
        """
        Store output data in MongoDB
        """
        # Run task
        task_result = main_store_output_data(self.query_dict, self.mongodb_service)

        # Result
        if task_result:
            self.query_dict["data"] = task_result
            self._run_next_step("upload_output_data")
        else:
            self.stop_process(status="Failed", error_message="Failed to store data to MongoDB")

    # 5. Upload output data
    def _upload_output_data(self) -> None:
        """
        Store output data to Google Drive
        """
        # Run task
        task_result = main_upload_output_data(self.query_dict, self.google_service)

        # Result
        if task_result:
            self.query_dict["data"] = task_result
            self.stop_process(status="Success")
        else:
            self.stop_process(status="Failed", error_message="Failed to store data to Google Drive")

    def load_input_data(self, input_fields: dict, status_callback) -> None:
        """
        Load input data from Google Sheets
        """
        # Prepare input fields
        input_fields = {
            "google_sheets_url": input_fields.get("google_sheets_url", ""),
            "google_drive_folder_url": input_fields.get("google_drive_folder_url", ""),
            "send_email_notifications": input_fields.get("send_email_notifications", False),
            "email_address": input_fields.get("email_address", "")
        }
        
        # Result
        self.query_dict.update(input_fields)
        self.status_callback = status_callback
        
    def send_email_notifications(self) -> None:
        """
        Send email notifications if enabled
        """
        # Skip email notifications if not enabled
        if not self.query_dict.get("send_email_notifications"):
            return
        else:
            # Run task
            task_result = main_send_email_notifications(self.status, self.query_dict, self.error_message, self.google_service)
                
            # Result
            if task_result:
                self.query_dict["sent_message"] = task_result
                self.stop_process(status="Success")
            else:
                self.stop_process(status="Failed", error_message="Failed to send email notifications")

    def process(self) -> dict:
        """
        Process the automation workflow
        """
        # Initialize steps
        self.status = "In Progress"
        self.steps = {
            "load_input_source_data": {"function": self._load_input_source_data, "description": "Load input source data from Google Sheets"},
            "validate_input_data": {"function": self._validate_input_data, "description": "Validate input data"},
            "generate_content": {"function": self._generate_content, "description": "Generate content by AI models"},
            "store_output_data": {"function": self._store_output_data, "description": "Store output data in Google Drive"},
            "upload_output_data": {"function": self._upload_output_data, "description": "Upload output data to Google Drive"},
        }
        
        # Start with the first step
        self._run_next_step("load_input_source_data")

    def _run_next_step(self, next_step_name: str) -> None:
        """
        Run the next step in the workflow
        """
        # Update UI status by step description
        if self.status_callback:
            self.status_callback(f"Running step: {self.steps[next_step_name]['description']}")
        return self.steps[next_step_name]["function"]()

    def stop_process(self, status: str="Failed", error_message: str="") -> dict:
        """
        Finalize the workflow and return the result
        """
        # Update status and error message
        self.status = status
        self.error_message = error_message

    def reset_resources(self) -> None:
        """
        Reset the workflow resources
        """
        self.steps = []
        self.query_dict = {}
        self.status = "Not Started"
        self.error_message = ""
        self._clear_temp_folder()

    def _clear_temp_folder(self):
        """
        Remove all files in the temp folder (TEMP_FOLDER_PATH)
        """
        if os.path.exists(TEMP_FOLDER_PATH):
            shutil.rmtree(TEMP_FOLDER_PATH)
        os.makedirs(TEMP_FOLDER_PATH, exist_ok=True)