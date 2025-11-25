import { BaseAgent } from '../BaseAgent';
import { USER_PROFILING_AGENT_CONFIG } from '../configs';
import type { AgentTask, AgentResponse, AgentMessage } from '../types';
import { getToolsByAgent } from '../tools';
import { createLLMProvider } from '../llm/LLMProvider';
import type { LLMConfig } from '../llm/LLMProvider';

export class UserProfilingAgent extends BaseAgent {
    private llmProvider;

    constructor(providerConfig?: LLMConfig) {
        super(USER_PROFILING_AGENT_CONFIG);

        // Register tools
        const tools = getToolsByAgent('user_profiling');
        tools.forEach(tool => this.registerTool(tool));

        // Initialize LLM provider
        const defaultConfig: LLMConfig = {
            provider: 'gemini',
            model: 'gemini-flash-latest',
            temperature: 0.7,
            maxTokens: this.config.maxTokens
        };

        this.llmProvider = createLLMProvider(providerConfig || defaultConfig);
    }

    async processTask(task: AgentTask): Promise<AgentResponse> {
        this.setStatus('working');

        try {
            switch (task.type) {
                case 'analyze_behavior':
                    return await this.analyzeBehavior(task.input);
                case 'adapt_ui':
                    return await this.adaptUI(task.input);
                default:
                    return this.createResponse(false, `Unknown task type: ${task.type}`);
            }
        } catch (error) {
            this.setStatus('error');
            return this.createResponse(
                false,
                `Error processing task: ${error instanceof Error ? error.message : 'Unknown error'}`
            );
        } finally {
            this.setStatus('idle');
        }
    }

    async generateResponse(message: AgentMessage): Promise<AgentResponse> {
        // UserProfilingAgent typically works in background, but can respond to "how am I doing?"
        this.setStatus('thinking');

        try {
            this.addToHistory(message);

            const systemPrompt = `You are a User Profiling Agent.
      Your goal is to understand the user's expertise level (Novice, Intermediate, Expert) based on their interactions.
      You can suggest interface adaptations to make the experience better.`;

            const contextMessage = this.buildContextMessage();

            const messages = [
                { role: 'system' as const, content: systemPrompt },
                { role: 'user' as const, content: contextMessage },
                { role: 'user' as const, content: message.content }
            ];

            const llmResponse = await this.llmProvider.chat(messages, {
                temperature: 0.7,
                maxTokens: 300
            });

            return this.createResponse(
                true,
                llmResponse.content,
                undefined,
                ['Analyzed user interaction patterns'],
                0.9
            );

        } catch (error) {
            this.setStatus('error');
            return this.createResponse(
                false,
                `Error generating response: ${error instanceof Error ? error.message : 'Unknown error'}`
            );
        } finally {
            this.setStatus('idle');
        }
    }

    private async analyzeBehavior(input: any): Promise<AgentResponse> {
        const { interactionHistory, errorRate, timePerTask } = input;

        // Logic to determine user expertise
        let expertise = 'novice';
        if (errorRate < 0.1 && timePerTask < 60) {
            expertise = 'expert';
        } else if (errorRate < 0.3) {
            expertise = 'intermediate';
        }

        // Update internal state
        this.updateContext({ userExpertise: expertise });

        return this.createResponse(
            true,
            `User analysis complete. Estimated expertise: ${expertise}`,
            { expertise, confidence: 0.85 },
            ['Analyzed error rate and task time'],
            0.9
        );
    }

    private async adaptUI(input: any): Promise<AgentResponse> {
        const { currentMode, recommendedMode } = input;

        if (currentMode === recommendedMode) {
            return this.createResponse(true, 'No adaptation needed.', { adapted: false }, [], 1.0);
        }

        return this.createResponse(
            true,
            `Recommending UI switch from ${currentMode} to ${recommendedMode}.`,
            { adapted: true, newMode: recommendedMode },
            ['User performance suggests different mode'],
            0.95
        );
    }

    private buildContextMessage(): string {
        const { userProfile } = this.state.memory;
        return `Current User Mode: ${userProfile.preferences.mode}`;
    }
}
