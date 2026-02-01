# AutoMerge AI - Django REST API

![Django REST Framework](https://img.shields.io/badge/Django-REST%20Framework-green)
![PyTorch](https://img.shields.io/badge/PyTorch-1.13+-red)
![Transformers](https://img.shields.io/badge/🤗-Transformers-yellow)
![License](https://img.shields.io/badge/License-MIT-blue)

A production-ready Django REST API for automatically resolving Git merge conflicts using the `ankit-ml11/code-t5-merge-resolver` Hugging Face model. This API intelligently resolves merge conflicts in multiple programming languages with sub-second response times.

## ✨ Features

- **🚀 Fast Conflict Resolution**: ~0.26s average response time
- **🌐 Multi-language Support**: Python, JavaScript, Java, C++, Go, Ruby, PHP
- **📦 Batch Processing**: Resolve multiple conflicts in a single request
- **🔍 Intelligent Merging**: Chooses best version based on code structure and comments
- **✅ Production Ready**: Proper error handling, validation, and health checks
- **⚡ High Performance**: Optimized model loading with singleton pattern

## 🏗️ Architecture
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Django REST │────▶│ AutoMerge AI │────▶│ Hugging Face │
│ API │ │ Merge Resolver │ │ CodeT5 Model │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
▼ ▼ ▼
REST Endpoints Conflict Parsing Model Inference
(JSON responses) (Base/Ours/Theirs) (Text-to-Text Gen.)


## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git
- pip (Python package manager)

### Installation and running the server

1. **Clone the repository and create virtual environment**
```bash
git clone https://github.com/ankitadhi/automerge-ai.git
cd automerge-ai

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Apply migrations
cd ai_modoel
python manage.py makemigrations
python manage.py migrate

#Run the server
python manage.py runserver

```
### 🔧 API Endpoints
```
 Base URL: http://localhost:8000/predictor/

 1.  Health Check ✅
 GET Base_URL/health/

 2. Single Conflict Resolution 🔄
 POST Base_URL/resolve/

 3. Batch Conflict Resolution 📦
POST Base_UR/resolve/batch/
```
### Command Line test using curl 
```
# Health check
curl http://localhost:8000/predictor/health/

# Resolve single conflict
curl -X POST http://localhost:8000/predictor/resolve/ \
  -H "Content-Type: application/json" \
  -d '{
    "conflict_text": "<<<<<<< HEAD\\nprint(\\"hello\\")\\n=======\\nprint(\\"world\\")\\n>>>>>>>",
    "language": "python"
  }'

# Batch resolve
curl -X POST http://localhost:8000/predictor/resolve/batch/ \
  -H "Content-Type: application/json" \
  -d '{
    "conflicts": [
      "<<<<<<< HEAD\\nx=1\\n=======\\nx=2\\n>>>>>>>",
      "<<<<<<< HEAD\\ny=3\\n=======\\ny=4\\n>>>>>>>"
    ]
  }'
  ```
