# Tax Fluent Chat

A modern, AI-powered tax assistance chat application built with Vue.js 3. This application provides an intuitive interface for users to get answers to their tax-related questions with the help of an integrated LLM-powered tax knowledge base.

## Features

- 💬 Interactive chat interface for tax-related queries
- 📚 Comprehensive 2024 tax knowledge base
- 🎨 Modern, responsive UI built with Tailwind CSS
- ⚡ Fast development experience with Vite
- 🔄 State management with Pinia
- 🎯 Type-safe development with TypeScript

## Getting Started

### Prerequisites

- Node.js (version 16 or higher recommended)
- npm or bun package manager

### Installation

1. Clone the repository:
```sh
git clone https://github.com/RADson2005official/tax-fluent-chat.git
cd tax-fluent-chat
```

2. Install dependencies:
```sh
npm install
# or
bun install
```

3. Start the development server:
```sh
npm run dev
# or
bun run dev
```

The application will be available at `http://localhost:8080`

### Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview the production build
- `npm run lint` - Run ESLint to check code quality


## Tech Stack

This project is built with modern web technologies:

- **[Vite](https://vitejs.dev/)** - Fast build tool and development server
- **[Vue.js 3](https://vuejs.org/)** - Progressive JavaScript framework
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript
- **[Pinia](https://pinia.vuejs.org/)** - Intuitive Vue state management
- **[Vue Router](https://router.vuejs.org/)** - Official router for Vue.js
- **[Radix Vue](https://www.radix-vue.com/)** - Unstyled, accessible UI components
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[React](https://react.dev/)** - Used for some UI components (via Radix UI)

## Project Structure

```
tax-fluent-chat/
├── public/                      # Static assets
│   └── llm-tax-knowledge.txt   # Tax knowledge base for LLMs
├── src/
│   ├── components/             # Reusable Vue components
│   │   ├── ui/                # UI component library
│   │   └── ...                # Feature-specific components
│   ├── pages/                 # Page components
│   ├── stores/                # Pinia state stores
│   ├── composables/           # Vue composition functions
│   ├── data/                  # Data utilities and helpers
│   ├── App.vue                # Root component
│   ├── main.ts                # Application entry point
│   └── router.ts              # Route configuration
├── index.html                 # HTML entry point
├── package.json               # Project dependencies
├── vite.config.ts             # Vite configuration
├── tailwind.config.ts         # Tailwind configuration
└── tsconfig.json              # TypeScript configuration
```

## Tax Knowledge Base

This project includes a comprehensive tax knowledge file that can be accessed by Large Language Models (LLMs) to provide accurate tax assistance.

### Accessing the Knowledge Base

**File Location**: `/public/llm-tax-knowledge.txt`  
**Development URL**: `http://localhost:8080/llm-tax-knowledge.txt`

The knowledge base includes:
- 2024 tax year information
- Tax brackets and filing status details
- Credits and deductions (Child Tax Credit, EITC, etc.)
- Business and self-employment tax guidance
- Common tax scenarios and calculations
- Filing requirements and important dates

### For Developers

If you need to programmatically access the tax knowledge in your code, you can use TypeScript helper functions:

```typescript
import { fetchTaxKnowledge, extractTaxSection } from '@/data/tax-knowledge';

// Fetch the complete tax knowledge
const taxData = await fetchTaxKnowledge();

// Extract specific sections
const creditInfo = extractTaxSection(taxData, 'CREDITS AND DEDUCTIONS');
```

### For LLM Integration

LLMs can access the knowledge base directly via HTTP GET request to `/llm-tax-knowledge.txt` for comprehensive tax information to assist users with tax-related questions.

## Development Workflow

### Local Development

1. Make changes to the code in the `src/` directory
2. The development server will automatically reload with your changes
3. Test your changes in the browser at `http://localhost:8080`

### Building for Production

```sh
npm run build
```

This will create an optimized production build in the `dist/` directory.

### Preview Production Build

```sh
npm run preview
```

This allows you to preview the production build locally before deployment.

## Deployment

This application can be deployed to various hosting platforms that support static sites:

### Vercel

1. Push your code to GitHub
2. Import your repository on [Vercel](https://vercel.com)
3. Vercel will automatically detect the Vite configuration
4. Deploy with one click

### Netlify

1. Push your code to GitHub
2. Connect your repository on [Netlify](https://netlify.com)
3. Build command: `npm run build`
4. Publish directory: `dist`

### GitHub Pages

1. Build the project: `npm run build`
2. Deploy the `dist` folder to GitHub Pages

## Contributing

Contributions are welcome! If you'd like to contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For questions or support, please open an issue in the GitHub repository.

## Acknowledgments

- Tax knowledge base compiled from IRS official documentation
- UI components powered by Radix Vue
- Built with modern web technologies and best practices
