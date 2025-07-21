#!/usr/bin/env python3
"""
Quick test to verify Google Sheets access
"""
import gspread
from google.oauth2.service_account import Credentials
import json

print("🔍 Testing Google Sheets Access")
print("=" * 50)

try:
    # Load credentials
    with open('credentials.json', 'r') as f:
        creds_dict = json.load(f)
    
    print(f"✅ Service Account: {creds_dict['client_email']}")
    
    # Authorize
    creds = Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(creds)
    print("✅ Sheets client authorized")
    
    # Test spreadsheet access
    spreadsheet_id = "11GbrOp7_B-dTYnYw_e_CIRxoHRuWXKCinbfUKU_Oww8"
    
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        print(f"✅ SUCCESS: Connected to '{spreadsheet.title}'")
        print(f"✅ Worksheet: '{spreadsheet.sheet1.title}'")
        
        # Try to read data
        try:
            headers = spreadsheet.sheet1.row_values(1)
            if headers:
                print(f"✅ Headers: {headers}")
            else:
                print("⚠️  No headers found - spreadsheet is empty")
                
            # Try to get all records
            records = spreadsheet.sheet1.get_all_records()
            print(f"✅ Data rows: {len(records)}")
            
            # Test write access by adding and removing a test row
            try:
                test_row = ["TEST", "TEST", "TEST", "TEST", "TEST", "TEST", "TEST"]
                spreadsheet.sheet1.append_row(test_row)
                print("✅ Write access: SUCCESS")
                
                # Remove the test row
                all_values = spreadsheet.sheet1.get_all_values()
                if all_values and len(all_values) > 1 and all_values[-1][0] == "TEST":
                    spreadsheet.sheet1.delete_rows(len(all_values))
                    print("✅ Test row cleaned up")
                    
            except Exception as e:
                print(f"❌ Write access FAILED: {str(e)}")
                
        except Exception as e:
            print(f"❌ Read access FAILED: {str(e)}")
            
    except gspread.exceptions.SpreadsheetNotFound:
        print("❌ SPREADSHEET NOT FOUND or NOT SHARED")
        print("")
        print("🔧 TO FIX THIS:")
        print("1. Go to: https://docs.google.com/spreadsheets/d/11GbrOp7_B-dTYnYw_e_CIRxoHRuWXKCinbfUKU_Oww8/edit")
        print("2. Click 'Share' button (top right)")
        print("3. Add: route-optimizer@youvit-ai-chatbot.iam.gserviceaccount.com")
        print("4. Set permission to 'Editor'")
        print("5. Click 'Send'")
        
    except Exception as e:
        print(f"❌ SPREADSHEET ACCESS FAILED: {str(e)}")
        print("")
        print("🔧 Possible issues:")
        print("- Spreadsheet not shared with service account")
        print("- Service account doesn't have Editor permissions")
        print("- Spreadsheet ID is incorrect")
        
except Exception as e:
    print(f"❌ SETUP FAILED: {str(e)}")

print("")
print("📋 Service Account Email: route-optimizer@youvit-ai-chatbot.iam.gserviceaccount.com")
print("📋 Spreadsheet URL: https://docs.google.com/spreadsheets/d/11GbrOp7_B-dTYnYw_e_CIRxoHRuWXKCinbfUKU_Oww8/edit")