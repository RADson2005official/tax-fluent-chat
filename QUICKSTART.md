# Quick Start Guide - Tax Fluent Chat

This guide will help you get the application running in 5 minutes.

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

## Step 1: Start the Backend (Terminal 1)

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python run.py
```

✅ Backend will be running at `http://localhost:8000`
📚 API docs available at `http://localhost:8000/docs`

## Step 2: Start the Frontend (Terminal 2)

```bash
# Navigate to frontend directory (in a new terminal)
cd vue-frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

✅ Frontend will be running at `http://localhost:5173`

## Step 3: Use the Application

1. Open `http://localhost:5173` in your browser
2. **Register a new account:**
   - Click "Register" (or it defaults to registration)
   - Enter email, username, password
   - Click "Register" button
   - You'll be logged in automatically

3. **Select your proficiency level:**
   - Choose: Beginner 🌱, Intermediate 🌿, or Expert 🌳
   - The form will adapt to your level

4. **Enter tax information:**
   - **Beginner**: Simple fields (income, filing status, dependents)
   - **Intermediate**: + additional deductions
   - **Expert**: + state field

5. **Calculate taxes:**
   - Click "Calculate Tax"
   - View results in the dashboard on the right

6. **Get explanations:**
   - Click "Explain Results" button
   - Read adaptive explanations based on your proficiency
   - Switch proficiency levels in the panel to see different explanations
   - Click on technical terms to learn more

## Example Usage

### Test with Sample Data

**Novice User:**
- Proficiency: Beginner
- Income: $75,000
- Filing Status: Single
- Dependents: 0

**Expected Result:**
- Federal Tax: $8,341.00
- Effective Rate: 11.12%
- Marginal Rate: 22%
- Tax Bracket: $47,150 - $100,525

### Try Different Scenarios

**Married with Children:**
- Income: $120,000
- Filing Status: Married Filing Jointly
- Dependents: 2

**Expert Mode:**
- Income: $250,000
- Filing Status: Head of Household
- Dependents: 1
- Deductions: $25,000
- State: CA

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Kill the process
lsof -ti:5173 | xargs kill -9
```

**Dependencies issues:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Cannot connect to backend:**
- Ensure backend is running on port 8000
- Check `vite.config.ts` proxy configuration
- Look for CORS errors in browser console

## API Testing (Optional)

Test the backend directly with curl:

```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "username": "testuser", "password": "test123"}'

# Calculate tax
curl -X POST "http://localhost:8000/tax/calculate" \
  -H "Content-Type: application/json" \
  -d '{"income": 75000, "filing_status": "single", "dependents": 0, "deductions": 0}'

# Get explanation
curl -X POST "http://localhost:8000/explain/" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AGI?", "proficiency": "novice"}'
```

## Features Overview

### Implemented Tasks

✅ **Task A**: Authentication (Register/Login with JWT)
✅ **Task B**: Tax Calculator (Progressive brackets, error handling)
✅ **Task C**: Explanation Engine (Novice/Intermediate/Expert responses)
✅ **Task D**: AdaptiveForm.vue (Fields change by proficiency)
✅ **Task E**: ExplanationPanel.vue (Adaptive text from API)
✅ **Task F**: Dashboard.vue (Tax summaries and visualizations)

### Proficiency Levels

- **Novice**: Simple language, helpful tooltips, basic fields
- **Intermediate**: Technical terms, more fields, moderate detail
- **Expert**: Jargon, all fields, compact interface, advanced explanations

## Next Steps

1. Try all three proficiency levels
2. Test different filing statuses
3. Explore explanations for various tax terms
4. Check the API documentation at `/docs`
5. Review the comprehensive README files

## Support

For detailed documentation:
- Backend: `backend/README.md`
- Frontend: `vue-frontend/README.md`
- Project Overview: `PROJECT_README.md`

## Security Note

This is a development setup. For production:
- Use environment variables for secrets
- Implement proper database (not in-memory)
- Configure CORS for your domain
- Use HTTPS
- Add email verification
- Implement rate limiting
