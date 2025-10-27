# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/342d33b1-7401-43c5-83ce-887fada4e7b0

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/342d33b1-7401-43c5-83ce-887fada4e7b0) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## LLM Tax Knowledge Base

This project includes a comprehensive tax knowledge file that can be accessed by Large Language Models (LLMs) to provide accurate tax assistance:

**File Location**: `/public/llm-tax-knowledge.txt`  
**Access URL**: `http://localhost:8080/llm-tax-knowledge.txt` (when running locally)

The knowledge base includes:
- 2024 tax year information
- Tax brackets and filing status details
- Credits and deductions (Child Tax Credit, EITC, etc.)
- Business and self-employment tax guidance
- Common tax scenarios and calculations
- Filing requirements and important dates

### For Developers

Use the TypeScript helper functions in `src/data/tax-knowledge.ts`:

```typescript
import { fetchTaxKnowledge, extractTaxSection } from '@/data/tax-knowledge';

// Fetch the complete tax knowledge
const taxData = await fetchTaxKnowledge();

// Extract specific sections
const creditInfo = extractTaxSection(taxData, 'CREDITS AND DEDUCTIONS');
```

### For LLMs

Access the knowledge base directly via HTTP GET request to `/llm-tax-knowledge.txt` for comprehensive tax information to assist users with tax-related questions.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- Vue.js 3
- Pinia (State Management)
- Vue Router
- Radix Vue (UI Components)
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/342d33b1-7401-43c5-83ce-887fada4e7b0) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
