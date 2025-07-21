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
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="You-POSM Data Collection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .upload-box {
        border: 2px dashed #ddd;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class YouPosmHandler:
    """Simple handler for You-POSM data collection"""
    
    def __init__(self):
        self.gc = None
        self.storage_client = None
        self.bucket = None
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup Google Cloud connections"""
        try:
            # Get credentials
            if "google_credentials" in st.secrets:
                creds_dict = dict(st.secrets["google_credentials"])
                bucket_name = st.secrets.get("gcs_bucket_name", "")
            else:
                creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS", "{}"))
                bucket_name = os.getenv("GCS_BUCKET_NAME", "")
            
            if not creds_dict:
                st.error("❌ Google Cloud credentials not configured")
                return False
            
            # Setup Google Sheets
            sheets_creds = Credentials.from_service_account_info(
                creds_dict, 
                scopes=["https://www.googleapis.com/auth/spreadsheets", 
                       "https://www.googleapis.com/auth/drive"]
            )
            self.gc = gspread.authorize(sheets_creds)
            
            # Setup Google Cloud Storage
            storage_creds = Credentials.from_service_account_info(
                creds_dict, 
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self.storage_client = storage.Client(credentials=storage_creds)
            
            if bucket_name:
                self.bucket = self.storage_client.bucket(bucket_name)
                return True
            else:
                st.error("❌ GCS bucket name not configured")
                return False
                
        except Exception as e:
            st.error(f"❌ Setup error: {str(e)}")
            return False
    
    def connect_spreadsheet(self, url: str):
        """Connect to Google Sheets"""
        try:
            if "/spreadsheets/d/" in url:
                sheet_id = url.split("/spreadsheets/d/")[1].split("/")[0]
            else:
                sheet_id = url
            
            spreadsheet = self.gc.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # Get existing data
            records = worksheet.get_all_records()
            df = pd.DataFrame(records) if records else pd.DataFrame()
            
            return df, worksheet
            
        except Exception as e:
            st.error(f"❌ Spreadsheet connection failed: {str(e)}")
            return None, None
    
    def upload_image(self, image: Image.Image, store: str, employee: str, img_type: str) -> Optional[str]:
        """Upload image to GCS with organized structure"""
        try:
            if not self.bucket:
                return None
            
            # Clean names for folder structure
            clean_store = "".join(c for c in store if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            clean_employee = "".join(c for c in employee if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            
            # Generate path: you-posm/{store}/{employee}/{date}/{type}/{timestamp_uuid}.png
            date_str = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            
            path = f"you-posm/{clean_store}/{clean_employee}/{date_str}/{img_type}/{timestamp}_{unique_id}.png"
            
            # Optimize image
            if image.width > 1920:
                ratio = 1920 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((1920, new_height), Image.Resampling.LANCZOS)
            
            # Upload to GCS
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)
            
            blob = self.bucket.blob(path)
            blob.upload_from_file(img_bytes, content_type='image/png')
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            st.error(f"❌ Image upload failed: {str(e)}")
            return None
    
    def save_data(self, worksheet, data: list) -> bool:
        """Save data to spreadsheet"""
        try:
            worksheet.append_row(data)
            return True
        except Exception as e:
            st.error(f"❌ Data save failed: {str(e)}")
            return False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 You-POSM</h1>
        <p>Store Data Collection Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize handler
    if 'handler' not in st.session_state:
        st.session_state.handler = YouPosmHandler()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Setup")
        
        # Connection status
        if st.session_state.handler.bucket:
            st.success(f"✅ Connected to: {st.session_state.handler.bucket.name}")
        else:
            st.error("❌ Not connected to storage")
        
        # Spreadsheet connection
        sheet_url = st.text_input(
            "📊 Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste your Google Sheets URL here"
        )
        
        if st.button("🔗 Connect", type="primary"):
            if sheet_url:
                with st.spinner("Connecting..."):
                    df, worksheet = st.session_state.handler.connect_spreadsheet(sheet_url)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.worksheet = worksheet
                        st.success("✅ Connected!")
                        st.rerun()
            else:
                st.error("Please enter a spreadsheet URL")
    
    # Main content
    if 'df' in st.session_state and 'worksheet' in st.session_state:
        # Data overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Total Records</h3>
                <h2>{}</h2>
            </div>
            """.format(len(st.session_state.df)), unsafe_allow_html=True)
        
        with col2:
            stores_count = st.session_state.df['Store Name'].nunique() if 'Store Name' in st.session_state.df.columns and not st.session_state.df.empty else 0
            st.markdown("""
            <div class="metric-card">
                <h3>🏪 Stores</h3>
                <h2>{}</h2>
            </div>
            """.format(stores_count), unsafe_allow_html=True)
        
        with col3:
            employees_count = st.session_state.df['Employee'].nunique() if 'Employee' in st.session_state.df.columns and not st.session_state.df.empty else 0
            st.markdown("""
            <div class="metric-card">
                <h3>👥 Employees</h3>
                <h2>{}</h2>
            </div>
            """.format(employees_count), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Data collection form
        st.header("📝 Add New Entry")
        
        # Get existing data for dropdowns
        stores = []
        employees = []
        
        if not st.session_state.df.empty:
            if 'Store Name' in st.session_state.df.columns:
                stores = sorted(st.session_state.df['Store Name'].dropna().unique().tolist())
            if 'Employee' in st.session_state.df.columns:
                employees = sorted(st.session_state.df['Employee'].dropna().unique().tolist())
        
        with st.form("data_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Store selection
                store_name = st.selectbox("🏪 Store Name", [""] + stores, help="Select or add new store below")
                new_store = st.text_input("➕ New Store", placeholder="Enter new store name")
                if new_store:
                    store_name = new_store
                
                # Date
                entry_date = st.date_input("📅 Date", value=date.today())
            
            with col2:
                # Employee selection
                employee = st.selectbox("👤 Employee", [""] + employees, help="Select or add new employee below")
                new_employee = st.text_input("➕ New Employee", placeholder="Enter new employee name")
                if new_employee:
                    employee = new_employee
            
            # Image uploads
            st.subheader("📸 Upload Images")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Before Image**")
                before_image = st.file_uploader(
                    "before_upload", 
                    type=['png', 'jpg', 'jpeg'],
                    label_visibility="collapsed"
                )
                if before_image:
                    st.image(before_image, caption="Before", use_column_width=True)
            
            with col2:
                st.markdown("**After Image**")
                after_image = st.file_uploader(
                    "after_upload", 
                    type=['png', 'jpg', 'jpeg'],
                    label_visibility="collapsed"
                )
                if after_image:
                    st.image(after_image, caption="After", use_column_width=True)
            
            # Submit
            submitted = st.form_submit_button("💾 Submit Entry", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                if not store_name:
                    errors.append("Store name is required")
                if not employee:
                    errors.append("Employee name is required")
                if not before_image:
                    errors.append("Before image is required")
                if not after_image:
                    errors.append("After image is required")
                
                if errors:
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>❌ Please fix:</strong><br>
                        • {('<br>• ').join(errors)}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Process submission
                    with st.spinner("Uploading images..."):
                        before_img = Image.open(before_image)
                        after_img = Image.open(after_image)
                        
                        before_url = st.session_state.handler.upload_image(before_img, store_name, employee, "before")
                        after_url = st.session_state.handler.upload_image(after_img, store_name, employee, "after")
                        
                        if before_url and after_url:
                            # Save to spreadsheet
                            data_row = [
                                store_name,
                                employee,
                                entry_date.strftime("%Y-%m-%d"),
                                before_url,
                                after_url,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ]
                            
                            if st.session_state.handler.save_data(st.session_state.worksheet, data_row):
                                st.markdown("""
                                <div class="success-box">
                                    <strong>✅ Success!</strong><br>
                                    Data and images uploaded successfully.
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                
                                # Refresh data
                                df, _ = st.session_state.handler.connect_spreadsheet(sheet_url)
                                if df is not None:
                                    st.session_state.df = df
                                
                                # Show uploaded images
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.image(before_url, caption="Before (Uploaded)", width=200)
                                with col2:
                                    st.image(after_url, caption="After (Uploaded)", width=200)
        
        # Recent entries
        if not st.session_state.df.empty:
            st.header("📊 Recent Entries")
            
            # Show last 5 entries
            recent = st.session_state.df.tail(5).iloc[::-1]  # Reverse to show newest first
            
            for idx, row in recent.iterrows():
                with st.expander(f"🏪 {row.get('Store Name', 'Unknown')} - {row.get('Employee', 'Unknown')} ({row.get('Date', 'Unknown')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'Before Picture' in row and row['Before Picture']:
                            st.image(row['Before Picture'], caption="Before", width=200)
                    
                    with col2:
                        if 'After Picture' in row and row['After Picture']:
                            st.image(row['After Picture'], caption="After", width=200)
    
    else:
        # Welcome message
        st.info("""
        👋 **Welcome to You-POSM!**
        
        **Quick Setup:**
        1. Enter your Google Sheets URL in the sidebar
        2. Click "Connect" to load existing data
        3. Start collecting store data with before/after images
        
        **Required Spreadsheet Columns:**
        - Store Name
        - Employee
        - Date
        - Before Picture
        - After Picture
        - Timestamp
        """)

if __name__ == "__main__":
    main()