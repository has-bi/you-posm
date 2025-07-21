#!/bin/bash

# You-POSM Setup Script
# Simple setup for the You-POSM data collection platform

set -e

echo "🚀 Setting up You-POSM..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create project directory
PROJECT_DIR="you-posm"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Creating project directory..."
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Initialize uv project
echo "⚙️  Initializing project..."
uv init --no-readme

# Install dependencies
echo "📦 Installing dependencies..."
uv add streamlit pandas gspread google-auth google-cloud-storage pillow python-dotenv

# Install dev dependencies
echo "🛠️  Installing dev dependencies..."
uv add --dev black ruff mypy pytest

# Create directory structure
echo "📁 Creating directories..."
mkdir -p .streamlit
mkdir -p data

# Create configuration files
echo "⚙️  Creating configuration files..."

# Create .env file
cat > .env << 'EOF'
# You-POSM Configuration
GOOGLE_CREDENTIALS='{}'
GCS_BUCKET_NAME="you-posm-data"
EOF

# Create Streamlit config
cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = 8501

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[browser]
gatherUsageStats = false
EOF

# Create secrets template
cat > .streamlit/secrets.toml << 'EOF'
# You-POSM Secrets - UPDATE WITH YOUR CREDENTIALS
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"

gcs_bucket_name = "you-posm-data"
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data
data/
EOF

# Create simple README
cat > README.md << 'EOF'
# You-POSM

Simple store data collection platform with image uploads.

## Quick Start

1. **Setup credentials:**
   ```bash
   # Edit .streamlit/secrets.toml with your Google Cloud credentials
   ```

2. **Run the app:**
   ```bash
   uv run streamlit run app.py
   ```

3. **Access:** http://localhost:8501

## Features

- 📊 Google Sheets integration
- 📸 Before/after image uploads
- ☁️ Google Cloud Storage
- 🏪 Store and employee tracking
- 📱 Mobile-friendly interface

## Folder Structure

Images are organized as:
```
you-posm/
├── {store_name}/
│   ├── {employee_name}/
│   │   ├── {date}/
│   │   │   ├── before/
│   │   │   └── after/
```

## Requirements

- Google Cloud Project with:
  - Cloud Storage API enabled
  - Sheets API enabled
  - Service account with appropriate permissions
EOF

echo "✅ You-POSM setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .streamlit/secrets.toml with your Google Cloud credentials"
echo "2. Create a Google Cloud Storage bucket named 'you-posm-data'"
echo "3. Create a Google Sheets document with these columns:"
echo "   - Store Name, Employee, Date, Before Picture, After Picture, Timestamp"
echo "4. Run: uv run streamlit run app.py"
echo ""
echo "🌐 Your You-POSM platform will be available at: http://localhost:8501"
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.docker/

# Logs
*.log

# Data
data/
uploads/
EOF

# Create README.md
cat > README.md << 'EOF'
# Store Data Collection Platform

A Streamlit application for collecting store data with image uploads, integrated with Google Sheets.

## Features

- 📊 Google Sheets integration for data storage
- 📸 Image upload with Google Cloud Storage
- 🗂️ Organized folder structure by store/employee/date
- 🏪 Store and employee management
- 📅 Date tracking
- 🐳 Docker deployment ready
- ⚡ Built with modern Python tools (uv)
- ☁️ Automatic image resizing and optimization

## Folder Organization

Images are automatically organized in Google Cloud Storage as:

```
store-data/
├── Store_Name_1/
│   ├── Employee_Name_1/
│   │   ├── 2024-01-15/
│   │   │   ├── before/
│   │   │   │   └── 2024-01-15_14-30-25_abc123def.png
│   │   │   └── after/
│   │   │       └── 2024-01-15_14-30-25_xyz789abc.png
│   │   └── 2024-01-16/
│   │       ├── before/
│   │       └── after/
│   └── Employee_Name_2/
│       └── ...
└── Store_Name_2/
    └── ...
```

## Quick Start

### 1. Google Cloud Setup

**Create Google Cloud Project:**
```bash
# Install Google Cloud CLI if needed
curl https://sdk.cloud.google.com | bash
gcloud init

# Create new project (or use existing)
gcloud projects create your-project-id
gcloud config set project your-project-id
```

**Enable Required APIs:**
```bash
gcloud services enable sheets.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable drive.googleapis.com
```

**Create Service Account:**
```bash
gcloud iam service-accounts create store-data-service \
    --display-name="Store Data Collection Service"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:store-data-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:store-data-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/sheets.editor"

# Create and download key
gcloud iam service-accounts keys create credentials.json \
    --iam-account=store-data-service@your-project-id.iam.gserviceaccount.com
```

### 2. Development Setup

**Install dependencies:**
```bash
uv install
```

**Setup Google Cloud Storage:**
```bash
# Run the GCS setup helper
uv run python setup_gcs.py \
    --credentials credentials.json \
    --bucket your-store-data-bucket \
    --project your-project-id \
    --test \
    --sample-data
```

**Configure secrets:**
```bash
# Copy and update environment files
cp .env.example .env
# Edit .env with your bucket name and credentials

# Update Streamlit secrets
cp secrets.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your service account details
```

### 3. Google Sheets Setup

1. **Create a Google Sheets document** with these columns:
   - Store Name
   - Youvitarian/Employee
   - Date
   - Before Picture (URL)
   - After Picture (URL)
   - Timestamp

2. **Share the sheet** with your service account email:
   `store-data-service@your-project-id.iam.gserviceaccount.com`

### 4. Run the Application

**Development:**
```bash
uv run streamlit run app.py
```

**Production with Docker:**
```bash
docker-compose up --build
```

Access the application at: http://localhost:8501

## Development

### Code Quality

Run linting and formatting:

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy .
```

### Testing

```bash
uv run pytest
```

## Deployment

### Docker

```bash
# Build image
docker build -t store-data-platform .

# Run container
docker run -p 8501:8501 --env-file .env store-data-platform
```

### Docker Compose

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License
EOF

# Create basic test file
cat > tests/test_app.py << 'EOF'
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st

# Basic test structure - add more tests as needed
def test_app_imports():
    """Test that the app can be imported without errors"""
    try:
        import app
        assert True
    except ImportError:
        pytest.fail("Could not import app module")

def test_google_sheets_handler():
    """Test GoogleSheetsHandler initialization"""
    from app import GoogleSheetsHandler
    
    with patch('app.st.secrets', {}):
        handler = GoogleSheetsHandler()
        assert handler.gc is None
        assert handler.sheet is None
EOF

# Make scripts executable
chmod +x setup.sh

echo "✅ Setup complete!"
echo ""
echo "📁 Project structure created in: $(pwd)"