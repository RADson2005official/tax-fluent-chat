import fs from 'fs';
import path from 'path';
import { runAllIntegrationTests } from '../src/agents/specialized/integration-test';

// Load .env manually
const envPath = path.resolve(process.cwd(), '.env');
if (fs.existsSync(envPath)) {
    const envConfig = fs.readFileSync(envPath, 'utf8');
    envConfig.split('\n').forEach(line => {
        const trimmedLine = line.trim();
        if (!trimmedLine || trimmedLine.startsWith('#')) return;

        const match = trimmedLine.match(/^([^=]+)=(.*)$/);
        if (match) {
            const key = match[1].trim();
            const value = match[2].trim().replace(/^["']|["']$/g, ''); // Remove quotes if present
            process.env[key] = value;
        }
    });
    console.log('Loaded .env file');
    console.log('VITE_OPENAI_API_KEY:', process.env.VITE_OPENAI_API_KEY ? process.env.VITE_OPENAI_API_KEY.substring(0, 5) + '...' : 'MISSING');
    console.log('VITE_GEMINI_API_KEY:', process.env.VITE_GEMINI_API_KEY ? process.env.VITE_GEMINI_API_KEY.substring(0, 5) + '...' : 'MISSING');
} else {
    console.log('.env file not found at:', envPath);
}

runAllIntegrationTests().catch(err => {
    console.error(err);
    process.exit(1);
});
