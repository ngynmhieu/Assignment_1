import time  # Changed from 'from time import time'
from typing import Optional

class AutomationWorkflow:
    def __init__(
        self,
        google_sheets_url: str = "",
        google_drive_folder: str = "",
        send_email_notifications: bool = False,
        email_address: Optional[str] = None,
    ) -> None:
        """
        Initialize the Automation Workflow
        """
        # Input validation and setup
        self.google_sheets_url = google_sheets_url
        self.google_drive_folder = google_drive_folder
        self.send_email_notifications = send_email_notifications
        self.email_address = email_address
        
        # Initialize steps and state
        self.steps = []
        self.status = "Not Started"
        self.status_callback = None

    def _validate_input_data(self) -> None:
        time.sleep(1.5)
        print("✅ Input validation completed")
        self._run_next_step("load_input_source_data")

    def _load_input_source_data(self) -> None:
        time.sleep(2)
        print("✅ Data loaded successfully")
        self._run_next_step("generate_content")

    def _generate_content(self) -> None:
        time.sleep(3)
        print("✅ Content generated successfully")
        self._run_next_step("store_output_data")

    def _store_output_data(self) -> None:
        time.sleep(1.5)
        print("✅ Data stored successfully")
        self._run_next_step("send_email_notifications")

    def _send_email_notifications(self) -> None:
        if self.send_email_notifications and self.email_address:
            time.sleep(1)
            print(f"✅ Email notification sent to {self.email_address}")
            self._run_final_step("Success")
        else:
            print("✅ Email notifications are disabled or no email address provided")
            self._run_final_step("Success")

    def load_input_data(self, input_fields: dict, status_callback) -> None:
        """
        Load input data from Google Sheets
        """
        self.google_sheets_url = input_fields.get("google_sheets_url", "")
        self.google_drive_folder = input_fields.get("google_drive_folder", "")
        self.send_email_notifications = input_fields.get("send_email_notifications", False)
        self.email_address = input_fields.get("email_address", None)
        
        self.status_callback = status_callback

    def process(self) -> dict:
        """
        Process the automation workflow
        """
        # Initialize steps
        self.status = "In Progress"
        self.steps = {
            "validate_input_data": {"function": self._validate_input_data, "description": "Validate input data"},
            "load_input_source_data": {"function": self._load_input_source_data, "description": "Load input source data from Google Sheets"},
            "generate_content": {"function": self._generate_content, "description": "Generate content by AI models"},
            "store_output_data": {"function": self._store_output_data, "description": "Store output data in Google Drive"},
            "send_email_notifications": {"function": self._send_email_notifications, "description": "Send email notifications if enabled"},
        }
        
        # Run each step
        self._run_next_step("validate_input_data")

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