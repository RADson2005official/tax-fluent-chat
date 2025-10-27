# Tax Fluent Chat - Vue Frontend

Vue 3 + TypeScript + Pinia frontend for Tax Fluent Chat.

## Features

### Implemented Tasks

- **Task D: AdaptiveForm.vue** - Dynamic form that changes fields based on proficiency mode
  - Novice: Simple labels, helpful descriptions
  - Intermediate: More fields, technical terminology
  - Expert: All fields, compact labels, advanced options

- **Task E: ExplanationPanel.vue** - Adaptive explanations from API
  - Fetches explanations based on user proficiency
  - Shows technical terms and related topics
  - Allows switching between proficiency levels

- **Task F: Dashboard.vue** - Tax calculation display
  - Visual breakdown of tax calculation
  - Detailed summary with rates and deductions
  - Interactive explanations

### State Management (Pinia)

- **authStore**: User authentication state
- **taxStore**: Tax calculation state and proficiency level

## Installation

```bash
cd vue-frontend
npm install
```

## Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Building

```bash
npm run build
```

## Project Structure

```
vue-frontend/
├── src/
│   ├── components/
│   │   ├── AdaptiveForm.vue       # Task D: Adaptive form
│   │   ├── ExplanationPanel.vue   # Task E: Explanation panel
│   │   ├── Dashboard.vue          # Task F: Tax dashboard
│   │   ├── AuthForm.vue           # Authentication
│   │   └── ProficiencySwitcher.vue
│   ├── stores/
│   │   ├── auth.ts               # Auth state management
│   │   └── tax.ts                # Tax state management
│   ├── views/
│   │   ├── Home.vue              # Main application view
│   │   └── Auth.vue              # Authentication view
│   ├── router/
│   │   └── index.ts              # Vue Router config
│   ├── composables/
│   │   └── useAPI.ts             # API client
│   ├── types/
│   │   └── api.ts                # TypeScript types
│   ├── App.vue
│   └── main.ts
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` via proxy configuration in `vite.config.ts`.

All API calls use the `/api` prefix which is proxied to the backend.

## Key Features

### Proficiency Modes

The application adapts to three proficiency levels:

1. **Novice (Beginner)**
   - Simple language
   - Helpful tooltips
   - Basic fields only
   - Detailed explanations

2. **Intermediate**
   - More technical terms
   - Additional fields (deductions)
   - Moderate detail

3. **Expert**
   - Technical jargon
   - All fields (including state)
   - Compact interface
   - Advanced explanations

### Authentication

- JWT-based authentication
- Login and registration
- Protected routes
- Token stored in localStorage

### Tax Calculation

- Real-time calculation via API
- Progressive tax brackets
- Deduction handling
- Visual breakdown

### Explanations

- Context-aware explanations
- Proficiency-based content
- Technical term lookup
- Related topics navigation

## Usage

1. Start the backend server (see backend/README.md)
2. Start the Vue frontend: `npm run dev`
3. Register a new account or login
4. Select your proficiency level
5. Fill in tax information
6. Calculate taxes
7. View results in dashboard
8. Click "Explain Results" for detailed explanations
