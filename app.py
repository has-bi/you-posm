import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import storage
from PIL import Image
import io
from datetime import datetime, date
import os
import json
import uuid
import time
from typing import Optional
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="You-POSM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-first, clean styling
st.markdown("""
<style>
    /* Hide Streamlit elements for cleaner mobile UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Mobile-optimized container */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Clean header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Status indicator */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    .status-connected {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Form styling */
    .form-section {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    .form-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin: 0 0 1rem 0;
        text-align: center;
    }
    
    /* Image upload areas */
    .upload-area {
        border: 2px dashed #ddd;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
        background: #fafafa;
    }
    
    /* Success/Error messages */
    .message-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        border-left: 4px solid #dc3545;
    }
    
    /* Mobile button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit file uploader label */
    .uploadedFile {
        display: none;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
        .form-section {
            padding: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        .form-section {
            padding: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

class YouPosmHandler:
    """You-POSM handler with Google Cloud Secret Manager backend"""
    
    def __init__(self):
        self.gc = None
        self.storage_client = None
        self.bucket = None
        self.worksheet = None
        self.connection_status = {"sheets": False, "storage": False}
        self._setup_connections()
    
    def _get_secret(self, secret_name: str, project_id: str) -> Optional[str]:
        """Get secret from Secret Manager with error handling"""
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            st.warning(f"Could not get {secret_name} from Secret Manager: {str(e)}")
            return None
    
    def _setup_connections(self):
        """Setup Google Cloud connections using Secret Manager or environment variables"""
        try:
            # Get project ID from environment or default
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "youvit-ai-chatbot")
            
            # Initialize variables
            bucket_name = None
            spreadsheet_id = None
            creds_dict = None
            
            # Try to get configuration from Secret Manager first
            try:
                # Get secrets from Secret Manager
                bucket_name = self._get_secret("youposm-gcs-bucket", project_id)
                spreadsheet_id = self._get_secret("youposm-spreadsheet-id", project_id)
                
                # Get credentials from Secret Manager
                creds_json = self._get_secret("youposm-google-credentials", project_id)
                if creds_json:
                    creds_dict = json.loads(creds_json)
                    
            except ImportError:
                st.info("🔄 Secret Manager not available, using environment variables")
            except Exception as e:
                st.info(f"🔄 Secret Manager access failed: {str(e)}, falling back to environment variables")
            
            # Fallback to environment variables if Secret Manager failed
            if not bucket_name:
                bucket_name = os.getenv("GCS_BUCKET_NAME")
            if not spreadsheet_id:
                spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not creds_dict:
                # Try environment variables for credentials
                google_creds_json = os.getenv("GOOGLE_CREDENTIALS")
                if google_creds_json:
                    try:
                        creds_dict = json.loads(google_creds_json)
                    except json.JSONDecodeError:
                        # Maybe it's a file path
                        if os.path.exists(google_creds_json):
                            with open(google_creds_json, 'r') as f:
                                creds_dict = json.load(f)
                
                # Try default credentials.json file (for local development)
                if not creds_dict and os.path.exists("credentials.json"):
                    with open("credentials.json", 'r') as f:
                        creds_dict = json.load(f)
            
            # Validate required configuration
            if not bucket_name:
                st.error("❌ GCS bucket name not found in Secret Manager or environment variables")
                return False
                
            if not spreadsheet_id:
                st.error("❌ Spreadsheet ID not found in Secret Manager or environment variables")
                return False
            
            if not creds_dict:
                st.error("❌ Google Cloud credentials not found in Secret Manager, environment variables, or credential files")
                return False
            
            # Setup Google Sheets
            try:
                sheets_creds = Credentials.from_service_account_info(
                    creds_dict, 
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets", 
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
                self.gc = gspread.authorize(sheets_creds)
                
                # Connect to the backend spreadsheet
                spreadsheet = self.gc.open_by_key(spreadsheet_id)
                self.worksheet = spreadsheet.sheet1
                
                # Verify sheet structure and create headers if needed
                self._ensure_sheet_structure()
                
                self.connection_status["sheets"] = True
                
            except Exception as e:
                st.error(f"❌ Cannot connect to Google Sheets: {str(e)}")
                self.connection_status["sheets"] = False
            
            # Setup Google Cloud Storage
            try:
                storage_creds = Credentials.from_service_account_info(
                    creds_dict, 
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                self.storage_client = storage.Client(credentials=storage_creds)
                self.bucket = self.storage_client.bucket(bucket_name)
                
                # Test bucket access
                self.bucket.exists()
                self.connection_status["storage"] = True
                
            except Exception as e:
                st.error(f"❌ Cannot connect to storage bucket '{bucket_name}': {str(e)}")
                self.connection_status["storage"] = False
                
        except Exception as e:
            st.error(f"❌ Setup error: {str(e)}")
            return False
    
    def _ensure_sheet_structure(self):
        """Ensure the spreadsheet has the correct headers"""
        try:
            # Expected headers
            expected_headers = [
                'Store_Name', 'Employee_Name', 'Date', 
                'Before_Image_URL', 'After_Image_URL', 
                'Timestamp', 'Status'
            ]
            
            # Get current headers
            try:
                current_headers = self.worksheet.row_values(1)
            except:
                current_headers = []
            
            # If no headers or headers don't match, set them
            if not current_headers or current_headers != expected_headers:
                self.worksheet.clear()
                self.worksheet.append_row(expected_headers)
                st.info("📋 Spreadsheet headers configured")
                
        except Exception as e:
            st.warning(f"Could not verify spreadsheet structure: {str(e)}")
    
    def get_existing_data(self):
        """Get existing data from spreadsheet for dropdowns"""
        try:
            if not self.worksheet:
                return [], []
            
            # Get all records
            records = self.worksheet.get_all_records()
            if not records:
                return [], []
            
            df = pd.DataFrame(records)
            
            # Extract unique stores and employees
            stores = []
            employees = []
            
            if 'Store_Name' in df.columns:
                stores = sorted([s for s in df['Store_Name'].dropna().unique().tolist() if s])
            
            if 'Employee_Name' in df.columns:
                employees = sorted([e for e in df['Employee_Name'].dropna().unique().tolist() if e])
            
            return stores, employees
            
        except Exception as e:
            st.error(f"❌ Error loading existing data: {str(e)}")
            return [], []
    
    def upload_image(self, image: Image.Image, store: str, employee: str, img_type: str) -> Optional[str]:
        """Upload image to GCS with uniform bucket-level access"""
        try:
            if not self.bucket:
                st.error("❌ Storage bucket not connected")
                return None
            
            # Clean names for folder structure
            clean_store = "".join(c for c in store if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            clean_employee = "".join(c for c in employee if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            
            # Generate path
            date_str = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            
            path = f"you-posm/{clean_store}/{clean_employee}/{date_str}/{img_type}/{timestamp}_{unique_id}.jpg"
            
            # Optimize image
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            if image.width > 1920:
                ratio = 1920 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((1920, new_height), Image.Resampling.LANCZOS)
            
            # Upload to GCS
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG', quality=85, optimize=True)
            img_bytes.seek(0)
            
            blob = self.bucket.blob(path)
            blob.upload_from_file(img_bytes, content_type='image/jpeg')
            
            # Don't try to make public - return the blob name instead
            # For uniform bucket-level access, we use a different URL format
            public_url = f"https://storage.googleapis.com/{self.bucket.name}/{path}"
            
            return public_url
            
        except Exception as e:
            st.error(f"❌ Image upload failed: {str(e)}")
            return None
    
    def save_data(self, data: dict) -> bool:
        """Save data to backend spreadsheet"""
        try:
            if not self.worksheet:
                st.error("❌ Spreadsheet not connected")
                return False
            
            # Prepare row data matching spreadsheet structure
            row_data = [
                data['store_name'],           # Store_Name
                data['employee_name'],        # Employee_Name  
                data['date'],                 # Date
                data['before_image_url'],     # Before_Image_URL
                data['after_image_url'],      # After_Image_URL
                data['timestamp'],            # Timestamp
                'Active'                      # Status
            ]
            
            self.worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            st.error(f"❌ Data save failed: {str(e)}")
            return False

def main():
    # Clean header
    st.markdown("""
    <div class="main-header">
        <h1>📊 You-POSM</h1>
        <p>Store Data Collection System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize handler
    if 'handler' not in st.session_state:
        with st.spinner("🔧 Initializing connections..."):
            st.session_state.handler = YouPosmHandler()
    
    # Connection status (compact)
    if st.session_state.handler.connection_status["sheets"] and st.session_state.handler.connection_status["storage"]:
        st.markdown('<div class="status-badge status-connected">✅ System Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-error">❌ Connection Error</div>', unsafe_allow_html=True)
    
    # Check if properly configured
    if not (st.session_state.handler.connection_status["sheets"] and st.session_state.handler.connection_status["storage"]):
        st.error("""
        ❌ **Configuration Required**
        
        The system needs proper configuration to work. Please check:
        
        **For Cloud Run deployment:**
        - Secret Manager secrets are configured
        - Service account has proper permissions
        - Google Spreadsheet is shared with service account
        
        **For local development:**
        - `credentials.json` file in project root
        - Environment variables in `.env` file
        """)
        st.stop()
    
    # Get data for dropdowns
    with st.spinner("📊 Loading data..."):
        stores, employees = st.session_state.handler.get_existing_data()
    
    # Main data collection form
    st.markdown('<div class="form-title">➕ Add New Entry</div>', unsafe_allow_html=True)
    
    with st.form("data_form", clear_on_submit=True):
        # Store and Employee in single row for mobile
        col1, col2 = st.columns(2)
        
        with col1:
            # Store selection
            store_options = ["Select Store..."] + stores + ["+ New Store"]
            store_selection = st.selectbox("🏪 Store", store_options)
            
            store_name = ""
            if store_selection == "+ New Store":
                store_name = st.text_input("New Store Name", placeholder="Enter store name", key="new_store")
            elif store_selection and store_selection != "Select Store...":
                store_name = store_selection
        
        with col2:
            # Employee selection
            employee_options = ["Select Employee..."] + employees + ["+ New Employee"]
            employee_selection = st.selectbox("👤 Employee", employee_options)
            
            employee_name = ""
            if employee_selection == "+ New Employee":
                employee_name = st.text_input("New Employee Name", placeholder="Enter employee name", key="new_employee")
            elif employee_selection and employee_selection != "Select Employee...":
                employee_name = employee_selection
        
        # Date (compact)
        entry_date = st.date_input("📅 Date", value=date.today())
        
        # Image uploads (mobile-optimized)
        st.markdown("**📸 Upload Images**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Before**")
            before_image = st.file_uploader(
                "Upload Before Image", 
                type=['png', 'jpg', 'jpeg'],
                key="before_img"
            )
            if before_image:
                st.image(before_image, use_column_width=True)
        
        with col2:
            st.markdown("**After**")
            after_image = st.file_uploader(
                "Upload After Image", 
                type=['png', 'jpg', 'jpeg'],
                key="after_img"
            )
            if after_image:
                st.image(after_image, use_column_width=True)
        
        # Submit button (full width)
        submitted = st.form_submit_button("💾 Submit Entry", type="primary")
        
        if submitted:
            # Validation
            errors = []
            if not store_name.strip():
                errors.append("Store name is required")
            if not employee_name.strip():
                errors.append("Employee name is required")
            if not before_image:
                errors.append("Before image is required")
            if not after_image:
                errors.append("After image is required")
            
            if errors:
                st.markdown(f"""
                <div class="message-box error-box">
                    <strong>❌ Please complete:</strong><br>
                    • {('<br>• ').join(errors)}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Process submission
                with st.spinner("📤 Uploading data and images..."):
                    try:
                        before_img = Image.open(before_image)
                        after_img = Image.open(after_image)
                        
                        # Upload images
                        before_url = st.session_state.handler.upload_image(
                            before_img, store_name, employee_name, "before"
                        )
                        after_url = st.session_state.handler.upload_image(
                            after_img, store_name, employee_name, "after"
                        )
                        
                        if before_url and after_url:
                            # Prepare data for backend spreadsheet
                            data = {
                                'store_name': store_name.strip(),
                                'employee_name': employee_name.strip(),
                                'date': entry_date.strftime("%Y-%m-%d"),
                                'before_image_url': before_url,
                                'after_image_url': after_url,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            }
                            
                            if st.session_state.handler.save_data(data):
                                st.markdown("""
                                <div class="message-box success-box">
                                    <strong>✅ Success!</strong><br>
                                    Data and images uploaded successfully.
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                
                                # Show uploaded images (mobile optimized)
                                st.markdown("**📷 Uploaded Images:**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.image(before_url, caption=f"Before - {store_name}", use_column_width=True)
                                with col2:
                                    st.image(after_url, caption=f"After - {store_name}", use_column_width=True)
                                
                                # Auto-refresh in 3 seconds to show updated dropdown data
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Failed to save data to spreadsheet")
                        else:
                            st.error("❌ Failed to upload images")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing submission: {str(e)}")

if __name__ == "__main__":
    main()