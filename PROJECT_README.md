# Tax Fluent Chat - Full Stack Application

A complete tax assistance application with adaptive UI and explainable AI, built with Vue.js + Pinia frontend and FastAPI backend.

## 🎯 Project Overview

This application provides an intelligent, adaptive tax calculation and explanation system that adjusts its complexity based on user proficiency level (Novice, Intermediate, Expert).

### Key Features

- **Adaptive UI**: Interface adapts to user proficiency (beginner, intermediate, expert)
- **Progressive Tax Calculation**: Accurate 2024 federal tax calculations with progressive brackets
- **Explainable AI**: Context-aware explanations tailored to user knowledge level
- **JWT Authentication**: Secure user registration and login
- **Real-time Calculations**: Instant tax calculations with detailed breakdowns
- **Visual Dashboard**: Interactive charts and summaries

## 🏗️ Architecture

### Backend (FastAPI)
Located in `/backend` directory

**Implemented Features:**
- ✅ **Task A**: Authentication routes (`/auth/register`, `/auth/login`) with JWT tokens
- ✅ **Task B**: Tax calculator with progressive slab logic and comprehensive error handling
- ✅ **Task C**: Explanation engine generating novice/intermediate/expert responses

**Technologies:**
- FastAPI 0.115.5
- Pydantic for data validation
- Python-JOSE for JWT tokens
- Passlib for password hashing
- Uvicorn for ASGI server

### Frontend (Vue.js)
Located in `/vue-frontend` directory

**Implemented Features:**
- ✅ **Task D**: AdaptiveForm.vue - Dynamic form that changes fields based on proficiency
- ✅ **Task E**: ExplanationPanel.vue - Adaptive explanations from API
- ✅ **Task F**: Dashboard.vue - Tax calculation display with visual breakdowns

**Technologies:**
- Vue 3.5.13
- Pinia 2.3.0 (state management)
- Vue Router 4.5.0
- TypeScript 5.8.3
- Vite 5.4.19
- Axios 1.12.0 (API client)

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or bun

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python run.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd vue-frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

## 📁 Project Structure

```
tax-fluent-chat/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API routes (auth, tax, explain)
│   │   ├── services/          # Business logic
│   │   │   ├── tax_calculator.py      # Task B: Progressive tax calculation
│   │   │   └── explanation_engine.py  # Task C: Adaptive explanations
│   │   ├── utils/             # Utilities (auth helpers)
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                # Server runner
│   └── README.md
│
├── vue-frontend/              # Vue.js Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdaptiveForm.vue       # Task D: Adaptive form
│   │   │   ├── ExplanationPanel.vue   # Task E: Explanation panel
│   │   │   ├── Dashboard.vue          # Task F: Tax dashboard
│   │   │   ├── AuthForm.vue           # Authentication
│   │   │   └── ProficiencySwitcher.vue
│   │   ├── stores/            # Pinia stores
│   │   │   ├── auth.ts       # Auth state management
│   │   │   └── tax.ts        # Tax state management
│   │   ├── views/            # Page views
│   │   ├── router/           # Vue Router config
│   │   ├── composables/      # API client
│   │   └── types/            # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
└── README.md                  # This file
```

## 🔐 Security

- JWT-based authentication with secure password hashing (bcrypt)
- All dependencies scanned for vulnerabilities and patched:
  - ✅ python-jose updated to 3.4.0 (CVE fixed)
  - ✅ axios updated to 1.12.0 (CVE fixed)
- CORS configured for development (adjust for production)
- Secret keys use environment variables in production

## 🎨 Proficiency Modes

### Novice (Beginner)
- Simple language and labels
- Helpful tooltips and descriptions
- Basic fields only (income, filing status, dependents)
- Detailed, easy-to-understand explanations

### Intermediate
- More technical terminology
- Additional fields (deductions)
- Moderate detail level
- Balance between clarity and precision

### Expert
- Technical jargon and abbreviations
- All fields including state taxes
- Compact interface
- Advanced explanations with technical details

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Tax Calculation
- `POST /tax/calculate` - Calculate federal taxes
- `GET /tax/brackets/{filing_status}` - Get tax bracket information

### Explanations
- `POST /explain` - Get adaptive explanations
- `GET /explain/topics` - List available topics

## 🧪 Testing

### Backend Tests
```bash
cd backend
# Test registration
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "pass123"}'

# Test tax calculation
curl -X POST "http://localhost:8000/tax/calculate" \
  -H "Content-Type: application/json" \
  -d '{"income": 75000, "filing_status": "single", "dependents": 0, "deductions": 0}'
```

### Frontend
```bash
cd vue-frontend
npm run lint
npm run build
```

## 🚢 Deployment

### Backend
- Use environment variables for SECRET_KEY
- Replace in-memory user storage with a database (PostgreSQL, MongoDB, etc.)
- Configure CORS for production domains
- Use a production ASGI server (e.g., Gunicorn + Uvicorn)

### Frontend
- Build production bundle: `npm run build`
- Deploy to static hosting (Netlify, Vercel, etc.)
- Update API proxy configuration for production backend URL

## 📝 License

This project is for educational purposes.

## 👥 Contributors

Built as part of the Tax Fluent Chat project.

## 📚 Documentation

- [Backend README](backend/README.md) - Detailed backend documentation
- [Frontend README](vue-frontend/README.md) - Detailed frontend documentation
- [API Docs](http://localhost:8000/docs) - Interactive API documentation (when running)

## 🐛 Known Limitations

- User data is stored in-memory (backend) - implement proper database for production
- No email verification for registration
- State tax calculation is placeholder - needs implementation
- PDF export and share features are placeholders

## 🔮 Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- Email verification
- State tax calculations
- PDF export functionality
- Social sharing
- Multi-year tax comparison
- Tax optimization suggestions
- Mobile app (React Native/Flutter)
