#!/bin/bash

# Quick fix script for common You-POSM issues
PROJECT_ID="youvit-ai-chatbot"
SERVICE_ACCOUNT="route-optimizer@youvit-ai-chatbot.iam.gserviceaccount.com"
BUCKET_NAME="posm-miniso"
SPREADSHEET_ID="11GbrOp7_B-dTYnYw_e_CIRxoHRuWXKCinbfUKU_Oww8"

echo "🔧 Quick Fix for You-POSM Issues"
echo "================================="

# Set project
gcloud config set project $PROJECT_ID

echo "1️⃣ Checking and fixing IAM permissions..."

# Ensure service account has all required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectAdmin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.legacyBucketReader" \
    --quiet

echo "2️⃣ Verifying Secret Manager secrets..."

# Check if secrets exist and are accessible
for secret in youposm-google-credentials youposm-gcs-bucket youposm-spreadsheet-id; do
    if gcloud secrets describe $secret &>/dev/null; then
        echo "✅ Secret $secret exists"
        
        # Ensure service account has access
        gcloud secrets add-iam-policy-binding $secret \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/secretmanager.secretAccessor" \
            --quiet
    else
        echo "❌ Secret $secret missing - run setup-secrets.sh first"
    fi
done

echo "3️⃣ Checking Google Cloud Storage bucket..."

# Verify bucket exists and is accessible
if gsutil ls gs://$BUCKET_NAME &>/dev/null; then
    echo "✅ Bucket $BUCKET_NAME is accessible"
    
    # Test upload permission
    echo "test" | gsutil cp - gs://$BUCKET_NAME/test-connection.txt
    gsutil rm gs://$BUCKET_NAME/test-connection.txt
    echo "✅ Upload permissions work"
else
    echo "❌ Cannot access bucket $BUCKET_NAME"
    echo "Creating bucket..."
    gsutil mb gs://$BUCKET_NAME
    
    # Set bucket permissions
    gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:objectAdmin gs://$BUCKET_NAME
fi

echo "4️⃣ Enabling required APIs..."

gcloud services enable secretmanager.googleapis.com \
    storage.googleapis.com \
    sheets.googleapis.com \
    drive.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com

echo ""
echo "🎯 ACTION REQUIRED:"
echo "Share your Google Spreadsheet with: $SERVICE_ACCOUNT"
echo "Spreadsheet URL: https://docs.google.com/spreadsheets/d/$SPREADSHEET_ID/edit"
echo ""
echo "Steps:"
echo "1. Open the spreadsheet URL above"
echo "2. Click 'Share' button"
echo "3. Add: $SERVICE_ACCOUNT"
echo "4. Give 'Editor' permissions"
echo "5. Click 'Send'"
echo ""
echo "✅ Quick fix complete!"
echo "Run: python debug-diagnosis.py to verify everything works"