import fs from 'fs';
import path from 'path';

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
            const value = match[2].trim().replace(/^["']|["']$/g, '');
            process.env[key] = value;
        }
    });
}

const apiKey = process.env.VITE_GEMINI_API_KEY;
console.log('Testing Gemini API with key:', apiKey ? apiKey.substring(0, 5) + '...' : 'MISSING');

if (!apiKey) {
    console.error('No API key found!');
    process.exit(1);
}

async function testModel(modelName: string) {
    console.log(`\nTesting model: ${modelName}`);
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: 'Hello, are you working?' }] }]
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('✅ Success!');
            console.log('Response:', data.candidates?.[0]?.content?.parts?.[0]?.text);
            return true;
        } else {
            const error = await response.json();
            console.log('❌ Failed:', response.status, response.statusText);
            console.log('Error details:', JSON.stringify(error, null, 2));
            return false;
        }
    } catch (e) {
        console.error('Request error:', e);
        return false;
    }
}

async function listModels() {
    console.log('\nListing available models...');
    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;
    try {
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            console.log('Available models:');
            data.models?.forEach((m: any) => {
                if (m.name.includes('gemini')) {
                    console.log(`- ${m.name} (${m.supportedGenerationMethods?.join(', ')})`);
                }
            });
        } else {
            console.log('Failed to list models:', response.status);
        }
    } catch (e) {
        console.error('Error listing models:', e);
    }
}

async function run() {
    await listModels();

    const modelsToTest = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-001',
        'gemini-1.5-flash-latest',
        'gemini-pro',
        'gemini-1.0-pro'
    ];

    for (const model of modelsToTest) {
        await testModel(model);
    }
}

run();
