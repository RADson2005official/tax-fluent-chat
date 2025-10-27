# Tax Fluent Chat Backend

FastAPI backend for Tax Fluent Chat with progressive tax calculation, authentication, and adaptive explanations.

## Features

- **Task A**: Authentication routes (`/auth/register`, `/auth/login`) with JWT tokens
- **Task B**: Tax calculator with progressive slab logic and comprehensive error handling
- **Task C**: Explanation engine generating novice/intermediate/expert responses

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running the Server

```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Tax Calculation
- `POST /tax/calculate` - Calculate federal taxes
- `GET /tax/brackets/{filing_status}` - Get tax bracket information

### Explanations
- `POST /explain` - Get adaptive explanations
- `GET /explain/topics` - List available topics

## Example Usage

### Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword"
  }'
```

### Calculate Taxes
```bash
curl -X POST "http://localhost:8000/tax/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "income": 75000,
    "filing_status": "single",
    "dependents": 0,
    "deductions": 0,
    "state": "CA"
  }'
```

### Get Explanation
```bash
curl -X POST "http://localhost:8000/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is AGI?",
    "proficiency": "novice",
    "context": {}
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── models/           # Pydantic models
│   ├── routes/           # API routes (auth, tax, explain)
│   ├── services/         # Business logic (tax_calculator, explanation_engine)
│   ├── utils/            # Utilities (auth helpers)
│   └── main.py          # FastAPI app
├── requirements.txt     # Python dependencies
└── run.py              # Server runner
```

## Security Notes

- The SECRET_KEY in `utils/auth.py` should be changed and stored in environment variables for production
- Currently uses in-memory user storage; replace with a proper database for production
- CORS is configured for development; adjust for production deployment
