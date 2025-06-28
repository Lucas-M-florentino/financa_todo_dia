# FastAPI Backend

A FastAPI backend application with proper structure and configuration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy .env.example to .env and configure your environment variables:
```bash
cp .env.example .env
```

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI application
│   ├── api/             # API routes
│   ├── core/            # Core configurations
│   ├── models/          # Database models
│   └── services/        # Business logic
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # Project documentation
```
