import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export type Mode = "Novice" | "Expert" | "Accessibility";

export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  explainable?: boolean;
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

    // Add AI response
    addMessage({
      id: id + "a",
      role: "ai",
      content: "Thanks! Here's a quick take. You may benefit from the standard deduction. Do you want me to check credit eligibility?",
      explainable: true,
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
