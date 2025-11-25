<template>
  <div class="min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary/20">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 transition-all duration-300" :class="{ 'bg-background/80 backdrop-blur-md border-b border-white/10': isScrolled }">
      <div class="container mx-auto px-6 h-20 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <span class="text-white font-bold text-xl">T</span>
          </div>
          <span class="font-heading font-bold text-xl tracking-tight">TaxFluent</span>
        </div>
        
        <div class="hidden md:flex items-center gap-8">
          <a href="#features" class="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Features</a>
          <a href="#how-it-works" class="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">How it Works</a>
          <a href="#pricing" class="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Pricing</a>
        </div>

        <div class="flex items-center gap-4">
          <Button variant="ghost" class="hidden sm:flex">Sign In</Button>
          <Button variant="glow" @click="$router.push('/dashboard')">Get Started</Button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
      <!-- Background Elements -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl pointer-events-none">
        <div class="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-[100px] animate-pulse-glow"></div>
        <div class="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-[100px] animate-pulse-glow" style="animation-delay: 1s"></div>
      </div>

      <div class="container mx-auto px-6 relative z-10">
        <div class="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
          <div class="flex-1 text-center lg:text-left">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 mb-6">
              <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
              <span class="text-xs font-medium text-primary">AI-Powered Tax Filing for AY 2025-26</span>
            </div>
            
            <h1 class="text-5xl lg:text-7xl font-heading font-bold leading-[1.1] mb-6">
              Tax Filing, <br />
              <span class="text-gradient">Reimagined.</span>
            </h1>
            
            <p class="text-lg text-muted-foreground mb-8 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              Experience Financial Zen. Our multi-agent AI handles the complexity of Indian tax laws while you watch your finances flow in real-time.
            </p>
            
            <div class="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
              <Button size="lg" variant="glow" class="w-full sm:w-auto h-12 px-8 text-base" @click="$router.push('/dashboard')">
                Start Filing Free
              </Button>
              <Button size="lg" variant="outline" class="w-full sm:w-auto h-12 px-8 text-base backdrop-blur-sm">
                Watch Demo
              </Button>
            </div>

            <div class="mt-10 flex items-center justify-center lg:justify-start gap-6 text-sm text-muted-foreground">
              <div class="flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-accent" />
                <span>ITR-1 & ITR-4</span>
              </div>
              <div class="flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-accent" />
                <span>Max Refund Guarantee</span>
              </div>
              <div class="flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-accent" />
                <span>Bank-Grade Security</span>
              </div>
            </div>
          </div>

          <div class="flex-1 w-full max-w-lg lg:max-w-none perspective-1000">
            <div class="relative transform rotate-y-12 rotate-x-6 transition-transform duration-500 hover:rotate-0">
              <Card class="glass-panel p-6 relative z-20 overflow-hidden">
                <!-- Mock UI -->
                <div class="flex items-center justify-between mb-6">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                      <Bot class="w-6 h-6" />
                    </div>
                    <div>
                      <div class="font-medium">Tax Expert Agent</div>
                      <div class="text-xs text-muted-foreground">Analyzing deductions...</div>
                    </div>
                  </div>
                  <div class="px-2 py-1 rounded bg-green-500/10 text-green-500 text-xs font-medium">Active</div>
                </div>
                
                <div class="space-y-4">
                  <div class="p-4 rounded-lg bg-muted/50 border border-white/5">
                    <div class="flex justify-between text-sm mb-2">
                      <span class="text-muted-foreground">Potential Refund</span>
                      <span class="font-bold text-green-500">+ ₹24,500</span>
                    </div>
                    <div class="h-2 bg-muted rounded-full overflow-hidden">
                      <div class="h-full bg-green-500 w-[75%]"></div>
                    </div>
                  </div>
                  
                  <div class="space-y-2">
                    <div class="flex gap-3 items-start p-3 rounded-lg hover:bg-white/5 transition-colors">
                      <div class="w-6 h-6 rounded bg-blue-500/10 flex items-center justify-center mt-0.5">
                        <FileText class="w-3 h-3 text-blue-500" />
                      </div>
                      <div class="text-sm">
                        <div class="font-medium">Form 16 Parsed</div>
                        <div class="text-xs text-muted-foreground">Gross Salary: ₹12,50,000</div>
                      </div>
                    </div>
                    <div class="flex gap-3 items-start p-3 rounded-lg hover:bg-white/5 transition-colors">
                      <div class="w-6 h-6 rounded bg-purple-500/10 flex items-center justify-center mt-0.5">
                        <Sparkles class="w-3 h-3 text-purple-500" />
                      </div>
                      <div class="text-sm">
                        <div class="font-medium">Optimization Found</div>
                        <div class="text-xs text-muted-foreground">Switching to New Regime saves ₹12k</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
              
              <!-- Floating Elements -->
              <Card class="absolute -right-10 top-20 p-4 glass-card w-48 animate-float z-30 hidden md:block">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                    <Check class="w-4 h-4 text-green-500" />
                  </div>
                  <div class="text-xs">
                    <div class="font-bold">Compliance Check</div>
                    <div class="text-muted-foreground">100% Verified</div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section id="features" class="py-20 bg-muted/30">
      <div class="container mx-auto px-6">
        <div class="text-center max-w-2xl mx-auto mb-16">
          <h2 class="text-3xl lg:text-4xl font-heading font-bold mb-4">Why Choose TaxFluent?</h2>
          <p class="text-muted-foreground">We combine the precision of code with the intuition of AI to deliver the most seamless filing experience ever.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <Card class="p-6 hover:-translate-y-2 transition-transform duration-300">
            <div class="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-6 text-primary">
              <BrainCircuit class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold mb-3">Multi-Agent Intelligence</h3>
            <p class="text-muted-foreground text-sm leading-relaxed">
              Seven specialized AI agents work in harmony to calculate, verify, and optimize your taxes, ensuring zero errors.
            </p>
          </Card>

          <Card class="p-6 hover:-translate-y-2 transition-transform duration-300">
            <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-6 text-accent">
              <Activity class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold mb-3">Live Tracking</h3>
            <p class="text-muted-foreground text-sm leading-relaxed">
              Watch the logic unfold in real-time. Our "Glass Box" engine shows you exactly how every rupee is calculated.
            </p>
          </Card>

          <Card class="p-6 hover:-translate-y-2 transition-transform duration-300">
            <div class="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6 text-purple-500">
              <ShieldCheck class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold mb-3">Privacy First</h3>
            <p class="text-muted-foreground text-sm leading-relaxed">
              Your financial data is encrypted and processed locally where possible. We use SMPC for secure benchmarking.
            </p>
          </Card>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-12 border-t border-white/10 bg-background">
      <div class="container mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded bg-primary flex items-center justify-center text-white text-xs font-bold">T</div>
            <span class="font-heading font-bold">TaxFluent</span>
          </div>
          <div class="text-sm text-muted-foreground">
            © 2025 TaxFluent AI. All rights reserved.
          </div>
          <div class="flex gap-6">
            <a href="#" class="text-muted-foreground hover:text-primary transition-colors"><Twitter class="w-5 h-5" /></a>
            <a href="#" class="text-muted-foreground hover:text-primary transition-colors"><Github class="w-5 h-5" /></a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import Button from '@/components-vue/ui/Button.vue';
import Card from '@/components-vue/ui/Card.vue';
import { 
  CheckCircle, 
  Bot, 
  FileText, 
  Sparkles, 
  Check, 
  BrainCircuit, 
  Activity, 
  ShieldCheck,
  Twitter,
  Github
} from 'lucide-vue-next';

const isScrolled = ref(false);

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20;
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.perspective-1000 {
  perspective: 1000px;
}
.rotate-y-12 {
  transform: rotateY(-12deg) rotateX(5deg);
}
</style>
