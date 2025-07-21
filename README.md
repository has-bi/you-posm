# You-POSM 📊

A modern, mobile-first data collection system for store Point of Sale Materials (POSM) management. Built with Streamlit and Google Cloud Platform.

## Features

- 📱 **Mobile-optimized UI** - Clean, responsive design for field usage
- 📊 **Google Sheets integration** - Automatic data storage and retrieval
- 🖼️ **Image management** - Before/after photo upload to Google Cloud Storage
- 👥 **Dynamic dropdowns** - Auto-populated store and employee lists
- 🔐 **Secure authentication** - Google Cloud service account integration
- ☁️ **Cloud deployment** - Ready for Google Cloud Run deployment

## Tech Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python 3.11+
- **Storage**: Google Cloud Storage
- **Database**: Google Sheets
- **Authentication**: Google Cloud Service Account
- **Deployment**: Google Cloud Run

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud account
- Google Sheets API access
- Google Cloud Storage bucket

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd you-posm
   ```

2. **Set up virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up Google Cloud credentials**

   - Download service account JSON file
   - Place as `credentials.json` in project root
   - Share Google Spreadsheet with service account email

6. **Run locally**
   ```bash
   streamlit run app-local.py
   ```

### Production Deployment

1. **Set up Google Cloud secrets**

   ```bash
   ./setup-secrets.sh
   ```

2. **Deploy to Cloud Run**
   ```bash
   ./deploy-youposm.sh
   ```

## Configuration

### Environment Variables

| Variable                         | Description           | Example              |
| -------------------------------- | --------------------- | -------------------- |
| `GOOGLE_CLOUD_PROJECT`           | GCP Project ID        | `youvit-ai-chatbot`  |
| `GCS_BUCKET_NAME`                | Storage bucket name   | `posm-miniso`        |
| `SPREADSHEET_ID`                 | Google Sheets ID      | `11GbrOp7_...`       |
| `GOOGLE_APPLICATION_CREDENTIALS` | Credentials file path | `./credentials.json` |

### Google Cloud Setup

1. **Enable APIs**

   - Google Sheets API
   - Google Drive API
   - Google Cloud Storage API
   - Secret Manager API

2. **Create Service Account**

   - Download credentials JSON
   - Grant necessary permissions
   - Share spreadsheet with service account

3. **Set up Storage Bucket**
   - Create GCS bucket
   - Configure appropriate access controls

## Project Structure

```
you-posm/
├── app.py                 # Main Streamlit app (production)
├── app-local.py          # Local development version
├── debug-diagnosis.py    # Diagnostic tool
├── test-sheets.py        # Google Sheets test
├── setup-secrets.sh      # GCP setup script
├── deploy-youposm.sh     # Deployment script
├── pyproject.toml        # Dependencies
├── Dockerfile           # Container configuration
├── cloudbuild.yaml      # Cloud Build configuration
├── .env.example         # Environment template
└── README.md           # This file
```

## Usage

1. **Access the app** (locally at http://localhost:8501)
2. **Select or add store** from dropdown
3. **Select or add employee** from dropdown
4. **Choose date** for the entry
5. **Upload before/after images**
6. **Submit** to save data and images

## Development

### Running Tests

```bash
# Test Google Sheets connection
python test-sheets.py

# Run full diagnostic
python debug-diagnosis.py
```

### Adding Test Data

```bash
# Populate spreadsheet with sample data
python add-test-data.py
```

## Security

- ✅ Credentials never committed to Git
- ✅ Environment variables for sensitive data
- ✅ Google Cloud Secret Manager for production
- ✅ Service account authentication
- ✅ Proper .gitignore configuration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and diagnostics
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or create an issue in the repository.
