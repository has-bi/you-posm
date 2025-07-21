#!/bin/bash

# Configuration - UPDATE THESE VALUES
PROJECT_ID="youvit-ai-chatbot"
SERVICE_ACCOUNT_EMAIL="your-service-account@youvit-ai-chatbot.iam.gserviceaccount.com"  # UPDATE THIS
BUCKET_NAME="your-bucket-name"  # UPDATE THIS
SPREADSHEET_ID="11GbrOp7_B-dTYnYw_e_CIRxoHRuWXKCinbfUKU_Oww8"  # UPDATE THIS
CREDENTIALS_FILE="path/to/your/credentials.json"  # UPDATE THIS

# Set project
gcloud config set project $PROJECT_ID

# Enable Secret Manager API (if not already enabled)
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo "Creating secrets in Secret Manager..."

# 1. Google credentials secret
echo "📁 Creating youposm-google-credentials secret..."
gcloud secrets create youposm-google-credentials \
    --data-file=$CREDENTIALS_FILE \
    --replication-policy="automatic"

# 2. GCS bucket name secret
echo "🪣 Creating youposm-gcs-bucket secret..."
echo -n $BUCKET_NAME | gcloud secrets create youposm-gcs-bucket \
    --data-file=- \
    --replication-policy="automatic"

# 3. Spreadsheet ID secret
echo "📊 Creating youposm-spreadsheet-id secret..."
echo -n $SPREADSHEET_ID | gcloud secrets create youposm-spreadsheet-id \
    --data-file=- \
    --replication-policy="automatic"

# Grant your service account access to the secrets
echo "🔐 Granting service account access to secrets..."

gcloud secrets add-iam-policy-binding youposm-google-credentials \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding youposm-gcs-bucket \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding youposm-spreadsheet-id \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

echo "✅ Secret Manager setup complete!"
echo ""
echo "📋 Summary:"
echo "   • youposm-google-credentials: Service account credentials"
echo "   • youposm-gcs-bucket: $BUCKET_NAME"
echo "   • youposm-spreadsheet-id: $SPREADSHEET_ID"
echo ""
echo "🚀 Your service account ($SERVICE_ACCOUNT_EMAIL) now has access to all secrets."
echo ""
echo "Next steps:"
echo "1. Make sure your service account has the necessary IAM roles:"
echo "   - Storage Object Admin (for bucket access)"
echo "   - Secret Manager Secret Accessor (already granted)"
echo "2. Share your Google Spreadsheet with: $SERVICE_ACCOUNT_EMAIL"
echo "3. Deploy your app to Cloud Run"