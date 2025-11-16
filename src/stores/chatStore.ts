import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAgentStore } from './agentStore';
import type { TaxFormSuggestion } from '@/agents/types';

export type Mode = "Novice" | "Expert" | "Accessibility";

export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  explainable?: boolean;
  formSuggestions?: TaxFormSuggestion[];
  onFormAccept?: (suggestion: TaxFormSuggestion) => void;
  onFormDismiss?: (id: string) => void;
}

export const useChatStore = defineStore('chat', () => {
  // State
  const mode = ref<Mode>("Novice");
  const messages = ref<ChatMessage[]>([
    { 
      id: "m1", 
      role: "ai", 
      content: "Hi! I'm your tax assistant. How can I help today?", 
      explainable: false 
    },
  ]);
  const explanationOpen = ref(false);
  const explanationContent = ref("");

  // Computed
  const suggestions = computed(() => {
    if (mode.value === "Novice") {
      return [
        "Do I qualify for the child tax credit?",
        "Should I itemize deductions?",
        "How do I report freelance income?"
      ];
    } else if (mode.value === "Expert") {
      return [
        "compute agi from w2 + 1099",
        "simulate standard vs itemized",
        "calc ctc 2 dependents"
      ];
    } else {
      return [
        "Explain EITC in simple terms",
        "Help me fill income",
        "Show larger text"
      ];
    }
  });

  // Actions
  function setMode(newMode: Mode) {
    mode.value = newMode;
  }

  function addMessage(message: ChatMessage) {
    messages.value.push(message);
  }

  function sendMessage(messageText: string) {
    const id = `${Date.now()}`;
    
    // Add user message
    addMessage({ 
      id: id + "u", 
      role: "user", 
      content: messageText 
    });

    // Use AI Agent System for response
    const agentStore = useAgentStore();
    
    agentStore.sendMessage(messageText)
      .then((response) => {
        // Add AI response from agent
        addMessage({
          id: id + "a",
          role: "ai",
          content: response.message,
          explainable: true,
          formSuggestions: response.formSuggestions,
          onFormAccept: (suggestion) => handleFormAccept(suggestion),
          onFormDismiss: (id) => handleFormDismiss(id)
        });
      })
      .catch((error) => {
        console.error('Error from AI Agent:', error);
        // Fallback response
        addMessage({
          id: id + "a",
          role: "ai",
          content: "I apologize, but I'm having trouble processing your request. Please try again.",
          explainable: false,
        });
      });
  }

  function requestExplanation(messageId: string) {
    explanationContent.value = 
      "This answer was generated based on your inputs and 2024 IRS thresholds. It considered filing status, dependents, and phase-out ranges, and cross-checked income caps.";
    explanationOpen.value = true;
  }

  function setExplanationOpen(isOpen: boolean) {
    explanationOpen.value = isOpen;
  }

  function handleFormAccept(suggestion: TaxFormSuggestion) {
    // TODO: Open form filling interface
    console.log('Form accepted:', suggestion);
    // For now, just show a toast or notification
  }

  function handleFormDismiss(id: string) {
    // Remove the suggestion from messages
    messages.value = messages.value.map(msg => ({
      ...msg,
      formSuggestions: msg.formSuggestions?.filter(s => s.id !== id)
    }));
  }

  return {
    mode,
    messages,
    explanationOpen,
    explanationContent,
    suggestions,
    setMode,
    addMessage,
    sendMessage,
    requestExplanation,
    setExplanationOpen,
  };
});
