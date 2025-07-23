#!/bin/bash

PROJECT_ID="youvit-ai-chatbot"
BUCKET_NAME="posm-miniso"
SPREADSHEET_ID="1q3GJMpVbKL7F_t7zN1DoKjKReaiFr-kEieyJnXsJ4WA"

gcloud config set project $PROJECT_ID

echo "🔄 Updating existing secrets with correct values..."

# Update bucket name secret
echo "🪣 Updating youposm-gcs-bucket secret..."
echo -n $BUCKET_NAME | gcloud secrets versions add youposm-gcs-bucket --data-file=-

# Update spreadsheet ID secret  
echo "📊 Updating youposm-spreadsheet-id secret..."
echo -n $SPREADSHEET_ID | gcloud secrets versions add youposm-spreadsheet-id --data-file=-

echo "✅ Secrets updated successfully!"

# Verify the secrets
echo ""
echo "🔍 Verifying secrets:"
echo "Bucket name: $(gcloud secrets versions access latest --secret=youposm-gcs-bucket)"
echo "Spreadsheet ID: $(gcloud secrets versions access latest --secret=youposm-spreadsheet-id)"