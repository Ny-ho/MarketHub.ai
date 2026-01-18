# MarketHub.ai - Local AI Version

Run the full MarketHub.ai with AI salary prediction on your local machine.

## Requirements
- Python 3.10, 3.11, or 3.12 (recommended: 3.11)
- 4GB+ RAM (AI model needs ~2GB)
- 3GB disk space

## Quick Start

### 1. Install Python
Download from: https://www.python.org/downloads/
Check "Add Python to PATH" during installation.

### 2. Open Terminal
- Windows: Open Command Prompt or PowerShell
- Mac/Linux: Open Terminal

Navigate to this folder:
```bash
cd path/to/MarketHub-AI-Local
```

### 3. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements_local.txt
```
This will take 5-10 minutes (downloads AI model).

### 5. Run the App
```bash
# Use main_local.py (has AI enabled)
uvicorn main_local:app --reload
```

### 6. Open in Browser
Go to: http://127.0.0.1:8000

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Web Interface |
| `/jobs` | Job listings |
| `/users` | User registration |
| `/login` | Authentication |
| `/predict_salary` | **AI Salary Prediction** |
| `/docs` | API Documentation |

## AI Salary Prediction

The first prediction request will take ~30 seconds (loading AI model).
Subsequent requests are instant.

### Example Request:
```bash
curl -X POST http://127.0.0.1:8000/predict_salary \
  -H "Content-Type: application/json" \
  -d '{"title":"Software Engineer","location":"New York","years_of_experience":5,"tech_stack":"Python","seniority":"Senior","company_size":"Large"}'
```

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements_local.txt
```

**Port already in use:**
```bash
uvicorn main_local:app --reload --port 8001
```

**Out of memory:**
Close other applications. AI model needs ~2GB RAM.

## Files Included
- `main_local.py` - Server with AI enabled
- `requirements_local.txt` - All dependencies
- `salary_model.pkl` - ML model for predictions
- `static/` - Frontend files
- `database.py`, `models.py`, `security.py` - Core modules
