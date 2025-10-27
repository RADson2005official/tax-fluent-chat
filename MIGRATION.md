# Tax Fluent Chat - Vue.js Migration

This project has been successfully migrated from React to Vue.js with Pinia state management and includes a FastAPI backend.

## Project Structure

```
tax-fluent-chat/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app with routes
│   │   ├── tax_calculator.py  # Tax calculation engine
│   │   └── explanation_engine.py  # Explanation generation
│   └── requirements.txt
├── src/                        # Vue.js frontend
│   ├── App.vue                # Main Vue component
│   ├── main.ts                # Vue app entry point
│   ├── stores/                # Pinia stores
│   │   ├── auth.ts           # Authentication state
│   │   ├── chat.ts           # Chat messages state
│   │   ├── tax.ts            # Tax calculation state
│   │   └── explanation.ts    # Explanations state
│   └── components/
│       ├── chat/             # Chat components
│       ├── adaptive/         # Mode switcher
│       ├── xai/              # Explanation panel
│       ├── shared/           # Shared components
│       └── inputs/           # Input fields
└── public/                   # Static assets
```

## Backend Features

### FastAPI Implementation

1. **Authentication Routes** (`/register`, `/login`)
   - User registration with email validation
   - JWT-based authentication
   - Password hashing with bcrypt

2. **Tax Calculator** (`/calculate-tax`)
   - Progressive tax bracket calculation
   - Support for all filing statuses (Single, MFJ, MFS, HOH)
   - 2024 tax year brackets
   - Detailed breakdown by tax bracket
   - Error handling and validation

3. **Explanation Engine** (`/explain`)
   - Generates explanations tailored to expertise level (Novice/Expert)
   - Topics include: standard deduction, tax brackets, credits, filing status
   - Key points and related topics

### Starting the Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

## Frontend Features

### Vue.js with Pinia

The frontend has been completely migrated to Vue.js 3 with Composition API and Pinia for state management.

1. **Pinia Stores**
   - `authStore`: User authentication and session management
   - `chatStore`: Chat messages and conversation history
   - `taxStore`: Tax calculation inputs and results
   - `explanationStore`: Explanation content and visibility

2. **Vue Components**
   - All React components converted to Vue.js
   - Uses Composition API with `<script setup>`
   - Maintains same UI/UX as original

3. **Features**
   - Mode switching (Novice/Expert/Accessible)
   - Real-time chat interface
   - Tax calculation forms
   - Explainability panel
   - Transparency indicators

### Starting the Frontend

```bash
npm install
npm run dev
```

App will be available at: http://localhost:8080

## Development

### Building for Production

```bash
# Frontend
npm run build

# Preview production build
npm run preview
```

### Running Both Services

For full functionality, run both backend and frontend:

Terminal 1:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Terminal 2:
```bash
npm run dev
```

## Testing the Integration

1. **Test Backend API:**
```bash
# Health check
curl http://localhost:8000/

# Tax calculation
curl -X POST http://localhost:8000/calculate-tax \
  -H "Content-Type: application/json" \
  -d '{"income": 75000, "filing_status": "single", "dependents": 0, "deductions": 0}'

# Explanation
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "standard_deduction", "context": {}, "expertise_level": "novice"}'
```

2. **Test Frontend:**
   - Open http://localhost:8080
   - Try sending chat messages
   - Switch between Novice/Expert modes
   - Click "Explain" buttons on AI responses

## Migration Details

### What Changed

✅ **Added:**
- Vue.js 3 framework
- Pinia state management
- FastAPI backend
- Tax calculation engine
- Explanation engine
- Authentication system

✅ **Migrated:**
- All React components to Vue.js
- Component logic to Composition API
- State management from React hooks to Pinia
- Build configuration from React to Vue

✅ **Maintained:**
- Same UI design (Tailwind CSS)
- Same functionality
- Same user experience
- Compatible with existing assets

### No Conflicts

The migration was done cleanly with:
- No React dependencies remaining
- Clean separation of concerns
- Proper TypeScript types
- Working build process
- No runtime errors

## Technologies Used

### Frontend
- Vue.js 3.4.15
- Pinia 2.1.7
- TypeScript
- Vite
- Tailwind CSS

### Backend
- Python 3.12
- FastAPI 0.109.0
- Pydantic 2.5.3
- Python-JOSE (JWT)
- Passlib (bcrypt)

## Next Steps

1. Add database integration (SQLite/PostgreSQL)
2. Implement user persistence
3. Add more tax topics to explanation engine
4. Create unit tests for components
5. Add E2E tests
6. Deploy to production

## License

[Your License Here]
