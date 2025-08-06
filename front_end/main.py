import streamlit as st

from back_end.automation_workflow.automation_workflow import AutomationWorkflow

# Set page configuration
st.set_page_config(
    page_title="Automation Workflow App",
    page_icon="🤖",
    layout="wide"
)

# Initialize the automation workflow
if 'automation_workflow' not in st.session_state:
    # Create instance once and store in session state
    st.session_state.automation_workflow = AutomationWorkflow()

# Now you can use the instance throughout your app
automation_workflow = st.session_state.automation_workflow

# Header with description
st.title("🤖 Automation Workflow Dashboard")
st.markdown("""
### Automated Content Generation from Google Sheets
This application processes data from your Google Sheets, generates content using AI models, 
and stores the results in your Google Drive with optional email notifications.
""")

# Main content in a container
with st.container():
    st.markdown("---")
    
    # I. HEADER SECTION
    # Input section
    st.subheader("📝 Configuration")
    
    # Inputs for Google Sheets and Google Drive
    input_source_col, output_source_col = st.columns(2)

    # II. INPUTS AND CONFIGURATION
    with input_source_col:
        # Google Sheets input
        st.markdown("**📊 Input Source**")
        google_sheets_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
            help="Enter the URL of your Google Sheets containing the input data"
        )
    
    with output_source_col:
        # Google Drive output
        st.markdown("**💾 Output Destination**")
        google_drive_folder = st.text_input(
            "Google Drive Folder ID",
            placeholder="1ABC2def3GHI4jkl5MNO6pqr7STU8vwx9",
            help="Enter the Google Drive folder ID where outputs will be stored"
        )
    
    # Email notification checkbox
    st.markdown("**📧 Notifications**")
    send_email_notifications = st.checkbox(
        "Enable email notifications",
        help="Check this box to receive email notifications about task completion"
    )
    
    # Email input (only show if checkbox is checked)
    if send_email_notifications:
        email_address = st.text_input(
            "Email Address",
            placeholder="your-email@example.com",
            help="Enter the email address for notifications"
        )
    
    st.markdown("---")

    # III. PROCESSING AND VALIDATION
    # Processing section
    st.subheader("🚀 Processing")
    
    # Validation
    is_valid = bool(google_sheets_url and google_drive_folder)
    if send_email_notifications:
        is_valid = is_valid and bool(email_address)
    
    # Processing button
    if st.button(
        "🔄 Begin Processing",
        type="primary",
        disabled=not is_valid,
        use_container_width=True
    ):
        if is_valid:
            # Run the automation workflow
            input_fields = {
                "google_sheets_url": google_sheets_url,
                "google_drive_folder": google_drive_folder,
                "send_email_notifications": send_email_notifications,
                "email_address": email_address if send_email_notifications else None
            }
            
            # Create spinner placeholder
            status_placeholder = st.empty()
            
            # Define simple callback to update spinner
            def update_status(message):
                with status_placeholder:
                    st.info(f"⏳ {message}")
            
            automation_workflow.load_input_data(input_fields, update_status)
            automation_workflow.process()
            
            # Show final result
            if automation_workflow.status == "Success":
                status_placeholder.success("✅ Processing completed successfully!")
                
                # Display configuration summary
                st.info(f"""
                **Configuration Summary:**
                - 📊 Input: {google_sheets_url}
                - 💾 Output: Google Drive Folder ID: {google_drive_folder}
                - 📧 Email Notifications: {'Enabled' if send_email_notifications else 'Disabled'}
                {f'- 📧 Email: {email_address}' if send_email_notifications else ''}
                """)
            else:
                status_placeholder.error(f"❌ {result.get('message')}")
    
    # Help section
    if not is_valid:
        st.markdown("---")
        st.markdown("**ℹ️ Required Information:**")
        if not google_sheets_url:
            st.markdown("- 📊 Google Sheets URL is required")
        if not google_drive_folder:
            st.markdown("- 💾 Google Drive Folder ID is required")
        if send_email_notifications and not email_address:
            st.markdown("- 📧 Email address is required when notifications are enabled")

# Footer
st.markdown("---")
st.markdown("📧 **Support:** admin@example.com | 🔧 **Status:** Ready for processing")