import { useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import ChatWindow from "@/components/chat/ChatWindow";
import MessageBubble, { ChatMessage } from "@/components/chat/MessageBubble";
import InputBar from "@/components/chat/InputBar";
import ModeSwitcher, { Mode } from "@/components/adaptive/ModeSwitcher";
import ExplanationPanel from "@/components/xai/ExplanationPanel";
import TransparencyIndicator from "@/components/shared/TransparencyIndicator";
import IntelligentField from "@/components/inputs/IntelligentField";
import DynamicLayoutContainer from "@/components/dynamic/DynamicLayoutContainer";

const Index = () => {
  const [mode, setMode] = useState<Mode>("Novice");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: "m1", role: "ai", content: "Hi! I’m your tax assistant. How can I help today?", explainable: false },
  ]);
  const [explanationOpen, setExplanationOpen] = useState(false);
  const [explanationContent, setExplanationContent] = useState("");

  const suggestions = useMemo(() => (
    mode === "Novice"
      ? ["Do I qualify for the child tax credit?", "Should I itemize deductions?", "How do I report freelance income?"]
      : mode === "Expert"
      ? ["compute agi from w2 + 1099", "simulate standard vs itemized", "calc ctc 2 dependents"]
      : ["Explain EITC in simple terms", "Help me fill income", "Show larger text"]
  ), [mode]);

  const requestExplain = (id: string) => {
    setExplanationContent(
      "This answer was generated based on your inputs and 2024 IRS thresholds. It considered filing status, dependents, and phase-out ranges, and cross-checked income caps."
    );
    setExplanationOpen(true);
  };

  const onSend = (message: string) => {
    const id = `${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      { id: id + "u", role: "user", content: message },
      {
        id: id + "a",
        role: "ai",
        content: "Thanks! Here’s a quick take. You may benefit from the standard deduction. Do you want me to check credit eligibility?",
        explainable: true,
      },
    ]);

    if (message.toLowerCase().includes("itemize") && mode !== "Expert") {
      toast({
        title: "Try Expert Mode?",
        description: "You’re using technical terms. Switch to Expert for power tools.",
      });
    }
  };

  return (
    <>
      <Helmet>
        <title>Tax Fluent Chat – Adaptive Conversational Tax Filing</title>
        <meta name="description" content="Adaptive AI chat for tax filing with explainability, dynamic UI, and accessibility-focused modes." />
        <link rel="canonical" href={typeof window !== 'undefined' ? window.location.href : '/'} />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              name: "Tax Fluent Chat",
              applicationCategory: "FinanceApplication",
              operatingSystem: "Web",
              description: "Adaptive AI chat for tax filing with explainability, dynamic UI, and accessibility-focused modes.",
              url: typeof window !== 'undefined' ? window.location.href : '/'
            }),
          }}
        />
      </Helmet>

      <main className="min-h-screen bg-background">
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <h1 className="text-xl md:text-2xl font-semibold">Tax Fluent Chat</h1>
            <div className="flex items-center gap-4">
              <TransparencyIndicator />
              <ModeSwitcher mode={mode} onChange={setMode} />
            </div>
          </div>
        </header>

        <DynamicLayoutContainer>
          <section className="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Conversation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[50vh] md:h-[60vh] overflow-hidden flex flex-col">
                  <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                    {messages.map((m) => (
                      <MessageBubble key={m.id} message={m} onExplain={requestExplain} />
                    ))}
                  </div>
                  <Separator className="my-3" />
                  <InputBar onSend={onSend} suggestions={suggestions} mode={mode} />
                </div>
              </CardContent>
            </Card>

            <aside className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Inputs</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <IntelligentField id="income" label="Annual Income" type="number" required help="Your total income before deductions." />
                  <IntelligentField id="dependents" label="Dependents" type="number" required help="Number of qualifying dependents." />
                  <IntelligentField id="state" label="State" placeholder="e.g., CA" help="State of residence for state taxes." />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Tips & Transparency</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground space-y-2">
                  <p>We highlight the rules and thresholds used for each outcome.</p>
                  <p>Ask for an explanation any time using the Explain button.</p>
                </CardContent>
              </Card>
            </aside>
          </section>
        </DynamicLayoutContainer>

        <ExplanationPanel open={explanationOpen} onOpenChange={setExplanationOpen} content={explanationContent} />
      </main>
    </>
  );
};

export default Index;
