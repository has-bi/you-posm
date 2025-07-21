#!/usr/bin/env python3
"""
Comprehensive diagnostic script for You-POSM GCP setup
Run this to identify all configuration issues at once
"""

import os
import json
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_environment():
    print_section("ENVIRONMENT VARIABLES")
    
    env_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_APPLICATION_CREDENTIALS', 
        'GCS_BUCKET_NAME',
        'SPREADSHEET_ID',
        'GOOGLE_CREDENTIALS'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'CREDENTIALS' in var and len(value) > 50:
                print(f"✅ {var}: Set (length: {len(value)})")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

def check_credential_files():
    print_section("CREDENTIAL FILES")
    
    credential_paths = [
        './credentials.json',
        '/app/credentials.json',
        './service-account.json'
    ]
    
    for path in credential_paths:
        if Path(path).exists():
            try:
                with open(path, 'r') as f:
                    creds = json.load(f)
                print(f"✅ {path}: Found")
                print(f"   Project ID: {creds.get('project_id', 'N/A')}")
                print(f"   Client Email: {creds.get('client_email', 'N/A')}")
                print(f"   Type: {creds.get('type', 'N/A')}")
            except Exception as e:
                print(f"❌ {path}: Found but invalid - {str(e)}")
        else:
            print(f"❌ {path}: Not found")

def check_secret_manager():
    print_section("SECRET MANAGER ACCESS")
    
    try:
        from google.cloud import secretmanager
        print("✅ Secret Manager library imported")
        
        # Try to create client
        try:
            client = secretmanager.SecretManagerServiceClient()
            print("✅ Secret Manager client created")
            
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "youvit-ai-chatbot")
            
            # Test access to each secret
            secrets_to_test = [
                "youposm-google-credentials",
                "youposm-gcs-bucket", 
                "youposm-spreadsheet-id"
            ]
            
            for secret_name in secrets_to_test:
                try:
                    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                    response = client.access_secret_version(request={"name": name})
                    value = response.payload.data.decode("UTF-8")
                    
                    if secret_name == "youposm-google-credentials":
                        try:
                            creds_data = json.loads(value)
                            print(f"✅ {secret_name}: Accessible")
                            print(f"   Project ID: {creds_data.get('project_id', 'N/A')}")
                            print(f"   Client Email: {creds_data.get('client_email', 'N/A')}")
                        except json.JSONDecodeError:
                            print(f"❌ {secret_name}: Accessible but invalid JSON")
                    else:
                        print(f"✅ {secret_name}: {value}")
                        
                except Exception as e:
                    print(f"❌ {secret_name}: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Cannot create Secret Manager client: {str(e)}")
            
    except ImportError:
        print("❌ Secret Manager library not available")

def check_gcs_access():
    print_section("GOOGLE CLOUD STORAGE ACCESS")
    
    try:
        from google.cloud import storage
        print("✅ GCS library imported")
        
        try:
            client = storage.Client()
            print("✅ GCS client created")
            
            bucket_name = "posm-miniso"  # Your bucket name
            try:
                bucket = client.bucket(bucket_name)
                exists = bucket.exists()
                print(f"✅ Bucket '{bucket_name}' exists: {exists}")
                
                if exists:
                    # Test upload permission
                    try:
                        blob = bucket.blob("test-connection.txt")
                        blob.upload_from_string("test", content_type="text/plain")
                        blob.delete()
                        print("✅ Upload/delete permissions work")
                    except Exception as e:
                        print(f"❌ Upload test failed: {str(e)}")
                        
            except Exception as e:
                print(f"❌ Bucket access failed: {str(e)}")
                
        except Exception as e:
            print(f"❌ Cannot create GCS client: {str(e)}")
            
    except ImportError:
        print("❌ GCS library not available")

def check_sheets_access():
    print_section("GOOGLE SHEETS ACCESS")
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        print("✅ Sheets libraries imported")
        
        # Try to get credentials
        creds_dict = None
        
        # Try Secret Manager first
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "youvit-ai-chatbot")
            name = f"projects/{project_id}/secrets/youposm-google-credentials/versions/latest"
            response = client.access_secret_version(request={"name": name})
            creds_json = response.payload.data.decode("UTF-8")
            creds_dict = json.loads(creds_json)
            print("✅ Got credentials from Secret Manager")
        except Exception as e:
            print(f"❌ Secret Manager credentials failed: {str(e)}")
            
            # Try local file
            if Path("credentials.json").exists():
                with open("credentials.json", 'r') as f:
                    creds_dict = json.load(f)
                print("✅ Got credentials from local file")
        
        if creds_dict:
            try:
                sheets_creds = Credentials.from_service_account_info(
                    creds_dict, 
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets", 
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
                gc = gspread.authorize(sheets_creds)
                print("✅ Sheets client authorized")
                
                # Test spreadsheet access
                spreadsheet_id = "1q3GJMpVbKL7F_t7zN1DoKjKReaiFr-kEieyJnXsJ4WA"
                try:
                    spreadsheet = gc.open_by_key(spreadsheet_id)
                    worksheet = spreadsheet.sheet1
                    print(f"✅ Spreadsheet accessible: '{spreadsheet.title}'")
                    print(f"   Worksheet: '{worksheet.title}'")
                    
                    # Test read access
                    try:
                        headers = worksheet.row_values(1)
                        print(f"✅ Can read headers: {headers}")
                    except Exception as e:
                        print(f"❌ Cannot read data: {str(e)}")
                        
                    # Test write access
                    try:
                        # Try to add a test row and then delete it
                        test_row = ["TEST", "TEST", "TEST", "TEST", "TEST", "TEST", "TEST"]
                        worksheet.append_row(test_row)
                        
                        # Get last row and delete it
                        all_values = worksheet.get_all_values()
                        if all_values and all_values[-1][0] == "TEST":
                            worksheet.delete_rows(len(all_values))
                            print("✅ Write permissions work")
                        else:
                            print("⚠️  Write test inconclusive")
                            
                    except Exception as e:
                        print(f"❌ Write test failed: {str(e)}")
                        
                except Exception as e:
                    print(f"❌ Cannot access spreadsheet: {str(e)}")
                    
            except Exception as e:
                print(f"❌ Cannot authorize sheets client: {str(e)}")
        else:
            print("❌ No credentials available for Sheets")
            
    except ImportError as e:
        print(f"❌ Sheets libraries not available: {str(e)}")

def check_cloud_run_metadata():
    print_section("CLOUD RUN METADATA")
    
    # Check if running in Cloud Run
    if os.getenv('K_SERVICE'):
        print("✅ Running in Cloud Run")
        print(f"   Service: {os.getenv('K_SERVICE')}")
        print(f"   Revision: {os.getenv('K_REVISION')}")
        print(f"   Configuration: {os.getenv('K_CONFIGURATION')}")
    else:
        print("❌ Not running in Cloud Run (local environment)")
    
    # Check metadata server access
    try:
        import requests
        response = requests.get(
            'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
            headers={'Metadata-Flavor': 'Google'},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Metadata server accessible")
        else:
            print(f"❌ Metadata server returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot access metadata server: {str(e)}")

def main():
    print("🔍 You-POSM Diagnostic Tool")
    print("This will check all aspects of your GCP configuration")
    
    check_environment()
    check_credential_files()
    check_cloud_run_metadata()
    check_secret_manager()
    check_gcs_access()
    check_sheets_access()
    
    print_section("SUMMARY & RECOMMENDATIONS")
    print("If you see any ❌ above, those need to be fixed before deployment.")
    print("\nCommon fixes:")
    print("1. Ensure service account has all required IAM roles")
    print("2. Share Google Spreadsheet with service account email")
    print("3. Verify Secret Manager secrets are created correctly")
    print("4. Check that credentials.json is valid (for local testing)")

if __name__ == "__main__":
    main()